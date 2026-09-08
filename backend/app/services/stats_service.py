"""统计分析服务：可视化各子模块统一使用「月薪 K」口径（年薪按 ÷12 折算）。"""
import json
from collections import Counter, defaultdict
from datetime import date

from flask import g, has_request_context
from sqlalchemy import func  # SQL 聚合函数（count/avg/max 等）

from .. import db
from ..models import JobRaw, JobClean
from ..services.geo_data import CITY_COORDS, CITY_TO_PROVINCE, normalize_city, to_geo_province  # 地理映射
from .data_cleaner import parse_salary
from ..utils.cache import cached  # 跨请求 TTL 内存缓存
from ..utils.logger import get_logger

logger = get_logger(__name__)


# 合理月薪上限（K）；超过视为异常，不参与可视化统计
MAX_REASONABLE_MONTHLY_K = 200


class StatsService:  # 统计分析服务类
    """统计分析服务"""

    # ── 月薪规范化（可视化统一入口）──────────────────────────────
    @staticmethod
    def _resolve_monthly_salary(salary_raw, salary_min=None, salary_max=None, salary_avg=None):
        """
        统一折算为月薪（K）
        优先按原始 salary_raw 重解析（如 60-90万/年 → ÷12）；
        否则回退清洗表数值，并对残留的异常高值再 ÷12。
        返回 (min_k, max_k, avg_k)，无法解析则 (None, None, None)。
        """
        if salary_raw:  # 优先用原始文本，确保年薪口径正确
            mn, mx, avg = parse_salary(salary_raw)
            if avg is not None or mn is not None or mx is not None:
                if avg is None:
                    if mn is not None and mx is not None:
                        avg = (mn + mx) / 2.0
                    else:
                        avg = mn if mn is not None else mx
                return mn, mx, avg

        mn = float(salary_min) if salary_min is not None else None
        mx = float(salary_max) if salary_max is not None else None
        avg = float(salary_avg) if salary_avg is not None else None
        ref = next((v for v in (mx, avg, mn) if v is not None), None)
        # 清洗表若仍残留「年薪当月薪」的异常高值，按 12 个月折算
        if ref is not None and ref >= MAX_REASONABLE_MONTHLY_K:
            mn = None if mn is None else round(mn / 12.0, 2)
            mx = None if mx is None else round(mx / 12.0, 2)
            avg = None if avg is None else round(avg / 12.0, 2)
        return mn, mx, avg

    @staticmethod
    def _salary_job_rows():
        """
        加载可视化用岗位薪资行：已统一为月薪 K。
        关联 JobRaw.salary_raw，年薪在解析阶段完成 ÷12。
        """
        if has_request_context() and hasattr(g, '_stats_salary_rows'):
            return g._stats_salary_rows
        rows = (
            db.session.query(
                JobClean.id,
                JobClean.platform,
                JobClean.city,
                JobClean.title,
                JobClean.company,
                JobClean.experience_years,
                JobClean.clean_time,
                JobClean.raw_id,
                JobClean.salary_min,
                JobClean.salary_max,
                JobClean.salary_avg,
                JobRaw.salary_raw,
            )
            .outerjoin(JobRaw, JobClean.raw_id == JobRaw.id)
            .all()
        )
        result = []
        for r in rows:
            mn, mx, avg = StatsService._resolve_monthly_salary(
                r.salary_raw, r.salary_min, r.salary_max, r.salary_avg,
            )
            if avg is None and mn is None and mx is None:
                continue
            monthly = mx if mx is not None else (avg if avg is not None else mn)
            if monthly is None or monthly <= 0:
                continue
            # 折算后仍超出合理月薪上限则丢弃，避免极端脏数据污染图表
            if monthly >= MAX_REASONABLE_MONTHLY_K:
                continue
            result.append({
                'id': r.id,
                'platform': r.platform,
                'city': r.city,
                'title': r.title,
                'company': r.company,
                'experience_years': r.experience_years,
                'clean_time': r.clean_time,
                'raw_id': r.raw_id,
                'salary_min': mn,
                'salary_max': mx,
                'salary_avg': float(avg if avg is not None else monthly),
                'monthly': float(monthly),
            })

        if has_request_context():
            g._stats_salary_rows = result
        return result

    @staticmethod
    def _valid_monthly(job):
        """判断薪资行是否可用于统计。"""
        m = job.get('monthly')
        return m is not None and 0 < m < MAX_REASONABLE_MONTHLY_K

    # ── 基础总览 / 分布 ──────────────────────────────────────────
    @staticmethod
    def get_overview():
        """获取数据总览：总量、平均薪资（月薪 K）、城市数与平台分布"""
        logger.info('查询数据总览')
        raw_total = JobRaw.query.count()
        clean_total = JobClean.query.count()
        platform_stats = db.session.query(  # 按平台分组统计岗位数（原始表，覆盖全部平台）
            JobRaw.platform,
            func.count(JobRaw.id),
        ).filter(
            JobRaw.platform.isnot(None),
            JobRaw.platform != '',
        ).group_by(JobRaw.platform).all()

        jobs = StatsService._salary_job_rows()
        avgs = [j['salary_avg'] for j in jobs if StatsService._valid_monthly(j)]
        avg_salary = (sum(avgs) / len(avgs)) if avgs else 0

        city_count = db.session.query(
            func.count(func.distinct(JobClean.city))
        ).scalar()

        result = {
            'raw_total': raw_total,
            'clean_total': clean_total,
            'avg_salary': round(float(avg_salary), 1) if avg_salary else 0,
            'city_count': city_count or 0,
            'platform_stats': {p: c for p, c in platform_stats},
        }
        logger.info(
            '数据总览 raw=%s clean=%s avg_salary=%s cities=%s',
            result['raw_total'], result['clean_total'],
            result['avg_salary'], result['city_count'],
        )
        return result

    @staticmethod
    def get_platform_distribution():
        """统计各招聘平台岗位数量（以原始表为准，覆盖库中全部平台）。"""
        results = db.session.query(
            JobRaw.platform,
            func.count(JobRaw.id),
        ).filter(
            JobRaw.platform.isnot(None),
            JobRaw.platform != '',
        ).group_by(JobRaw.platform).order_by(
            func.count(JobRaw.id).desc()
        ).all()
        return [{'name': p, 'value': c} for p, c in results]

    @staticmethod
    def _platform_salary_from_raw(platform, sample_limit=5000):
        """从原始表抽样解析月薪，用于清洗表缺失该平台时的可视化补齐。"""
        rows = (
            JobRaw.query.filter_by(platform=platform)
            .with_entities(JobRaw.salary_raw, JobRaw.salary_min, JobRaw.salary_max)
            .limit(sample_limit)
            .all()
        )
        avgs, mins, maxs = [], [], []
        for salary_raw, smin, smax in rows:
            mn, mx, avg = StatsService._resolve_monthly_salary(
                salary_raw, smin, smax, None,
            )
            monthly = mx if mx is not None else (avg if avg is not None else mn)
            if monthly is None or monthly <= 0 or monthly >= MAX_REASONABLE_MONTHLY_K:
                continue
            if avg is not None and 0 < avg < MAX_REASONABLE_MONTHLY_K:
                avgs.append(float(avg))
            else:
                avgs.append(float(monthly))
            if mn is not None and 0 < mn < MAX_REASONABLE_MONTHLY_K:
                mins.append(float(mn))
            if mx is not None and 0 < mx < MAX_REASONABLE_MONTHLY_K:
                maxs.append(float(mx))
        if not avgs:
            return None
        return {
            'sum': sum(avgs),
            'count': len(avgs),
            'mins': mins,
            'maxs': maxs,
        }

    @staticmethod
    def get_salary_distribution():
        """按月薪区间统计岗位数量分布（年薪已折算为月薪）"""
        ranges = [
            ('0-10K', 0, 10),
            ('10-15K', 10, 15),
            ('15-20K', 15, 20),
            ('20-30K', 20, 30),
            ('30-50K', 30, 50),
            ('50K+', 50, 999),
        ]
        jobs = [j for j in StatsService._salary_job_rows() if StatsService._valid_monthly(j)]
        data = []
        for label, low, high in ranges:
            count = sum(1 for j in jobs if low <= j['salary_avg'] < high)
            data.append({'name': label, 'value': count})
        return data

    @staticmethod
    def get_city_ranking(limit=10):
        """获取岗位数量与平均月薪的城市排行"""
        jobs = StatsService._salary_job_rows()
        city_stats = defaultdict(lambda: {'count': 0, 'salary_sum': 0.0, 'salary_n': 0})

        # 岗位数仍以清洗表全量计，薪资用规范化月薪
        city_counts = db.session.query(
            JobClean.city, func.count(JobClean.id),
        ).filter(
            JobClean.city.isnot(None), JobClean.city != '',
        ).group_by(JobClean.city).all()
        for city, cnt in city_counts:
            city_stats[city]['count'] = cnt

        for j in jobs:
            if not j.get('city') or not StatsService._valid_monthly(j):
                continue
            city_stats[j['city']]['salary_sum'] += j['salary_avg']
            city_stats[j['city']]['salary_n'] += 1

        ranked = sorted(city_stats.items(), key=lambda x: x[1]['count'], reverse=True)[:limit]
        return [{
            'city': city,
            'count': st['count'],
            'avg_salary': round(st['salary_sum'] / st['salary_n'], 1) if st['salary_n'] else 0,
        } for city, st in ranked]

    @staticmethod
    def get_skill_ranking(limit=20):
        """统计热门技能出现频次排行"""
        jobs = JobClean.query.filter(JobClean.skills.isnot(None)).all()
        skill_counter = Counter()
        for job in jobs:
            try:
                skills = json.loads(job.skills)
                skill_counter.update(skills)
            except (json.JSONDecodeError, TypeError):
                continue

        top_skills = skill_counter.most_common(limit)
        return [{'name': s, 'value': c} for s, c in top_skills]

    @staticmethod
    def get_skill_city_salary_heatmap(skill_limit=15, city_limit=15):
        """
        技能-城市-薪资三维交叉分析（热力图数据）。
        对 (技能 × 城市) 聚合平均月薪与岗位数，返回 ECharts heatmap 可直接使用的矩阵。
        """
        rows = (
            db.session.query(
                JobClean.id,
                JobClean.city,
                JobClean.skills,
                JobClean.salary_min,
                JobClean.salary_max,
                JobClean.salary_avg,
                JobRaw.salary_raw,
            )
            .outerjoin(JobRaw, JobClean.raw_id == JobRaw.id)
            .all()
        )

        skill_counter = Counter()
        city_counter = Counter()
        skill_city = defaultdict(lambda: {'sum': 0.0, 'n': 0})
        valid = 0

        for r in rows:
            mn, mx, avg = StatsService._resolve_monthly_salary(
                r.salary_raw, r.salary_min, r.salary_max, r.salary_avg,
            )
            monthly = mx if mx is not None else (avg if avg is not None else mn)
            if monthly is None or monthly <= 0 or monthly >= MAX_REASONABLE_MONTHLY_K:
                continue
            if not r.skills:
                continue
            try:
                skills = json.loads(r.skills)
            except (json.JSONDecodeError, TypeError):
                continue
            city = (r.city or '未知').strip() or '未知'
            city_counter[city] += 1
            for s in skills:
                name = str(s).strip()
                if not name or len(name) < 2:
                    continue
                # 统一技能名称大小写：长度<=3全大写（AI/SQL/C++），否则首字母大写
                name = name.upper() if len(name) <= 3 else name.capitalize()
                skill_counter[name] += 1
                skill_city[(name, city)]['sum'] += monthly
                skill_city[(name, city)]['n'] += 1
            valid += 1

        # 先选 Top N 城市，再只在这些城市里统计技能频次、选 Top N 技能
        # 避免技能和城市各自独立选 TopN 导致交集为空（选出来的技能在选中城市里 0 条数据）
        top_cities = [c for c, _ in city_counter.most_common(city_limit)]
        top_city_set = set(top_cities)
        city_skill_counter = Counter()
        for (sk, city), st in skill_city.items():
            if city in top_city_set and st['n'] > 0:
                city_skill_counter[sk] += st['n']
        top_skills = [s for s, _ in city_skill_counter.most_common(skill_limit)]
        # 反转：让频次高的技能显示在热力图最上方，避免最上面全是冷门技能的空行
        top_skills = top_skills[::-1]

        # 完整矩阵（含无数据格子，便于热力图整体展示）
        data = []
        for si, skill in enumerate(top_skills):
            for ci, city in enumerate(top_cities):
                st = skill_city.get((skill, city))
                if st and st['n'] > 0:
                    data.append([ci, si, round(st['sum'] / st['n'], 1), st['n']])
                else:
                    data.append([ci, si, None, 0])

        return {
            'skills': top_skills,
            'cities': top_cities,
            'data': data,
            'total_jobs': valid,
        }

    @staticmethod
    def get_education_distribution():
        """统计学历要求分布"""
        edu_labels = {0: '不限', 1: '高中/中专', 2: '大专', 3: '本科', 4: '硕士', 5: '博士'}
        results = db.session.query(
            JobClean.education_level,
            func.count(JobClean.id),
        ).group_by(JobClean.education_level).all()

        return [{
            'name': edu_labels.get(level, '未知'),
            'value': count,
        } for level, count in results]

    @staticmethod
    def get_experience_salary():
        """按工作年限统计平均月薪与岗位数"""
        jobs = [j for j in StatsService._salary_job_rows() if StatsService._valid_monthly(j)]
        buckets = defaultdict(lambda: {'sum': 0.0, 'count': 0})
        for j in jobs:
            exp = j.get('experience_years')
            if exp is None:
                continue
            buckets[exp]['sum'] += j['salary_avg']
            buckets[exp]['count'] += 1

        return [{
            'experience': exp,
            'avg_salary': round(st['sum'] / st['count'], 1) if st['count'] else 0,
            'count': st['count'],
        } for exp, st in sorted(buckets.items(), key=lambda x: x[0])]

    @staticmethod
    def get_platform_salary():
        """按平台统计月薪均值、极值与岗位数（覆盖原始表中全部平台）。"""
        # 清洗表已有平台
        jobs = [j for j in StatsService._salary_job_rows() if StatsService._valid_monthly(j)]
        buckets = defaultdict(lambda: {
            'sum': 0.0, 'count': 0, 'mins': [], 'maxs': [],
        })
        for j in jobs:
            p = j.get('platform') or 'unknown'
            buckets[p]['sum'] += j['salary_avg']
            buckets[p]['count'] += 1
            if j.get('salary_min') is not None:
                buckets[p]['mins'].append(j['salary_min'])
            if j.get('salary_max') is not None:
                buckets[p]['maxs'].append(j['salary_max'])

        # 原始表全部平台（保证可视化不因清洗不全而缺失）
        raw_platforms = [
            p for p, in db.session.query(JobRaw.platform).filter(
                JobRaw.platform.isnot(None), JobRaw.platform != '',
            ).distinct().all()
        ]
        preferred = ['qcwy', 'zhaopin', 'lagou', 'liepin', 'boss']
        ordered = [p for p in preferred if p in raw_platforms]
        ordered.extend(sorted(p for p in raw_platforms if p not in ordered))

        result = []
        for platform in ordered:
            st = buckets.get(platform)
            # 清洗样本过少时，用原始表解析补齐，避免只显示 1～2 个平台
            if not st or st['count'] < 5:
                raw_st = StatsService._platform_salary_from_raw(platform)
                if raw_st:
                    st = raw_st
            if not st or st['count'] <= 0:
                continue
            result.append({
                'platform': platform,
                'avg_salary': round(st['sum'] / st['count'], 1) if st['count'] else 0,
                'min_salary': float(min(st['mins'])) if st['mins'] else 0,
                'max_salary': float(max(st['maxs'])) if st['maxs'] else 0,
                'count': st['count'],
            })
        return result

    @staticmethod
    def get_trend_data():
        """获取近30日清洗数据量与平均月薪趋势"""
        jobs = StatsService._salary_job_rows()
        day_stats = defaultdict(lambda: {'count': 0, 'salary_sum': 0.0, 'salary_n': 0})

        # 数量按全量清洗时间；薪资用规范化月薪
        all_clean = db.session.query(
            func.date(JobClean.clean_time), func.count(JobClean.id),
        ).group_by(func.date(JobClean.clean_time)).all()
        for d, cnt in all_clean:
            if d is None:
                continue
            day_stats[str(d)]['count'] = cnt

        for j in jobs:
            ct = j.get('clean_time')
            if not ct or not StatsService._valid_monthly(j):
                continue
            d = ct.date() if hasattr(ct, 'date') else ct
            if isinstance(d, date):
                key = str(d)
            else:
                key = str(d)[:10]
            day_stats[key]['salary_sum'] += j['salary_avg']
            day_stats[key]['salary_n'] += 1

        ordered = sorted(day_stats.items(), key=lambda x: x[0])[-30:]
        return {
            'dates': [d for d, _ in ordered],
            'counts': [st['count'] for _, st in ordered],
            'salaries': [
                round(st['salary_sum'] / st['salary_n'], 1) if st['salary_n'] else 0
                for _, st in ordered
            ],
        }

    @staticmethod
    def get_map_data():
        """招聘岗位地区分布（省份聚合 + 城市坐标散点，均薪为月薪）"""
        jobs = StatsService._salary_job_rows()
        city_agg = defaultdict(lambda: {'count': 0, 'salary_sum': 0.0, 'salary_n': 0})

        city_counts = db.session.query(
            JobClean.city, func.count(JobClean.id),
        ).filter(
            JobClean.city.isnot(None), JobClean.city != '',
        ).group_by(JobClean.city).all()
        for city, cnt in city_counts:
            city_agg[city]['count'] = cnt

        for j in jobs:
            if not j.get('city') or not StatsService._valid_monthly(j):
                continue
            city_agg[j['city']]['salary_sum'] += j['salary_avg']
            city_agg[j['city']]['salary_n'] += 1

        province_counter = {}
        city_points = []

        for city_name, st in city_agg.items():
            city = normalize_city(city_name)
            count = st['count']
            avg_salary = round(st['salary_sum'] / st['salary_n'], 1) if st['salary_n'] else 0

            province = CITY_TO_PROVINCE.get(city, city)
            province_counter[province] = province_counter.get(province, 0) + count

            coords = CITY_COORDS.get(city)
            city_points.append({
                'city': city or city_name,
                'count': count,
                'avg_salary': avg_salary,
                'lng': coords[0] if coords else None,
                'lat': coords[1] if coords else None,
            })

        provinces = [
            {'name': to_geo_province(k), 'value': v}
            for k, v in province_counter.items()
        ]
        provinces.sort(key=lambda x: x['value'], reverse=True)

        return {
            'provinces': provinces,
            'cities': sorted(city_points, key=lambda x: x['count'], reverse=True),
        }

    # ── 大屏专用（全部月薪口径）────────────────────────────────
    @staticmethod
    def get_city_avg_salary_top(limit=10):
        """城市薪资 TOP：按城市内最高月薪降序排序"""
        jobs = [j for j in StatsService._salary_job_rows() if StatsService._valid_monthly(j)]
        city_agg = defaultdict(lambda: {
            'count': 0, 'salary_sum': 0.0, 'max_salary': 0.0,
        })
        for j in jobs:
            city = j.get('city')
            if not city:
                continue
            city_agg[city]['count'] += 1
            city_agg[city]['salary_sum'] += j['salary_avg']
            if j['monthly'] > city_agg[city]['max_salary']:
                city_agg[city]['max_salary'] = j['monthly']

        ranked = sorted(city_agg.items(), key=lambda x: x[1]['max_salary'], reverse=True)[:limit]
        return [{
            'city': city,
            'count': st['count'],
            'avg_salary': round(st['salary_sum'] / st['count'], 1) if st['count'] else 0,
            'avg_salary_yuan': int(round((st['salary_sum'] / st['count']) * 1000)) if st['count'] else 0,
            'max_salary': round(st['max_salary'], 1),
            'max_salary_yuan': int(round(st['max_salary'] * 1000)),
        } for city, st in ranked]

    @staticmethod
    def get_salary_range_analysis():
        """工资区间分析：按月薪划分区间"""
        ranges = [
            ('0-5k', 0, 5),
            ('5k-7k', 5, 7),
            ('7k-10k', 7, 10),
            ('10-20k', 10, 20),
            ('20k以上', 20, 9999),
        ]
        jobs = [j for j in StatsService._salary_job_rows() if StatsService._valid_monthly(j)]
        enriched = []
        for label, low, high in ranges:
            bucket = [j for j in jobs if low <= j['monthly'] < high]
            if not bucket:
                continue
            max_m = max(j['monthly'] for j in bucket)
            enriched.append({
                'name': label,
                'value': len(bucket),
                'max_salary': round(max_m, 1),
                'max_salary_yuan': int(round(max_m * 1000)),
            })
        enriched.sort(key=lambda x: x['max_salary'], reverse=True)
        return enriched

    @staticmethod
    def get_experience_salary_minmax():
        """按经验分段统计最高/最低月薪（大屏折线）"""
        buckets = [
            ('经验1年以下', 0, 1),
            ('经验1-3年', 1, 3),
            ('经验3-5年', 3, 5),
            ('经验5-10年', 5, 10),
            ('经验10年以上', 10, 99),
        ]
        jobs = [j for j in StatsService._salary_job_rows() if StatsService._valid_monthly(j)]
        data = []
        for label, low, high in buckets:
            bucket = [
                j for j in jobs
                if j.get('experience_years') is not None
                and low <= j['experience_years'] < high
            ]
            if not bucket:
                continue
            min_k = min(j['monthly'] for j in bucket)
            max_k = max(j['monthly'] for j in bucket)
            avg_k = sum(j['salary_avg'] for j in bucket) / len(bucket)
            data.append({
                'name': label,
                'min_salary': round(min_k, 1),
                'max_salary': round(max_k, 1),
                'avg_salary': round(avg_k, 1),
                'min_salary_yuan': int(round(min_k * 1000)),
                'max_salary_yuan': int(round(max_k * 1000)),
                'count': len(bucket),
            })
        return data

    @staticmethod
    def get_company_size_distribution():
        """公司人数分析：从原始描述解析规模，并按该规模组最高月薪排序"""
        import re

        size_buckets = [
            ('0-10', 0, 10),
            ('10-50', 10, 50),
            ('50-150', 50, 150),
            ('150-500', 150, 500),
            ('500-1000', 500, 1000),
            ('1000以上', 1000, 10 ** 9),
        ]
        counter = {name: 0 for name, _, _ in size_buckets}
        counter['未分类'] = 0
        salary_max_map = defaultdict(float)

        pattern = re.compile(
            r'(\d+)\s*[-~到至]\s*(\d+)\s*人|(\d+)\s*人\s*以上|少于\s*(\d+)\s*人|(\d+)\s*人'
        )

        def classify(n):
            for name, low, high in size_buckets:
                if low <= n < high:
                    return name
            return '未分类'

        # raw_id → 规范化月薪
        clean_salary = {}
        for j in StatsService._salary_job_rows():
            if j.get('raw_id') is None or not StatsService._valid_monthly(j):
                continue
            clean_salary[j['raw_id']] = j['monthly']

        raws = JobRaw.query.with_entities(
            JobRaw.id, JobRaw.description
        ).limit(12000).all()

        for raw_id, desc in raws:
            text = desc or ''
            m = pattern.search(text)
            bucket = '未分类'
            if m:
                if m.group(1) and m.group(2):
                    n = (int(m.group(1)) + int(m.group(2))) // 2
                elif m.group(3):
                    n = int(m.group(3))
                elif m.group(4):
                    n = max(int(m.group(4)) // 2, 1)
                else:
                    n = int(m.group(5))
                bucket = classify(n)
            counter[bucket] += 1
            sal = clean_salary.get(raw_id, 0)
            if sal > salary_max_map[bucket]:
                salary_max_map[bucket] = sal

        result = []
        for name, _, _ in size_buckets:
            if counter.get(name, 0) <= 0:
                continue
            max_k = salary_max_map.get(name, 0)
            result.append({
                'name': name,
                'value': counter[name],
                'max_salary': round(max_k, 1),
                'max_salary_yuan': int(round(max_k * 1000)),
            })
        if counter.get('未分类', 0) > 0:
            max_k = salary_max_map.get('未分类', 0)
            result.append({
                'name': '未分类',
                'value': counter['未分类'],
                'max_salary': round(max_k, 1),
                'max_salary_yuan': int(round(max_k * 1000)),
            })
        result.sort(key=lambda x: x['max_salary'], reverse=True)
        return result

    @staticmethod
    def get_salary_top_jobs(limit=10):
        """薪资 TOP：按最高月薪降序（年薪已折算）"""
        jobs = [j for j in StatsService._salary_job_rows() if StatsService._valid_monthly(j)]
        jobs.sort(key=lambda j: j['monthly'], reverse=True)
        rows = []
        for j in jobs[:limit]:
            monthly_k = j['monthly']
            rows.append({
                'id': j['id'],
                'title': j['title'],
                'company': j.get('company') or '-',
                'city': j.get('city') or '-',
                'salary_avg': j['salary_avg'],
                'salary_yuan': int(round(monthly_k * 1000)),
                'salary_min': j.get('salary_min'),
                'salary_max': j.get('salary_max'),
                'max_salary': round(monthly_k, 1),
            })
        return rows

    @staticmethod
    def get_highlight_job():
        """顶部高亮：月薪最高的岗位"""
        jobs = [j for j in StatsService._salary_job_rows() if StatsService._valid_monthly(j)]
        if not jobs:
            return {
                'max_salary': 0,
                'max_salary_yuan': 0,
                'title': '-',
                'city': '-',
                'company': '-',
            }
        job = max(jobs, key=lambda j: j['monthly'])
        monthly_k = job['monthly']
        return {
            'max_salary': round(monthly_k, 1),
            'max_salary_yuan': int(round(monthly_k * 1000)),
            'title': job.get('title') or '-',
            'city': job.get('city') or '-',
            'company': job.get('company') or '-',
        }

    @staticmethod
    def get_job_city_distribution():
        """各职位城市分布：按城市岗位数聚合，附带城市最高月薪"""
        jobs = StatsService._salary_job_rows()
        city_agg = defaultdict(lambda: {
            'count': 0, 'salary_sum': 0.0, 'salary_n': 0, 'max_salary': 0.0,
        })

        city_counts = db.session.query(
            JobClean.city, func.count(JobClean.id),
        ).filter(
            JobClean.city.isnot(None), JobClean.city != '',
        ).group_by(JobClean.city).all()
        for city, cnt in city_counts:
            city_agg[city]['count'] = cnt

        for j in jobs:
            if not j.get('city') or not StatsService._valid_monthly(j):
                continue
            city_agg[j['city']]['salary_sum'] += j['salary_avg']
            city_agg[j['city']]['salary_n'] += 1
            if j['monthly'] > city_agg[j['city']]['max_salary']:
                city_agg[j['city']]['max_salary'] = j['monthly']

        province_counter = {}
        city_points = []

        for city_name, st in city_agg.items():
            city = normalize_city(city_name)
            count = st['count']
            avg_salary = round(st['salary_sum'] / st['salary_n'], 1) if st['salary_n'] else 0
            max_salary = round(st['max_salary'], 1)

            province = CITY_TO_PROVINCE.get(city, city)
            province_counter[province] = province_counter.get(province, 0) + count

            coords = CITY_COORDS.get(city)
            city_points.append({
                'city': city or city_name,
                'count': count,
                'avg_salary': avg_salary,
                'max_salary': max_salary,
                'max_salary_yuan': int(round(max_salary * 1000)),
                'lng': coords[0] if coords else None,
                'lat': coords[1] if coords else None,
            })

        provinces = [
            {'name': to_geo_province(k), 'value': v}
            for k, v in province_counter.items()
        ]
        provinces.sort(key=lambda x: x['value'], reverse=True)
        city_points.sort(key=lambda x: (x['max_salary'], x['count']), reverse=True)

        return {
            'provinces': provinces,
            'cities': city_points,
        }

    @staticmethod
    def get_big_screen_data():
        """可视化大屏专用数据包（全部来自数据库，月薪口径）"""
        logger.info('加载可视化大屏数据')
        return {
            'highlight': StatsService.get_highlight_job(),
            'city_avg_salary_top': StatsService.get_city_avg_salary_top(10),
            'salary_range': StatsService.get_salary_range_analysis(),
            'experience_salary': StatsService.get_experience_salary_minmax(),
            'company_size': StatsService.get_company_size_distribution(),
            'salary_top_jobs': StatsService.get_salary_top_jobs(10),
            'map_data': StatsService.get_job_city_distribution(),
            'overview': StatsService.get_overview(),
        }

    @staticmethod
    @cached('stats:dashboard', ttl=300)
    def get_dashboard_data():
        """汇总仪表盘所需的全部统计数据"""
        logger.info('加载仪表盘聚合数据')
        return {
            'overview': StatsService.get_overview(),
            'platform_distribution': StatsService.get_platform_distribution(),
            'salary_distribution': StatsService.get_salary_distribution(),
            'city_ranking': StatsService.get_city_ranking(),
            'skill_ranking': StatsService.get_skill_ranking(limit=40),
            'education_distribution': StatsService.get_education_distribution(),
            'experience_salary': StatsService.get_experience_salary(),
            'platform_salary': StatsService.get_platform_salary(),
            'trend': StatsService.get_trend_data(),
            'map_data': StatsService.get_map_data(),
            'city_avg_salary_top': StatsService.get_city_avg_salary_top(10),
            'salary_range': StatsService.get_salary_range_analysis(),
            'experience_salary_minmax': StatsService.get_experience_salary_minmax(),
            'company_size': StatsService.get_company_size_distribution(),
            'salary_top_jobs': StatsService.get_salary_top_jobs(10),
            'highlight': StatsService.get_highlight_job(),
        }
