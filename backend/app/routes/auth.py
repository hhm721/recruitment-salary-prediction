"""
认证相关路由：注册、登录、获取用户信息、退出登录
"""
from flask import Blueprint,jsonify,request,current_app
from ..services.auth_service import AuthService

#定义蓝图
auth_bp = Blueprint('auth',__name__)

@auth_bp.route('/register',methods=['POST'])
def register():
    """用户注册接口 创建账号并返回登录"""
    #接收参数
    data = request.get_json(silent=True) or {}
    try:
        user = AuthService.register(
            username=data.get('username'),
            password=data.get('password'),
            email=data.get('email'),
            nickname=data.get('nickname'),
        )

        token = AuthService.create_token(user,current_app.config['SECRET_KEY'])
        return jsonify({
            "code": 200,
            "message": "注册成功",
            "data": {
                "token": token,
                "user": user.to_dict()
            }
        })
    except ValueError as e:
        return jsonify({'code': 400 ,'message': str(e)}), 400


@auth_bp.route('/login',methods=['POST'])
def login():
    """用户登录接口，校验账号密码并返回登录"""
    #接收参数
    data = request.get_json(silent=True) or {}
    #调用服务端校验方法进行校验
    try:
        user = AuthService.login(
            username=data.get('username'),
            password=data.get('password'),
        )
        #创建Token
        token = AuthService.create_token(user,current_app.config['SECRET_KEY'])
        #返回结果
        return jsonify({
            "code": 200,
            "message": "登录成功",
            "data": {
                "token": token,
                "user": user.to_dict()
            }
        })
    except ValueError as e:
        return jsonify({'code': 400 ,'message': str(e)}), 400

@auth_bp.route('/logout',methods=['POST'])
def logout():
    """用户退出登录，前端清除token"""
    return jsonify({"code":200,"message":"退出成功"})
