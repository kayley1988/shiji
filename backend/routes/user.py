"""用户路由"""
from flask import Blueprint, jsonify, request
from models import User
from functools import wraps

user_bp = Blueprint('user', __name__, url_prefix='/v1/me')

def get_user_id():
    from flask import request, g
    return request.headers.get('X-User-ID') or g.get('user_id') or 'default_user'

@user_bp.route('/profile', methods=['GET'])
def get_profile():
    """获取当前用户资料"""
    user_id = get_user_id()
    return jsonify({
        'success': True,
        'data': {
            'id': user_id,
            'nickname': '匿名雅客',
            'email': None,
            'avatar': None,
            'created_at': None
        }
    })

@user_bp.route('/stats', methods=['GET'])
def get_user_stats():
    """获取用户统计"""
    return jsonify({
        'success': True,
        'data': {
            'total_games': 0,
            'total_poems': 0,
            'favorites': 0,
            'reading_minutes': 0
        }
    })
