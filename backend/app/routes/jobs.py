"""
岗位数据处理：原始数据查询 更新 删除 导出
"""
from ..config import Config
from flask import Blueprint, jsonify, request
from ..models import JobRaw
from ..services.job_service import (filter_raw_query, update_raw_job, delete_raw_job, export_jobs_response)
from ..utils.cache import invalidate_stats_cache  # 数据写入后失效统计缓存
#定义蓝图
jobs_bp = Blueprint('jobs', __name__)

#筛选条件
def _filter_args():
    """从请求参数当中提取岗位筛选（平台 城市 关键词 公司名称 学历。。。。）"""
    return{
        #组装筛选条件
        "platform":request.args.get('platform'),
        "city":request.args.get('city'),
        "keyword":request.args.get('keyword'),
        "company":request.args.get('company'),
        "education":request.args.get('education'),
    }

@jobs_bp.route('/raw', methods=['GET'])


def get_raw_jobs():
    """分页查询所有原始岗位数据"""
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    #提取筛选条件
    filters = _filter_args()
    #构建数据查询
    query = filter_raw_query(**filters)
    pagination = query.order_by(JobRaw.crawl_time.desc()).paginate(page=page, per_page=per_page, error_out=False)
    #返回数据
    return jsonify({
        "code": 200,
        "data": {
            "items": [j.to_dict() for j in pagination.items],
            "total": pagination.total,
            "page":page,
            "per_page":per_page,
        }
    })


###########
###########
##########
# @jobs_bp.route('/platforms', methods=["GET"])
# def get_platform_list():
#     """获取所有不重复招聘平台"""
#     platform_rows = JobRaw.query.with_entities(JobRaw.platform).distinct().all()
#     data = [row[0] for row in platform_rows if row[0]]
#     return jsonify({
#         "code": 200,
#         "data": data
#     })
##########
##########
##########


@jobs_bp.route("/raw/<int:job_id>", methods=['PUT'])
def update_raw(job_id):
    """按id更新一条岗位记录"""
    #接收修改参数
    data = request.get_json()
    #调用服务层更新方法执行更新
    job = update_raw_job(job_id, data)
    #判断job是否存在
    if not job:
        return jsonify({"code": 404, "message": "记录不存在"}),404
    invalidate_stats_cache()
    return jsonify({"code": 200, "data": job.to_dict(),"message": "更新成功"})

@jobs_bp.route("/raw/<int:job_id>", methods=['DELETE'])
def remove_raw(job_id):
    """按id删除一条岗位记录"""
    if not delete_raw_job(job_id):
        return jsonify({"code":404,"message":"记录不存在"}),404
    invalidate_stats_cache()
    return jsonify({"code":200,"message":"删除成功"})

@jobs_bp.route('/raw/export', methods=['GET'])  # 导出原始岗位数据接口
def export_raw():
    """导出原始岗位数据（支持 excel/json/txt）。"""
    fmt = request.args.get('format', 'excel')  # 导出格式，默认 Excel
    if fmt not in ('excel', 'json', 'txt'):  # 校验格式是否支持
        return jsonify({'code': 400, 'message': '不支持的导出格式'}), 400  # 返回 400
    filters = _filter_args()  # 提取筛选条件
    items = filter_raw_query(**filters).order_by(JobRaw.crawl_time.desc()).limit(10000).all()  # 查询待导出数据
    response = export_jobs_response(items, fmt, '原始数据')  # 生成文件下载响应
    if not response:  # 导出失败
        return jsonify({'code': 400, 'message': '导出失败'}), 400  # 返回 400
    return response  # 返回文件流响应

@jobs_bp.route("platforms", methods=['GET'])
def get_platforms():
    """获取招聘平台"""
    platform = [{"key": k, "name": v} for k,v in Config.PLATFORM_NAMES.items()]
    #返回数据
    return jsonify({"code": 200, "data": platform})