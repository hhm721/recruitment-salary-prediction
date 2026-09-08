"""
爬虫调度路由：启动采集、查询任务、删除任务
"""

from flask import Blueprint, jsonify, request

from ..services.crawl_service import CrawlService


#定义蓝图
crawl_bp = Blueprint('crawl', __name__)


@crawl_bp.route('/start', methods=["POST"])
def start_crawl():
    """ 启动爬虫采集任务 可选择平台 城市 关键词 页数"""
    #接收参数
    data = request.get_json() or {}
    #调用服务端处理爬虫调度任务
    tasks = CrawlService.start_crawl(
        platform = data.get('platform'),
        keyword = data.get('keyword'),
        city = data.get('city'),
        pages = data.get('pages'),
    )
    #返回结果
    return jsonify({"code": 200, "data": tasks,"message": "爬虫任务已启动"})

@crawl_bp.route("/tasks", methods=["GET"])
def get_tasks():
    """分页查询爬虫任务列表"""
    #接收页码和每页条数
    page = request.args.get("page",1,type=int)
    page_size = request.args.get("per_page",20,type=int)
    #调用服务层获取所有数据
    data = CrawlService.get_tasks(page, page_size)
    #返回数据
    return jsonify({"code": 200, "data": data})
@crawl_bp.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
        """按id删除爬虫记录"""
        ok, message = CrawlService.delete_task(task_id)
        if not ok:
            code = 404 if message =="任务不存在" else 400
            return jsonify({"code": code, "message": message}),code
        #任务存在时返回信息
        return jsonify({"code": 200, "message": message})


