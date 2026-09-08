import re  # 正则表达式，用于校验用户名和邮箱格式
from datetime import datetime, timedelta  # 日期时间与时间差，用于登录时间与令牌过期
import jwt  # JWT 编解码库
from werkzeug.security import check_password_hash, generate_password_hash  # 密码哈希生成与校验
from .. import db  # 数据库会话
from ..models import User  # 用户模型


class AuthService:
    """用户认证与令牌服务"""

    USERNAME_PATTERN = re.compile(r'^[a-zA-Z0-9_]{3,20}$')  # 用户名格式：3-20 位字母数字下划线
    EMAIL_PATTERN = re.compile(r'^[\w.-]+@[\w.-]+\.\w+$')  # 邮箱格式正则

    @staticmethod
    def register(username, password, email=None, nickname=None):
        """注册新用户并写入数据库"""
        username = (username or '').strip()  # 去除用户名首尾空白
        email = (email or '').strip() or None  # 邮箱去空白，空串转为 None
        nickname = (nickname or '').strip() or None  # 昵称去空白，空串转为 None

        if not AuthService.USERNAME_PATTERN.match(username):  # 校验用户名格式
            raise ValueError('用户名需为 3-20 位字母、数字或下划线')
        if len(password or '') < 6:  # 校验密码长度
            raise ValueError('密码长度不能少于 6 位')
        if email and not AuthService.EMAIL_PATTERN.match(email):  # 校验邮箱格式
            raise ValueError('邮箱格式不正确')
        if User.query.filter_by(username=username).first():  # 检查用户名是否已存在
            raise ValueError('用户名已存在')
        if email and User.query.filter_by(email=email).first():  # 检查邮箱是否已注册
            raise ValueError('邮箱已被注册')

        user = User(  # 构造新用户对象
            username=username,
            email=email,
            nickname=nickname or username,  # 无昵称时默认使用用户名
            password_hash=generate_password_hash(password),  # 存储密码哈希而非明文
        )
        db.session.add(user)  # 加入会话待提交
        db.session.commit()  # 持久化到数据库
        return user  # 返回新建用户

    @staticmethod
    def login(username, password):
        """校验用户名密码并更新最近登录时间"""
        username = (username or '').strip()  # 去除用户名首尾空白
        user = User.query.filter_by(username=username).first()  # 按用户名查询用户
        if not user or not check_password_hash(user.password_hash, password or ''):  # 用户不存在或密码错误
            raise ValueError('用户名或密码错误')

        user.last_login = datetime.now()  # 更新最近登录时间
        db.session.commit()  # 提交变更
        return user  # 返回登录用户

    @staticmethod
    def create_token(user, secret_key, expire_hours=168):
        """为用户生成 JWT 登录令牌"""
        payload = {  # 令牌载荷
            'user_id': user.id,  # 用户 ID
            'username': user.username,  # 用户名
            'exp': datetime.utcnow() + timedelta(hours=expire_hours),  # 过期时间（UTC）
        }
        return jwt.encode(payload, secret_key, algorithm='HS256')  # 使用 HS256 签名并返回令牌

    @staticmethod
    def decode_token(token, secret_key):
        """解析并校验 JWT 令牌，返回载荷"""
        if not token:  # 未提供令牌
            raise ValueError('未提供登录凭证')
        try:
            payload = jwt.decode(token, secret_key, algorithms=['HS256'])  # 解码并校验签名
            return payload  # 返回载荷字典
        except jwt.ExpiredSignatureError as exc:  # 令牌已过期
            raise ValueError('登录已过期，请重新登录') from exc
        except jwt.InvalidTokenError as exc:  # 令牌无效
            raise ValueError('无效的登录凭证') from exc

    @staticmethod
    def get_user_by_id(user_id):
        """根据用户 ID 查询用户"""
        return User.query.get(user_id)  # 主键查询，不存在返回 None

    @staticmethod
    def ensure_demo_user():
        """确保演示账号 admin 存在，不存在则创建"""
        if User.query.filter_by(username='admin').first():  # 已存在则直接返回
            return
        user = User(  # 创建默认演示账号
            username='admin',
            email='admin@example.com',
            nickname='管理员',
            password_hash=generate_password_hash('admin123'),  # 默认密码 admin123
        )
        db.session.add(user)  # 加入会话
        db.session.commit()  # 写入数据库
