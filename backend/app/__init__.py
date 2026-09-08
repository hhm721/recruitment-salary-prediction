"""
Flask 应用工厂模块。

提供全局 SQLAlchemy 实例与 create_app()，用于创建并配置
招聘数据分析后端（鉴权、岗位、爬虫、统计、预测、文档等蓝图）。
"""
from flask import Flask, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

# 全局数据库对象，在 create_app 中通过 init_app 绑定到具体应用实例
db = SQLAlchemy()

def create_app():
    """
    应用工厂：创建 Flask 实例、加载配置、注册扩展与路由蓝图。
    Returns:
        Flask: 已完成初始化的应用对象
    """
    app = Flask(__name__)
    # 从 app.config.Config 加载数据库、JWT、爬虫路径等配置
    app.config.from_object('app.config.Config')

    # 初始化日志
    from .utils.logger import get_logger,setup_logging
    setup_logging(app)
    logger = get_logger("app")

    # 允许前端跨域访问 /api/* 接口
    CORS(app, resources={r'/api/*': {'origins': '*'}})
    # 将 SQLAlchemy 绑定到当前应用
    db.init_app(app)

    # 延迟导入各业务蓝图，避免循环依赖
    from .routes.auth import auth_bp
    from .routes.crawl import crawl_bp
    from .routes.jobs import jobs_bp
    from .routes.stats import stats_bp
    from .routes.rinse import rinse_bp
    from .routes.predict import predict_bp

    # 注册业务路由：认证
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(crawl_bp, url_prefix='/api/crawl')
    app.register_blueprint(jobs_bp, url_prefix='/api/jobs')
    app.register_blueprint(stats_bp, url_prefix='/api/stats')
    app.register_blueprint(rinse_bp, url_prefix='/api/rinse')
    app.register_blueprint(predict_bp, url_prefix='/api/predict')

    @app.route('/api/health')
    def health():
        """健康检查接口，用于探活与部署状态检测。"""
        return jsonify({'code': 200, 'message': 'ok', 'service': 'recruitment-api'})

    @app.before_request
    def _log_request():
        """记录进入的 API 请求：写操作 INFO，高频查询 DEBUG。"""
        from flask import request
        path = request.path
        if path == '/api/health':
            return
        noisy_get_prefixes = (
            '/api/crawl/tasks',
            '/api/crawl/tasks/',
            '/api/stats/',
            '/api/jobs/raw',
            '/api/jobs/clean',
        )
        if request.method == 'GET' and (
                path.startswith(noisy_get_prefixes) or path.startswith('/api/crawl/tasks')
        ):
            logger.debug('HTTP %s %s', request.method, path)
            return
        # 爬虫列表轮询不写 info；启动/删除等写操作仍记录
        if request.method == 'GET' and path.startswith('/api/crawl'):
            logger.debug('HTTP %s %s', request.method, path)
            return
        logger.info('HTTP %s %s', request.method, path)

    @app.after_request
    def _log_response(response):
        from flask import request
        path = request.path
        if path == '/api/health':
            return response
        noisy_get_prefixes = (
            '/api/crawl/tasks',
            '/api/stats/',
            '/api/jobs/raw',
            '/api/jobs/clean',
        )
        if request.method == 'GET' and path.startswith(noisy_get_prefixes):
            logger.debug('HTTP %s %s → %s', request.method, path, response.status_code)
        else:
            logger.info('HTTP %s %s → %s', request.method, path, response.status_code)
        return response

    # 应用上下文中初始化数据库表结构，并确保演示账号存在
    with app.app_context():
        db.create_all()
        _ensure_job_clean_columns()
        from .services.auth_service import AuthService
        AuthService.ensure_demo_user()
        logger.info('Flask 应用初始化完成')

    return app


def _ensure_job_clean_columns():
    """为已有 job_clean 表补齐专项清洗扩展列（create_all 不会 ALTER）。"""
    from sqlalchemy import inspect, text

    try:
        inspector = inspect(db.engine)
        if 'job_clean' not in inspector.get_table_names():
            return
        existing = {c['name'] for c in inspector.get_columns('job_clean')}
    except Exception:
        return

    alters = []
    if 'city_level' not in existing:
        alters.append('ADD COLUMN city_level INT NULL')
    if 'job_level' not in existing:
        alters.append('ADD COLUMN job_level VARCHAR(20) NULL')
    if 'job_features' not in existing:
        alters.append('ADD COLUMN job_features TEXT NULL')
    if 'skill_features' not in existing:
        alters.append('ADD COLUMN skill_features TEXT NULL')
    if 'text_features' not in existing:
        alters.append('ADD COLUMN text_features TEXT NULL')

    if not alters:
        return

    # MySQL 支持一次 ADD 多列
    sql = f"ALTER TABLE job_clean {', '.join(alters)}"
    try:
        db.session.execute(text(sql))
        db.session.commit()
    except Exception:
        db.session.rollback()