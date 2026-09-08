"""
数据库链接
"""

from sqlalchemy import create_engine
from ml.salary_forecast.config.config import Config

class DatabaseEngine:
    @classmethod
    def get_mysql_engine(cls):
        """获取MYSQL连接引擎"""
        try:
            connection_string = (f"mysql+pymysql://{Config.MYSQL_CONFIG['user']}:{Config.MYSQL_CONFIG['password']}"
                                 f"@{Config.MYSQL_CONFIG['host']}:{Config.MYSQL_CONFIG['port']}"
                                 f"/{Config.MYSQL_CONFIG['database']}?charset={Config.MYSQL_CONFIG['charset']}")
            # 创建引擎
            engine = create_engine(connection_string)
            return engine
        except Exception as e:
            print(f"MySQL连接失败：{e}")
            return None