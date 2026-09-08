import os
# 从 .env 文件中加载环境变量到 Python 程序中
from dotenv import load_dotenv

# 实例化
load_dotenv()

class Config:
    # 设置 Flask 应用的密钥，用于加密 JWT 令牌等安全功能
    SECRET_KEY = os.getenv('SECRET_KEY', 'recruitment-secret-key')
    # 数据库连接字符串，用于连接 MySQL 数据库
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{os.getenv('DB_USER', 'root')}:"
        f"{os.getenv('DB_PASSWORD', 'root')}@"
        f"{os.getenv('DB_HOST', 'localhost')}:"
        f"{os.getenv('DB_PORT', '3306')}/"
        f"{os.getenv('DB_NAME', 'recruitment_db')}?charset=utf8mb4"
    )
    # 设置 SQLAlchemy 是否跟踪数据库修改，通常在开发环境中设置为 False，生产环境中设置为 True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # 控制是否在控制台打印所有 SQL 语句，方便调试
    SQLALCHEMY_ECHO = False
    # 设置爬虫关键词，用于爬取招聘网站的职位信息
    CRAWL_KEYWORD = os.getenv('CRAWL_KEYWORD', 'Python')
    CRAWL_CITY = os.getenv('CRAWL_CITY', '北京')
    CRAWL_PAGES = int(os.getenv('CRAWL_PAGES', '3'))

    # 招聘平台英文 key 到中文名称的映射
    PLATFORM_NAMES = {'lagou': '拉勾网', 'liepin': '猎聘网', 'qcwy': '前程无忧', 'zhilian': '智联招聘'}
    # 设置模型路径，用于加载文件
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # 设置项目目录路径，用于加载文件
    PROJECT_DIR = os.path.dirname(BASE_DIR)
    # 设置上传文件的保存路径，用于保存用户上传的文件
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    # 设置爬虫目录路径，用于加载爬虫文件（scrapy.cfg 所在目录）
    SCRAPY_DIR = os.path.join(PROJECT_DIR, 'recuitment_spider')
    # 设置模型路径，用于加载模型文件
    MODEL_PATH = os.getenv('MODEL_PATH', os.path.join(PROJECT_DIR, 'ml', 'salary_forecast','save_models' ))

    # 设置文件上传的最大大小，单位为字节，这里设置为 16MB
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    # 设置 JWT 令牌的过期时间，单位为小时，这里设置为 168 小时（7 天）
    JWT_EXPIRE_HOURS = int(os.getenv('JWT_EXPIRE_HOURS', '168'))

    # 前端展示名 / 请求别名 → 模型文件 key
    MODEL_FILES = {
        'catboost': 'catboost_model.pkl',
        'gradient_boosting': 'gradient_boosting_model.pkl',
        'stacking_ensemble': 'stacking_ensemble_model.pkl',
    }

    MODEL_LABELS = {
        'catboost': 'CatBoost',
        'gradient_boosting': '梯度提升',
        'stacking_ensemble': 'Stacking集成',
    }

    MODEL_ALIASES = {
        'CatBoost': 'catboost',
        'catboost': 'catboost',
        '梯度提升': 'gradient_boosting',
        '梯度提升树': 'gradient_boosting',
        'gradient_boosting': 'gradient_boosting',
        'gb': 'gradient_boosting',
        'gbr': 'gradient_boosting',
        'Stacking集成': 'stacking_ensemble',
        'Stacking': 'stacking_ensemble',
        'stacking': 'stacking_ensemble',
        'stacking_ensemble': 'stacking_ensemble',
        '集成': 'stacking_ensemble',
    }

    EDU_LEVEL_MAP = {
        '博士': 6, '硕士': 5, '研究生': 5,
        '本科': 4, '大专': 3, '中专': 2,
        '高中': 2, '初中': 1, '小学': 1,
    }

    CITY_TIER_MAP = {
        '北京': 5, '上海': 5, '广州': 5, '深圳': 5,
        '成都': 4, '杭州': 4, '武汉': 4, '南京': 4, '重庆': 4,
        '西安': 4, '苏州': 4, '天津': 4, '长沙': 4, '郑州': 4,
        '东莞': 4, '青岛': 4, '合肥': 4, '宁波': 4, '无锡': 4,
        '佛山': 3, '济南': 3, '长春': 3, '大连': 3, '厦门': 3,
        '沈阳': 3, '昆明': 3, '石家庄': 3, '南昌': 3, '哈尔滨': 3,
        '太原': 3, '贵阳': 3, '乌鲁木齐': 3, '兰州': 3, '南宁': 3,
        '福州': 3, '中山': 3, '潍坊': 3, '盐城': 3, '洛阳': 3,
        '芜湖': 3, '扬州': 3,
        '三亚': 2, '万宁': 2,
    }

    SCALE_MAP = {
        '少于50人': 1,
        '50-100人': 2,
        '150-500人': 3,
        '500-1000人': 4,
        '1000-5000人': 5,
        '5000人以上': 6,
        # 前端/简历常见别名
        '0-20人': 1,
        '20-99人': 2,
        '50-150人': 2,
        '100-499人': 3,
        '150-500': 3,
        '2000人以上': 6,
        '1000以上': 5,
    }

    SKILL_CATEGORIES = {
        'programming': ['python', 'java', 'c++', 'go', 'rust', 'javascript', 'typescript'],
        'web': ['react', 'vue', 'angular', 'html', 'css', 'node', 'spring', 'django'],
        'data': ['sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch'],
        'cloud': ['docker', 'kubernetes', 'aws', 'azure', 'gcp', 'linux'],
        'ml': ['tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy', '机器学习', '算法'],
        'management': ['管理', '项目', '团队', '领导', '协调', '产品'],
    }

    SKILL_COMBOS = [
        ['python', 'sql'],
        ['python', 'java'],
        ['react', 'node'],
        ['docker', 'kubernetes'],
        ['管理', '项目'],
        ['测试', '自动化'],
    ]

    INDUSTRIES = ['互联网', '金融', '电商', '医疗', '教育', '服务业', '制造业']
    COMPANY_TYPES = ['国企', '民营', '上市公司', '外资', '合资', '私营']
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'doc', 'docx'}