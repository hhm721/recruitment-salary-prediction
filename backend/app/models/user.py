"""
用户模型
=========

字段 (严格按需求):
  - username:        用户名 3-20 位, 唯一
  - email:           邮箱, 符合格式
  - password_hash:   密码哈希 (Werkzeug)
  - nickname:        昵称
  - created_at:      注册时间 (需求: created_at)
  - login_time:      最近登录时间

方法:
  - set_password / check_password: 安全哈希
  - to_dict: 序列化（排除密码哈希）
"""

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from .. import db

class User(db.Model):
    """用户表"""
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password_hash = db.Column(db.String(256), nullable=False)
    nickname = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.now)
    last_login = db.Column(db.DateTime)

    # ---------- 序列化 ----------
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'nickname': self.nickname or self.username,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
        }