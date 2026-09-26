"""
接尾飞花令 API 路由
"""
import json
import uuid
import random
from datetime import datetime, timedelta
from functools import wraps

from flask import Blueprint, request, jsonify, g
from flask_socketio import emit

from config import Config
from services.tail_connect_service import TailConnectService, TailConnectState

tail_connect_bp = Blueprint('tail_connect', __name__, url_prefix='/v1/tail-connect')

# 内存存储（实际应使用 Redis）
_game_states = {}
_member_tokens = {}


def require_auth(f):
    """简单的认证装饰器"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'error': 'UNAUTHORIZED'}), 401
        # 简化验证，实际应查数据库
        g.token = token
        return f(*args, **kwargs)
    return decorated


@tail_connect_bp.route('/rooms', methods=['POST'])
def create_room():
    """创建接尾游戏房间"""
    data = request.get_json() or {}
    
    difficulty = data.get('difficulty', 'medium')
    max_players = min(data.get('max_players', 8), Config.GAME_MAX_PLAYERS)
    
    # 生成房间信息
    room_id = str(uuid.uuid4())
    room_code = str(random.randint(100000, 999999))
    
    # 随机选择起始字
    start_char = random.choice(['月', '花', '春', '秋', '风', '雨', '山', '水', '云', '鸟'])
    
    # 初始化游戏状态
    state = {
        'room_id': room_id,
        'code': room_code,
        'difficulty': difficulty,
        'max_players': max_players,
        'start_char': start_char,
        'host_token': str(uuid.uuid4()),
        'members': [],
        'status': 'waiting',
        'current_char': start_char,
        'current_player_id': None,
        'round_no': 0,
        'used_lines': [],
        'used_chars': [start_char],
        'player_scores': {},
        'created_at': datetime.now().isoformat()
    }
    
    _game_states[room_id] = state
    _member_tokens[room_id] = {}
    
    return jsonify({
        'data': {
            'room_id': room_id,
            'code': room_code,
            'start_char': start_char,
            'difficulty': difficulty,
            'max_players': max_players,
            'my_user_id': state['host_token'],  # 简化：用 token 作为 user_id
            'host_user_id': state['host_token']
        }
    })


@tail_connect_bp.route('/rooms/<room_id>', methods=['GET'])
def get_room(room_id):
    """获取房间信息"""
    state = _game_states.get(room_id)
    if not state:
        return jsonify({'error': 'ROOM_NOT_FOUND'}), 404
    
    # 获取请求者 token
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    
    return jsonify({
        'data': {
            'room_id': state['room_id'],
            'code': state['code'],
            'status': state['status'],
            'start_char': state['start_char'],
            'current_char': state['current_char'],
            'difficulty': state['difficulty'],
            'max_players': state['max_players'],
            'members': [
                {
                    'user_id': m['token'],
                    'nickname': m['nickname'],
                    'score': state['player_scores'].get(m['token'], 0),
                    'is_host': m['token'] == state['host_token']
                }
                for m in state['members']
            ],
            'host_user_id': state['host_token']
        }
    })


@tail_connect_bp.route('/rooms/<room_id>/join', methods=['POST'])
def join_room(room_id):
    """加入房间"""
    state = _game_states.get(room_id)
    if not state:
        return jsonify({'error': 'ROOM_NOT_FOUND'}), 404
    
    data = request.get_json() or {}
    code = data.get('code')
    
    # 验证房间码
    if code and code != state['code']:
        return jsonify({'error': 'INVALID_CODE'}), 400
    
    # 检查是否已满
    if len(state['members']) >= state['max_players']:
        return jsonify({'error': 'ROOM_FULL'}), 400
    
    # 生成成员 token
    member_token = str(uuid.uuid4())
    nickname = data.get('nickname', f'雅客{len(state["members"]) + 1}')
    
    member = {
        'token': member_token,
        'nickname': nickname,
        'joined_at': datetime.now().isoformat()
    }
    
    state['members'].append(member)
    state['player_scores'][member_token] = 0
    _member_tokens[room_id][member_token] = member_token
    
    return jsonify({
        'data': {
            'room_id': room_id,
            'code': state['code'],
            'my_user_id': member_token,
            'host_user_id': state['host_token'],
            'members': [
                {
                    'user_id': m['token'],
                    'nickname': m['nickname'],
                    'is_host': m['token'] == state['host_token']
                }
                for m in state['members']
            ]
        }
    })


@tail_connect_bp.route('/rooms/<room_id>/start', methods=['POST'])
def start_game(room_id):
    """开始游戏"""
    state = _game_states.get(room_id)
    if not state:
        return jsonify({'error': 'ROOM_NOT_FOUND'}), 404
    
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    
    # 验证房主
    if token != state['host_token']:
        return jsonify({'error': 'NOT_HOST'}), 403
    
    # 检查人数
    if len(state['members']) < Config.GAME_MIN_PLAYERS:
        return jsonify({'error': 'MIN_PLAYERS_NOT_MET'}), 400
    
    # 开始游戏
    state['status'] = 'playing'
    state['current_player_id'] = state['members'][0]['token']
    state['round_no'] = 1
    
    return jsonify({
        'data': {
            'status': 'playing',
            'current_char': state['current_char'],
            'current_player_id': state['current_player_id'],
            'round_no': state['round_no'],
            'message': f'游戏开始！请用包含「{state["current_char"]}」字的诗句接龙'
        }
    })


@tail_connect_bp.route('/rooms/<room_id>/submit', methods=['POST'])
def submit_answer(room_id):
    """提交答案"""
    state = _game_states.get(room_id)
    if not state:
        return jsonify({'error': 'ROOM_NOT_FOUND'}), 404
    
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    data = request.get_json() or {}
    
    answer = data.get('answer', '').strip()
    if not answer:
        return jsonify({'error': 'EMPTY_ANSWER'}), 400
    
    # 检查是否是当前玩家
    if token != state['current_player_id']:
        return jsonify({
            'error': 'NOT_YOUR_TURN',
            'message': '还没轮到你哦',
            'current_player_id': state['current_player_id']
        }), 400
    
    # 清理答案
    import re
    clean_answer = re.sub(r'[，。！？；：""''【】（）、…—]', '', answer)
    
    # 验证是否包含关键字
    if state['current_char'] not in clean_answer:
        return jsonify({
            'result': 'INVALID',
            'message': f'诗句需要包含「{state["current_char"]}」字'
        })
    
    # 检查是否已使用
    if clean_answer in state['used_lines']:
        return jsonify({
            'result': 'DUPLICATE',
            'message': '这句诗已经用过了'
        })
    
    # 提取尾字
    tail_char = _get_tail_char(clean_answer)
    
    if not tail_char:
        return jsonify({
            'result': 'INVALID',
            'message': '无法识别诗句尾字'
        })
    
    # 更新状态
    state['used_lines'].append(clean_answer)
    state['player_scores'][token] = state['player_scores'].get(token, 0) + 15
    
    # 更新当前字
    state['used_chars'].append(tail_char)
    state['current_char'] = tail_char
    
    # 轮转到下一玩家
    current_idx = next(i for i, m in enumerate(state['members']) if m['token'] == token)
    next_idx = (current_idx + 1) % len(state['members'])
    state['current_player_id'] = state['members'][next_idx]['token']
    state['round_no'] += 1
    
    return jsonify({
        'data': {
            'result': 'VALID',
            'score_delta': 15,
            'total_score': state['player_scores'][token],
            'tail_char': tail_char,
            'next_char': state['current_char'],
            'next_player_id': state['current_player_id'],
            'message': f'正确！+15分，下一句需要包含「{state["current_char"]}」'
        }
    })


def _get_tail_char(line: str) -> str:
    """获取诗句尾字"""
    import re
    clean = re.sub(r'[，。！？；：""''【】（）、…—]', '', line.strip())
    
    if len(clean) < 2:
        return ''
    
    # 返回最后一个汉字
    for i in range(len(clean) - 1, -1, -1):
        char = clean[i]
        if '\u4e00' <= char <= '\u9fff':
            return char
    
    return ''


@tail_connect_bp.route('/rooms/<room_id>/used-lines', methods=['GET'])
def get_used_lines(room_id):
    """获取已用诗句"""
    state = _game_states.get(room_id)
    if not state:
        return jsonify({'error': 'ROOM_NOT_FOUND'}), 404
    
    return jsonify({
        'data': {
            'used_lines': state['used_lines'],
            'used_chars': state['used_chars']
        }
    })
