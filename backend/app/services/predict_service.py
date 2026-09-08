import hashlib
import json
import os
import re
import sys
import joblib
import numpy as np
import xgboost as xgb
from collections import Counter
from .. import db
from ..config import Config
from ..models import JobClean, SalaryPrediction
from ..services.resume_parser import ResumeParser
from ..utils.logger import get_logger

logger = get_logger(__name__)

class PredictService:
    """薪资预测服务（训练模型：CatBoost / 梯度提升 / Stacking）"""
    _cache = {}
    _scaler = None
    _feature_names = None

    @classmethod
    def resolve_model_key(cls, model_name):
        if not model_name:
            return 'gradient_boosting'
        key = Config.MODEL_ALIASES.get(str(model_name).strip(), str(model_name).strip())
        if key not in Config.MODEL_FILES:
            return 'gradient_boosting'
        return key

    @classmethod
    def list_models(cls):
        items = []
        for key, filename in Config.MODEL_FILES.items():
            path = os.path.join(Config.MODEL_PATH, filename)
            items.append({
                'key': key,
                'label': Config.MODEL_LABELS[key],
                'filename': filename,
                'available': os.path.exists(path),
                'default': key == 'gradient_boosting',
            })
        return items

    @classmethod
    def _load_feature_names(cls):
        if cls._feature_names is not None:
            return cls._feature_names
        path = os.path.join(Config.MODEL_PATH, 'feature_names.json')
        if os.path.exists(path):
            with open(path, encoding='utf-8') as f:
                cls._feature_names = json.load(f)
            return cls._feature_names
        return []

    @classmethod
    def _load_scaler(cls):
        if cls._scaler is not None:
            return cls._scaler
        path = os.path.join(Config.MODEL_PATH, 'robust_scaler.pkl')
        if not os.path.exists(path):
            return None
        cls._scaler = joblib.load(path)
        return cls._scaler

    @classmethod
    def load_model(cls, model_key='gradient_boosting'):
        model_key = cls.resolve_model_key(model_key)
        if model_key in cls._cache:
            return cls._cache[model_key]

        filename = Config.MODEL_FILES[model_key]
        model_path = os.path.join(Config.MODEL_PATH, filename)
        if not os.path.exists(model_path):
            logger.error('模型文件不存在: %s', model_path)
            return None

        ml_root = os.path.abspath(os.path.join(Config.PROJECT_DIR, 'ml'))
        if ml_root not in sys.path:
            sys.path.insert(0, ml_root)

        data = joblib.load(model_path)
        if isinstance(data, dict) and 'model' in data:
            model = data['model']
            feature_names = data.get('feature_names') or cls._load_feature_names()
        else:
            model = data
            feature_names = cls._load_feature_names()

        bundle = {
            'model': model,
            'feature_names': feature_names,
            'model_name': Config.MODEL_LABELS.get(model_key, model_key),
            'key': model_key,
            'metrics': data.get('metrics') if isinstance(data, dict) else None,
        }
        cls._cache[model_key] = bundle
        return bundle

    @staticmethod
    def encode_education(education):
        if education is None or (isinstance(education, float) and np.isnan(education)):
            return 3
        if isinstance(education, (int, float)) and not isinstance(education, bool):
            val = int(education)
            return val if 1 <= val <= 6 else 3
        text = str(education).strip()
        if not text or '不限' in text:
            return 3
        if '高中/中专' in text or '中专/高中' in text:
            return 2
        for key, val in Config.EDU_LEVEL_MAP.items():
            if key in text:
                return val
        return 3

    @staticmethod
    def encode_experience_level(experience):
        """工作经验 """
        if experience is None or (isinstance(experience, float) and np.isnan(experience)):
            return 0
        # 已是等级整数且无「年」字样
        if isinstance(experience, (int, float)) and not isinstance(experience, bool):
            # 若数值像年限（>5 的小数或大数），按年限分桶
            exp_val = float(experience)
            if exp_val <= 0:
                return 0
            if exp_val <= 1:
                return 1
            if exp_val <= 3:
                return 2
            if exp_val <= 5:
                return 3
            if exp_val <= 10:
                return 4
            return 5

        exp = str(experience).lower()
        if '在校生' in exp or '应届生' in exp:
            return 0
        if '无需' in exp or '不限' in exp:
            return 0

        nums = re.findall(r'\d+\.?\d*', exp)
        if nums:
            if len(nums) >= 2:
                exp_val = (float(nums[0]) + float(nums[1])) / 2
            else:
                exp_val = float(nums[0])
            if exp_val <= 1:
                return 1
            if exp_val <= 3:
                return 2
            if exp_val <= 5:
                return 3
            if exp_val <= 10:
                return 4
            return 5
        return 0

    @staticmethod
    def encode_experience_years(experience):
        if experience is None:
            return 0.0
        if isinstance(experience, (int, float)) and not isinstance(experience, bool):
            return float(experience)
        exp = str(experience)
        nums = re.findall(r'\d+\.?\d*', exp)
        if not nums:
            return 0.0
        if len(nums) >= 2:
            return (float(nums[0]) + float(nums[1])) / 2
        return float(nums[0])

    @staticmethod
    def encode_city_level(city):
        if not city:
            return 3
        text = str(city).strip()
        for sep in ['·', '-', '（', '(']:
            if sep in text:
                text = text.split(sep)[0]
                break
        return float(Config.CITY_TIER_MAP.get(text, 3))

    @staticmethod
    def encode_city_encoded(city):
        text = str(city or '未知').strip() or '未知'
        digest = hashlib.md5(text.encode('utf-8')).hexdigest()
        return float(int(digest[:8], 16) % 500)

    @staticmethod
    def encode_company_scale(company_size):
        if not company_size:
            return 0
        text = str(company_size).strip()
        if text in Config.SCALE_MAP:
            return Config.SCALE_MAP[text]
        for key, val in Config.SCALE_MAP.items():
            if key in text or text in key:
                return val
        nums = re.findall(r'\d+', text)
        if nums:
            n = int(nums[0])
            if n < 50:
                return 1
            if n < 100:
                return 2
            if n < 500:
                return 3
            if n < 1000:
                return 4
            if n < 5000:
                return 5
            return 6
        return 0

    @classmethod
    def _normalize_skills(cls, skills, job_title=''):
        result = []
        if isinstance(skills, list):
            result.extend([str(s) for s in skills if s])
        elif isinstance(skills, str) and skills.strip():
            result.extend([s.strip() for s in skills.split(',') if s.strip()])
        if job_title:
            result.append(str(job_title))
        # 去重保序
        seen = set()
        out = []
        for s in result:
            key = s.lower()
            if key not in seen:
                seen.add(key)
                out.append(s)
        return out

    @classmethod
    def _skill_text_blob(cls, skills):
        return ' '.join(str(s).lower() for s in skills)

    @classmethod
    def build_feature_dict(
        cls,
        skills=None,
        experience=None,
        experience_years=None,
        education=None,
        education_level=None,
        city='',
        company_size='',
        job_title='',
        description='',
    ):
        # 按训练特征名构造单样本原始特征值
        skills = cls._normalize_skills(skills, job_title)
        blob = cls._skill_text_blob(skills)
        title_blob = f"{job_title or ''} {description or ''}".lower()
        full_blob = f"{blob} {title_blob}"

        if education is not None:
            edu = cls.encode_education(education)
        elif education_level is not None:
            try:
                edu = int(float(education_level))
                if edu < 1 or edu > 6:
                    edu = cls.encode_education(education_level)
            except (TypeError, ValueError):
                edu = cls.encode_education(education_level)
        else:
            edu = 3
        if experience_years is not None and experience is None:
            exp_years = float(experience_years)
            exp_level = cls.encode_experience_level(exp_years)
        else:
            exp_level = cls.encode_experience_level(experience if experience is not None else experience_years)
            exp_years = cls.encode_experience_years(
                experience if experience is not None else (experience_years if experience_years is not None else 0)
            )

        city_level = cls.encode_city_level(city)
        city_encoded = cls.encode_city_encoded(city)
        scale_level = cls.encode_company_scale(company_size)
        skill_count = float(len(skills))

        feat = {
            'experience_level': float(exp_level),
            'experience_years': float(exp_years),
            'experience_level_squared': float(exp_level) ** 2,
            'education_level': float(edu),
            'city_level': float(city_level),
            'city_encoded': float(city_encoded),
            'company_scale_level': float(scale_level),
            'skill_count': skill_count,
            'skill_richness': skill_count / 10.0,
            'exp_edu_interaction': float(exp_years) * float(edu),
            'exp_edu_ratio': float(exp_years) / (float(edu) + 1.0),
            # 在线预测无原文薪资区间，取常见比例中性值
            'salary_range_ratio': 0.45,
        }

        for ctype in Config.COMPANY_TYPES:
            feat[f'company_type_{ctype}'] = 1.0 if ctype in (description or '') else 0.0

        for industry in Config.INDUSTRIES:
            hit = industry in full_blob or industry in (description or '')
            feat[f'industry_{industry}'] = 1.0 if hit else 0.0
        # 技术岗默认偏互联网
        if feat.get('industry_互联网', 0) == 0 and any(
            k in full_blob for k in ('python', 'java', '前端', '后端', '算法', '开发', '数据')
        ):
            feat['industry_互联网'] = 1.0

        for category, keywords in Config.SKILL_CATEGORIES.items():
            feat[f'skill_category_{category}'] = float(
                sum(1 for kw in keywords if kw in full_blob)
            )

        for combo in Config.SKILL_COMBOS:
            name = '_'.join(combo)
            feat[f'skill_combo_{name}'] = (
                1.0 if all(any(kw in full_blob for kw in [c]) for c in combo) else 0.0
            )

        # 训练时留下的具体 skill_* 列：按名称精确/词边界匹配（原为子串匹配，会误报 java↔javascript）
        feature_names = cls._load_feature_names()
        # 技能名标准化 token 集合（去掉空格/下划线/点/连字符），用于与特征名 token 精确对齐
        norm_skill_tokens = {
            str(s).lower().replace(' ', '').replace('_', '').replace('.', '').replace('-', '')
            for s in skills
        }
        for name in feature_names:
            if not name.startswith('skill_') or name.startswith('skill_category_') or name.startswith('skill_combo_'):
                continue
            if name in ('skill_count', 'skill_richness'):
                continue
            token = name[len('skill_'):].replace('_', '').lower()
            if not token:
                feat[name] = 0.0
                continue
            # 1) 技能列表精确匹配（如 skill_node_js → 'nodejs' 对齐 'Node.js'）
            hit = token in norm_skill_tokens
            # 2) 岗位/描述文本词边界匹配（防止 javascript 里的 java、google 里的 go 误命中）
            if not hit:
                pat = re.compile(r'(?<![a-z0-9])' + re.escape(token) + r'(?![a-z0-9])')
                hit = bool(pat.search(full_blob))
            feat[name] = 1.0 if hit else 0.0

        # 文本 SVD 特征在线无法复现，置 0（RobustScaler 后接近训练集中心）
        for name in feature_names:
            if name.startswith('text_feature_'):
                feat[name] = 0.0

        return feat, {
            'skills': skills,
            'experience_level': exp_level,
            'experience_years': exp_years,
            'education_level': edu,
            'city_level': city_level,
            'company_scale_level': scale_level,
        }

    @classmethod
    def _vectorize(cls, feature_dict, feature_names):
        if not feature_names:
            feature_names = sorted(feature_dict.keys())
        return np.array([[float(feature_dict.get(name, 0.0)) for name in feature_names]], dtype=np.float64)

    @classmethod
    def _predict_raw(cls, bundle, X):
        model = bundle['model']
        if isinstance(model, xgb.Booster):
            names = bundle.get('feature_names')
            dmatrix = xgb.DMatrix(X, feature_names=list(names) if names and len(names) == X.shape[1] else None)
            pred = model.predict(dmatrix)
        else:
            pred = model.predict(X)
        return float(np.asarray(pred).ravel()[0])

    @classmethod
    def predict_from_resume(cls, filepath, resume_name=None, city=None, model_name=None, company_size=None):
        logger.info(
            '简历预测开始 file=%s city=%s model=%s',
            resume_name or filepath, city, model_name,
        )
        parsed = ResumeParser.parse_file(filepath)
        result = cls.predict(
            skills=parsed.get('skills') or [],
            experience_years=parsed.get('experience_years', 0),
            education_level=parsed.get('education_level', 3),
            resume_name=resume_name or os.path.basename(filepath),
            city=city or parsed.get('city') or '',
            model_name=model_name,
            company_size=company_size or parsed.get('company_size') or '',
            job_title=parsed.get('job_title') or '',
        )
        result['extracted'] = {
            'skills': parsed.get('skills', []),
            'experience_years': parsed.get('experience_years', 0),
            'education_level': parsed.get('education_level', 3),
            'city': parsed.get('city') or city or '',
            'job_title': parsed.get('job_title') or '',
            'company_size': parsed.get('company_size') or company_size or '',
        }
        return result

    @classmethod
    def predict(
        cls,
        skills=None,
        experience_years=0,
        education_level=3,
        resume_name=None,
        city=None,
        model_name=None,
        company_size=None,
        job_title=None,
        experience=None,
        education=None,
        description='',
        platform='zhaopin',
    ):
        model_key = cls.resolve_model_key(model_name)
        logger.info(
            '薪资预测开始 model=%s city=%s job=%s company_size=%s',
            model_key, city, job_title, company_size,
        )
        bundle = cls.load_model(model_key)
        if bundle is None:
            raise FileNotFoundError(
                f'未找到模型文件，请确认已训练并保存到 {Config.MODEL_PATH}'
            )

        feature_names = bundle.get('feature_names') or cls._load_feature_names()
        feat_dict, encoded = cls.build_feature_dict(
            skills=skills,
            experience=experience,
            experience_years=experience_years,
            education=education,
            education_level=education_level,
            city=city or '',
            company_size=company_size or '',
            job_title=job_title or '',
            description=description or '',
        )
        X = cls._vectorize(feat_dict, feature_names)
        scaler = cls._load_scaler()
        if scaler is not None:
            try:
                X = scaler.transform(X)
            except Exception as e:
                logger.warning('RobustScaler 变换失败，使用原始特征: %s', e)

        predicted_yuan = cls._predict_raw(bundle, X)
        predicted_yuan = max(float(predicted_yuan), 1000.0)

        # 模型输出为月薪平均值（元），前端/历史以 K（千元）展示
        predicted_avg_k = predicted_yuan / 1000.0
        margin = predicted_avg_k * 0.15
        predicted_min = max(predicted_avg_k - margin, 1.0)
        predicted_max = predicted_avg_k + margin
        skills_list = encoded['skills'] or (skills if isinstance(skills, list) else [])
        matched_jobs = cls._count_matched_jobs(skills_list, encoded['experience_years'])
        model_label = Config.MODEL_LABELS.get(model_key, model_key)
        display_name = resume_name or job_title or '手动输入'
        display_name = f'{display_name} [{model_label}]'

        # 用训练指标粗略给置信度
        metrics = bundle.get('metrics') or {}
        r2 = float(metrics.get('r2') or 0)
        confidence = float(min(0.95, max(0.7, 0.55 + r2 * 0.4))) if r2 else 0.85

        record = SalaryPrediction(
            resume_name=display_name,
            predicted_salary_min=round(predicted_min, 1),
            predicted_salary_max=round(predicted_max, 1),
            predicted_salary_avg=round(predicted_avg_k, 1),
            matched_jobs=matched_jobs,
            skills_extracted=json.dumps(skills_list, ensure_ascii=False),
            experience_years=int(round(encoded['experience_years'])),
            education_level=int(encoded['education_level']),
            confidence=confidence,
        )
        db.session.add(record)
        db.session.commit()

        data = record.to_dict()
        data['model'] = model_key
        data['model_name'] = model_label
        data['predicted_salary_yuan'] = round(predicted_yuan, 0)
        data['target_definition'] = '(salary_min + salary_max) / 2'
        logger.info(
            '薪资预测完成 model=%s avg_k=%s yuan=%s record_id=%s',
            model_key, data.get('predicted_salary_avg'), predicted_yuan, data.get('id'),
        )
        return data

    @classmethod
    def _count_matched_jobs(cls, skills, experience_years):
        if not skills:
            return 0
        count = 0
        jobs = JobClean.query.limit(5000).all()
        for job in jobs:
            try:
                job_skills = json.loads(job.skills) if job.skills else []
            except (json.JSONDecodeError, TypeError):
                job_skills = []
            overlap = set(str(s).lower() for s in skills) & set(str(s).lower() for s in job_skills)
            if overlap and (
                job.experience_years is None
                or abs((job.experience_years or 0) - experience_years) <= 3
            ):
                count += 1
        return count

    @classmethod
    def get_history(cls, page=1, per_page=20):
        pagination = SalaryPrediction.query.order_by(
            SalaryPrediction.created_at.desc()
        ).paginate(page=page, per_page=per_page, error_out=False)
        return {
            'items': [r.to_dict() for r in pagination.items],
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
        }

    @classmethod
    def analyze_skill_gap(cls, skills=None, job_title='', city='', top_n=10):
        """
        技能缺口分析：对比简历技能 vs 目标岗位 JD 技能。
        从清洗库中筛选与目标岗位相关（岗位关键词 / 城市 / 技能交集）的职位，
        统计其 JD 高频技能，去除简历已有技能与福利噪声后，返回「还差哪些技能」建议。
        """
        from ..services.data_cleaner import _is_benefit_tag, normalize_skill_name, expand_user_skills
        #归一化
        raw_skills = [str(s) for s in (skills or []) if str(s).strip()]
        raw_skills = [normalize_skill_name(s) for s in raw_skills if normalize_skill_name(s)]
        user_skill_set = set(str(s).strip().lower() for s in raw_skills)
        # 技能包含关系扩展：已有 MySQL 自动视为已有 SQL 等
        user_skill_set = expand_user_skills(raw_skills)

        # 1. 筛选相关岗位（优先按岗位关键词 + 城市）
        query = JobClean.query.filter(JobClean.skills.isnot(None))
        if city:
            query = query.filter(JobClean.city.like(f'%{city}%'))
        if job_title:
            query = query.filter(JobClean.title.like(f'%{job_title}%'))
        jobs = query.limit(3000).all()

        # 2. 未指定岗位关键词时，退化为「技能交集」匹配
        if not job_title:
            filtered = []
            for j in jobs:
                try:
                    jskills = [str(s).lower() for s in json.loads(j.skills)]
                except (json.JSONDecodeError, TypeError):
                    continue
                if user_skill_set & set(jskills):
                    filtered.append(j)
            jobs = filtered

        # 3. 统计相关岗位的技能频次（统一标准化后计数）
        skill_counter = Counter()
        for j in jobs:
            try:
                jskills = json.loads(j.skills)
            except (json.JSONDecodeError, TypeError):
                continue
            for s in jskills:
                std = normalize_skill_name(str(s))
                if std:
                    skill_counter[std] += 1

        total = max(len(jobs), 1)

        # 新增：校验用户输入的技能是否在匹配岗位中出现
        all_skill_keys = {str(k).strip().lower() for k in skill_counter}
        user_skill_hit = any(
            str(s).strip().lower() in all_skill_keys
            for s in raw_skills
        )
        if not user_skill_hit and raw_skills:
            return {
                'skill_gaps': [],
                'total_matched_jobs': len(jobs),
                'user_skills': raw_skills,
                'filter': {'job_title': job_title, 'city': city},
                'warning': '未搜索到有岗位包含该技能，请仔细确认后再输入',
            }

        gaps = []
        for name, cnt in skill_counter.most_common(300):
            key = str(name).strip().lower()
            if not key or len(key) < 2:
                continue
            if key in user_skill_set:          # 已有技能不重复建议
                continue
            if _is_benefit_tag(name):           # 过滤福利/经验/非技能噪声
                continue
            gaps.append({
                'name': str(name),
                'count': cnt,
                'ratio': round(cnt / total, 4),  # 出现岗位占比
            })
            if len(gaps) >= top_n:
                break

        return {
            'skill_gaps': gaps,
            'total_matched_jobs': len(jobs),
            'user_skills': raw_skills,
            'filter': {'job_title': job_title, 'city': city},
        }
