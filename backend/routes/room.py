"""房间/对战 API"""
from flask import Blueprint, request, jsonify
import uuid
from datetime import datetime

room_bp = Blueprint('room', __name__)

# 内存存储房间
rooms = {}

@room_bp.route('', methods=['GET'])
def list_rooms():
    """获取房间列表"""
    return jsonify({
        'success': True,
        'data': {'rooms': []}
    })

@room_bp.route('', methods=['POST'])
def create_room():
    """创建房间"""
    data = request.get_json() or {}
    room_id = str(uuid.uuid4())[:8].upper()
    
    rooms[room_id] = {
        'id': room_id,
        'name': data.get('name', '诗词对战'),
        'mode': data.get('mode', 'feihua'),
        'created_at': datetime.now().isoformat(),
        'members': []
    }
    
    return jsonify({
        'success': True,
        'data': {'room_id': room_id}
    })

@room_bp.route('/<room_id>', methods=['GET'])
def get_room(room_id):
    """获取房间信息"""
    room = rooms.get(room_id)
    if not room:
        return jsonify({'success': False, 'error': '房间不存在'}), 404
    
    return jsonify({
        'success': True,
        'data': room
    })

@room_bp.route('/<room_id>/join', methods=['POST'])
def join_room(room_id):
    """加入房间"""
    data = request.get_json() or {}
    
    if room_id not in rooms:
        return jsonify({'success': False, 'error': '房间不存在'}), 404
    
    member = {
        'id': str(uuid.uuid4()),
        'nickname': data.get('nickname', '匿名'),
        'score': 0
    }
    rooms[room_id]['members'].append(member)
    
    return jsonify({
        'success': True,
        'data': {'member_id': member['id']}
    })
