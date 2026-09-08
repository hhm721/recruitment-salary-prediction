import io
import json
from datetime import datetime
import pandas as pd
from flask import send_file
from venv import logger
from .. import db
from ..models import JobRaw, JobClean
from ..utils.logger import get_logger

logger = get_logger(__name__)

RAW_EDITABLE = (  # 原始职位允许前端编辑的字段名
    'platform', 'title', 'company', 'city', 'salary_raw',
    'experience', 'education', 'skills', 'description',
)
CLEAN_EDITABLE = (  # 清洗职位允许编辑的字段名
    'platform', 'title', 'company', 'city',
    'salary_min', 'salary_max', 'salary_avg',
    'experience_years', 'education_level', 'skills',
)

def filter_raw_query(platform=None, city=None, keyword=None, company=None, education=None):
    """按条件过滤原始职位查询"""
    query = JobRaw.query  # 基础查询
    if platform:  # 按平台精确过滤
        query = query.filter_by(platform=platform)
    if city:  # 城市模糊匹配
        query = query.filter(JobRaw.city.like(f'%{city}%'))
    if keyword:  # 职位标题关键词
        query = query.filter(JobRaw.title.like(f'%{keyword}%'))
    if company:  # 公司名称模糊匹配
        query = query.filter(JobRaw.company.like(f'%{company}%'))
    if education:  # 学历要求模糊匹配
        query = query.filter(JobRaw.education.like(f'%{education}%'))
    return query  # 返回可继续链式调用的 Query 对象


def filter_clean_query(platform=None, city=None, keyword=None, company=None, education=None):
    """按条件过滤清洗后职位查询"""
    query = JobClean.query
    if platform:
        query = query.filter_by(platform=platform)
    if city:
        query = query.filter(JobClean.city.like(f'%{city}%'))
    if keyword:
        query = query.filter(JobClean.title.like(f'%{keyword}%'))
    if company:
        query = query.filter(JobClean.company.like(f'%{company}%'))
    if education and education != '不限':  # 「不限」表示不按学历筛
        edu_map = {'高中/中专': 1, '高中': 1, '大专': 2, '本科': 3, '硕士': 4, '博士': 5}  # 文案到等级
        level = edu_map.get(education)
        if level is not None:
            query = query.filter_by(education_level=level)  # 按数值等级精确过滤
    return query

def update_raw_job(job_id, data):
    """更新原始职位可编辑字段"""
    job = JobRaw.query.get(job_id)  # 按 ID 取记录
    if not job:
        logger.warning('更新原始职位失败：记录不存在 job_id=%s', job_id)
        return None
    for key in RAW_EDITABLE:  # 仅更新白名单字段
        if key in data:
            setattr(job, key, data[key])
    db.session.commit()
    logger.info('更新原始职位成功 job_id=%s title=%s', job_id, job.title)
    return job

def delete_raw_job(job_id):
    """删除原始职位及其关联的清洗数据"""
    job = JobRaw.query.get(job_id)
    if not job:
        logger.warning('删除原始职位失败：记录不存在 job_id=%s', job_id)
        return False
    JobClean.query.filter_by(raw_id=job.id).delete()  # 先删关联清洗记录
    db.session.delete(job)  # 再删原始记录
    db.session.commit()
    logger.info('删除原始职位成功 job_id=%s', job_id)
    return True

def update_clean_job(job_id, data):
    """更新清洗职位字段，并同步薪资均值与技能数"""
    job = JobClean.query.get(job_id)
    if not job:
        logger.warning('更新清洗职位失败：记录不存在 job_id=%s', job_id)
        return None
    for key in CLEAN_EDITABLE:
        if key in data:
            setattr(job, key, data[key])
    if 'salary_min' in data or 'salary_max' in data:  # 薪资区间变更时重算均值
        smin = float(job.salary_min) if job.salary_min is not None else None
        smax = float(job.salary_max) if job.salary_max is not None else None
        if smin is not None and smax is not None:
            job.salary_avg = (smin + smax) / 2  # 上下限都有则取平均
        elif smin is not None:
            job.salary_avg = smin  # 仅下限
        elif smax is not None:
            job.salary_avg = smax  # 仅上限
    if 'skills' in data and isinstance(data['skills'], str):  # 技能为 JSON 字符串时更新数量
        try:
            skills = json.loads(data['skills'])
            job.skill_count = len(skills) if isinstance(skills, list) else 0
        except (json.JSONDecodeError, TypeError):
            pass  # 解析失败则跳过 skill_count
    db.session.commit()
    logger.info('更新清洗职位成功 job_id=%s title=%s', job_id, job.title)
    return job


def delete_clean_job(job_id):
    """删除清洗职位记录"""
    job = JobClean.query.get(job_id)
    if not job:
        logger.warning('删除清洗职位失败：记录不存在 job_id=%s', job_id)
        return False
    db.session.delete(job)
    db.session.commit()
    logger.info('删除清洗职位成功 job_id=%s', job_id)
    return True


def _rows_to_export(items):
    """将职位对象列表转为可导出的字典列表"""
    return [item.to_dict() for item in items]  # 每条记录转字典


def export_jobs_response(items, fmt, filename_prefix):
    """按指定格式导出职位数据并返回下载响应"""
    rows = _rows_to_export(items)  # 转为行数据
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')  # 文件名时间戳
    logger.info(
        '导出数据 prefix=%s fmt=%s rows=%s',
        filename_prefix, fmt, len(rows),
    )

    if fmt == 'json':  # JSON 格式导出
        content = json.dumps(rows, ensure_ascii=False, indent=2)
        buf = io.BytesIO(content.encode('utf-8'))
        return send_file(
            buf,
            mimetype='application/json',
            as_attachment=True,
            download_name=f'{filename_prefix}_{timestamp}.json',
        )

    if fmt == 'txt':  # 制表符分隔的文本
        if rows:
            headers = list(rows[0].keys())  # 首行表头
            lines = ['\t'.join(headers)]
            for row in rows:
                lines.append('\t'.join(str(row.get(h, '') or '') for h in headers))  # 每行按列拼接
            content = '\n'.join(lines)
        else:
            content = '无数据'
        buf = io.BytesIO(content.encode('utf-8'))
        return send_file(
            buf,
            mimetype='text/plain; charset=utf-8',
            as_attachment=True,
            download_name=f'{filename_prefix}_{timestamp}.txt',
        )

    if fmt == 'excel':  # Excel xlsx
        df = pd.DataFrame(rows)
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='数据')
        buf.seek(0)  # 重置读指针供 send_file 读取
        return send_file(
            buf,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'{filename_prefix}_{timestamp}.xlsx',
        )

    return None  # 不支持的格式
