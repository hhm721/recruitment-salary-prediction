"""
用于数据清洗
"""
from flask import Blueprint, jsonify, request
from ..models import JobClean
from ..services.rinse_service import (
    filter_clean_query,
    delete_clean_job,
    update_clean_job,
    export_jobs_response
)
from ..services.data_cleaner import DataCleaner
from ..config import Config
from ..utils.cache import invalidate_stats_cache  # 数据写入后失效统计缓存

rinse_bp = Blueprint('rise', __name__)



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

# 专项清洗类型 → 处理函数
CLEAN_TYPE_HANDLERS = {  # 各清洗类型对应的处理函数
    'salary': DataCleaner.clean_salary,  # 薪资字段清洗
    'education': DataCleaner.clean_education,  # 学历字段清洗
    'experience': DataCleaner.clean_experience,  # 经验字段清洗
    'city': DataCleaner.clean_city,  # 城市字段清洗
    'job': DataCleaner.clean_job,  # 岗位名称清洗
    'skills': DataCleaner.clean_skills,  # 技能标签清洗
    'description': DataCleaner.clean_description,  # 岗位描述清洗
}

@rinse_bp.route("/clean",methods=['GET'])
def get_clean_jobs():
    """分页查询后的岗位数据"""
    #接收信息
    page = request.args.get('page',1,type=int)
    per_page = request.args.get('per_page',20,type=int)

    filters = _filter_args()

    query = filter_clean_query(**filters)
    pagination = query.order_by(JobClean.clean_time.desc()).paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        "code":200,
        "data":{
            "items":[j.to_dict() for j in pagination.items],
            "total":pagination.total,
            "page":page,
            "per_page":per_page,
        }
    })
@rinse_bp.route("/clean/run",methods=['POST'])
def clean_run():
    """触发数据清洗"""
    #解析请求体
    data = request.get_json() or {}
    #可选平台过滤
    platform = data.get("platform")
    #清洗原始数据
    count = DataCleaner.clean_all_uncleaned(platform = platform)
    #联动执行专项清洗
    details = {} #用于汇总结果
    for name , handler in CLEAN_TYPE_HANDLERS.items():
        try:
            if name =="skills":
                details[name] = handler(platform=platform,top_n=50)
            elif name =="description":
                details[name] = handler(platform=platform,max_features=100)
            else:
    #其他类型
                details[name] = handler(platform=platform)
        except Exception as e:
            #记录错误信息
            details[name] = {'error':str(e)}
    invalidate_stats_cache()  # 清洗后数据已变更，失效统计缓存
    return jsonify({
        "code":200,
        "data":{
            "cleaned_count":count,
            "details":details,
        },
        "message":"清洗完成"
    })

@rinse_bp.route("/clean/<int:job_id>",methods=['PUT'])
def update_clean(job_id):
    """按id更新一条清洗后的数据"""
    data = request.get_json() or {}
    #执行更新
    job = update_clean_job(job_id,data)
    #记录是否存在
    if not job:
        return jsonify({"code":404,"message":"记录不存在"})
    return jsonify({
        "code":200,
        "data":job.to_dict(),
        "message":"更新成功"
    })

@rinse_bp.route("/clean/<int:job_id>",methods=['DELETE'])
def remove_clean(job_id):
    if not delete_clean_job(job_id):
        return jsonify({"code":404,"message":"记录不存在"})
    invalidate_stats_cache()
    return jsonify({
        "code":200,
        "message":"删除成功"
    })
@rinse_bp.route('/clean/export', methods=['GET'])  # 导出清洗后岗位数据接口
def export_clean():
    """导出清洗后岗位数据（支持 excel/json/txt）。"""
    fmt = request.args.get('format', 'excel')  # 导出格式，默认 Excel
    if fmt not in ('excel', 'json', 'txt'):  # 校验格式是否支持
        return jsonify({'code': 400, 'message': '不支持的导出格式'}), 400  # 返回 400
    filters = _filter_args()  # 提取筛选条件
    items = filter_clean_query(**filters).order_by(JobClean.clean_time.desc()).limit(Config.EXPORT_LIMIT).all()  # 查询待导出数据
    response = export_jobs_response(items, fmt, '清洗数据')  # 生成文件下载响应
    if not response:  # 导出失败
        return jsonify({'code': 400, 'message': '导出失败'}), 400  # 返回 400
    return response  # 返回文件流响应