"""统计与可视化数据路由：总览、大屏、平台/薪资/城市/技能等聚合接口。"""
from flask import Blueprint, jsonify, request  # Flask 蓝图、JSON 响应与请求对象

from ..services.stats_service import StatsService  # 统计分析业务服务

stats_bp = Blueprint('stats', __name__)  # 创建统计模块蓝图


@stats_bp.route('/overview', methods=['GET'])  # 系统数据总览接口
def overview():
    """获取系统数据总览（原始量、清洗量、均薪、城市数等）。"""
    return jsonify({'code': 200, 'data': StatsService.get_overview()})  # 返回总览指标


@stats_bp.route('/dashboard', methods=['GET'])  # 可视化大屏聚合数据接口
def dashboard():
    """获取可视化大屏所需的聚合数据包。"""
    return jsonify({'code': 200, 'data': StatsService.get_dashboard_data()})  # 返回大屏数据包


@stats_bp.route('/big-screen', methods=['GET'])  # 科技风大屏专用数据接口
def big_screen():
    """获取科技风可视化大屏专用数据。"""
    return jsonify({'code': 200, 'data': StatsService.get_big_screen_data()})  # 返回科技风大屏数据


@stats_bp.route('/platform', methods=['GET'])  # 各平台岗位分布接口
def platform_distribution():
    """获取各招聘平台岗位数量分布。"""
    return jsonify({'code': 200, 'data': StatsService.get_platform_distribution()})  # 返回平台分布


@stats_bp.route('/salary', methods=['GET'])  # 薪资区间分布接口
def salary_distribution():
    """获取薪资区间分布统计。"""
    return jsonify({'code': 200, 'data': StatsService.get_salary_distribution()})  # 返回薪资分布


@stats_bp.route('/city', methods=['GET'])  # 城市排行接口
def city_ranking():
    """获取城市岗位数量/薪资排行。"""
    limit = request.args.get('limit', 10, type=int)  # 返回城市数量上限
    return jsonify({'code': 200, 'data': StatsService.get_city_ranking(limit)})  # 返回城市排行


@stats_bp.route('/skills', methods=['GET'])  # 技能词频排行接口
def skill_ranking():
    """获取技能词频排行。"""
    limit = request.args.get('limit', 20, type=int)  # 返回技能数量上限
    return jsonify({'code': 200, 'data': StatsService.get_skill_ranking(limit)})  # 返回技能排行


@stats_bp.route('/skill-city-salary', methods=['GET'])  # 技能-城市-薪资三维交叉分析接口
def skill_city_salary():
    """获取技能-城市-薪资三维交叉分析（热力图）数据。"""
    skill_limit = request.args.get('skill_limit', 15, type=int)
    city_limit = request.args.get('city_limit', 15, type=int)
    return jsonify({'code': 200, 'data': StatsService.get_skill_city_salary_heatmap(skill_limit, city_limit)})


@stats_bp.route('/education', methods=['GET'])  # 学历要求分布接口
def education_distribution():
    """获取学历要求分布。"""
    return jsonify({'code': 200, 'data': StatsService.get_education_distribution()})  # 返回学历分布


@stats_bp.route('/experience-salary', methods=['GET'])  # 经验与薪资关系接口
def experience_salary():
    """获取工作经验与平均薪资关系数据。"""
    return jsonify({'code': 200, 'data': StatsService.get_experience_salary()})  # 返回经验-薪资关系


@stats_bp.route('/platform-salary', methods=['GET'])  # 各平台平均薪资对比接口
def platform_salary():
    """获取各平台平均薪资对比数据。"""
    return jsonify({'code': 200, 'data': StatsService.get_platform_salary()})  # 返回平台薪资对比


@stats_bp.route('/map', methods=['GET'])  # 地图可视化数据接口
def map_data():
    """获取地图可视化所需的地区分布数据。"""
    return jsonify({'code': 200, 'data': StatsService.get_map_data()})  # 返回地图分布数据


@stats_bp.route('/trend', methods=['GET'])  # 岗位采集与薪资趋势接口
def trend():
    """获取岗位采集/薪资趋势数据。"""
    return jsonify({'code': 200, 'data': StatsService.get_trend_data()})  # 返回趋势数据
