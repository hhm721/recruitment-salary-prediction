import os.path

import numpy as np


class Config:
    """数据库配置"""
    MYSQL_CONFIG = {
        "host": "localhost",
        'port': 3306,
        'user': 'root',
        'password': '123456',
        'database': 'recruitment_db',
        'charset': 'utf8mb4'
    }
    # 文件路径配置
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # 模型保存路径
    MODEL_SAVE_PATH = os.path.join(BASE_DIR, "save_models")
    # 数据保存路径
    DATA_SAVE_PATH = os.path.join(BASE_DIR, 'data', 'validation_data.csv')
    # robust_scaler保存路径
    ROBUST_SCALER_SAVE_PATH = os.path.join(MODEL_SAVE_PATH, 'robust_scaler.pkl')
    # 设置随机种子
    RANDOM_STATE = np.random.seed(42)
    # 所有模型名称
    MODEL_KEYS = ["xgboost", "catboost", "gradient", "stacking"]

if __name__ == '__main__':
    config = Config()