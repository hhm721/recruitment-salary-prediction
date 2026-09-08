from flask import Blueprint, current_app, jsonify, request
import os
from werkzeug.utils import secure_filename
from ..config import Config
from ..services.predict_service import PredictService
from ..services.resume_parser import ResumeParser

predict_bp = Blueprint("predict", __name__)


def _save_upload(file_storage):
    """保存上传文件到上传目录，返回本地路径。"""
    folder = Config.UPLOAD_FOLDER
    os.makedirs(folder, exist_ok=True)
    original = file_storage.filename or 'resume'
    name, ext = os.path.splitext(secure_filename(original))
    if not name:
        name = 'resume'
    # 追加时间戳避免重名覆盖
    import time
    path = os.path.join(folder, f'{name}_{int(time.time() * 1000)}{ext or ".txt"}')
    file_storage.save(path)
    return path


@predict_bp.route("/preview", methods=["POST"])
def preview_resume():
    """解析上传简历并返回提取的纯文本，用于前端预览。"""
    file = request.files.get('file')
    if not file:
        return jsonify({'code': 400, 'message': '请上传简历文件'}), 400
    path = _save_upload(file)
    try:
        text = ResumeParser.extract_text(path)
        return jsonify({'code': 200, 'data': {'text': text or ''}})
    except Exception as e:
        return jsonify({'code': 500, 'message': f'简历预览失败: {e}'}), 500


@predict_bp.route("/upload", methods=["POST"])
def upload_predict():
    """上传简历并进行薪资预测。"""
    file = request.files.get('file')
    if not file:
        return jsonify({'code': 400, 'message': '请上传简历文件'}), 400
    path = _save_upload(file)
    city = request.form.get('city', '')
    company_size = request.form.get('company_size') or request.form.get('companySize') or ''
    model = request.form.get('model') or 'gradient_boosting'
    try:
        result = PredictService.predict_from_resume(
            path,
            resume_name=file.filename,
            city=city,
            model_name=model,
            company_size=company_size,
        )
        return jsonify({'code': 200, 'data': result})
    except Exception as e:
        return jsonify({'code': 500, 'message': f'预测失败: {e}'}), 500

@predict_bp.route("/history", methods=["GET"])
def prediction_history():
    """分页查询历史薪资预测记录"""
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    data = PredictService.get_history(page=page, per_page=per_page)
    return jsonify({
        "code": 200,
        "data": data
    })


@predict_bp.route('/manual', methods=['POST'])
def manual_predict():
    """根据职位/学历/公司规模/城市/经验等进行薪资预测（输出平均值）。"""
    data = request.get_json() or {}
    skills = data.get('skills', [])
    city = data.get('city', '')
    model_name = data.get('model') or data.get('model_name') or 'gradient_boosting'
    company_size = data.get('company_size') or data.get('companySize') or ''
    job_title = data.get('job') or data.get('job_title') or data.get('title') or ''
    experience = data.get('experience')
    education = data.get('education')
    experience_years = data.get('experience_years')
    education_level = data.get('education_level')

    if not job_title and not skills:
        return jsonify({'code': 400, 'message': '请选择职位或至少填写一项技能'}), 400

    if not skills and job_title:
        from ..services.data_cleaner import extract_skills
        skills = extract_skills(job_title) or [job_title]

    try:
        result = PredictService.predict(
            skills=skills,
            experience=experience,
            experience_years=experience_years,
            education=education,
            education_level=education_level,
            resume_name=job_title or '手动输入',
            city=city,
            model_name=model_name,
            company_size=company_size,
            job_title=job_title,
        )
        return jsonify({'code': 200, 'data': result})
    except FileNotFoundError as e:
        return jsonify({'code': 500, 'message': str(e)}), 500
    except Exception as e:
        return jsonify({'code': 500, 'message': f'预测失败: {e}'}), 500


@predict_bp.route('/skill-gap', methods=['POST'])
def skill_gap_analysis():
    """技能缺口分析：简历技能 vs 目标岗位 JD 技能，输出「还差哪些技能」建议。"""
    data = request.get_json() or {}
    skills = data.get('skills', [])
    job_title = data.get('job') or data.get('job_title') or data.get('title') or ''
    city = data.get('city', '')
    top_n = data.get('top_n', 10)
    if not skills:
        return jsonify({'code': 400, 'message': '请至少填写一项简历技能'}), 400
    try:
        result = PredictService.analyze_skill_gap(
            skills=skills, job_title=job_title, city=city, top_n=top_n,
        )
        return jsonify({'code': 200, 'data': result})
    except Exception as e:
        return jsonify({'code': 500, 'message': f'技能缺口分析失败: {e}'}), 500

