"""认证 API"""
from flask import Blueprint, request, jsonify
import uuid
import time

auth_bp = Blueprint('auth', __name__)

# 内存存储匿名用户
anonymous_users = {}

@auth_bp.route('/anonymous', methods=['POST'])
def anonymous_login():
    """匿名登录"""
    device_id = request.headers.get('X-Device-ID') or str(uuid.uuid4())
    
    # 生成简单token
    token = f"anon_{device_id}_{int(time.time())}"
    
    user = {
        'id': f"anon_{device_id[:8]}",
        'nickname': '匿名雅客',
        'avatar': None,
        'token': token
    }
    
    anonymous_users[token] = user
    
    return jsonify({
        'success': True,
        'data': {
            'user': {
                'id': user['id'],
                'nickname': user['nickname'],
                'avatar': user['avatar']
            },
            'token': token
        }
    })

@auth_bp.route('/login', methods=['POST'])
def login():
    """登录"""
    data = request.get_json() or {}
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'success': False, 'error': '请提供邮箱和密码'}), 400
    
    # 简化处理：创建或返回用户
    token = f"user_{email}_{int(time.time())}"
    
    return jsonify({
        'success': True,
        'data': {
            'user': {
                'id': email,
                'nickname': email.split('@')[0],
                'avatar': None
            },
            'token': token
        }
    })

@auth_bp.route('/register', methods=['POST'])
def register():
    """注册"""
    data = request.get_json() or {}
    email = data.get('email')
    password = data.get('password')
    nickname = data.get('nickname', '新雅客')
    
    if not email or not password:
        return jsonify({'success': False, 'error': '请提供邮箱和密码'}), 400
    
    token = f"user_{email}_{int(time.time())}"
    
    return jsonify({
        'success': True,
        'data': {
            'user': {
                'id': email,
                'nickname': nickname,
                'avatar': None
            },
            'token': token
        }
    })
