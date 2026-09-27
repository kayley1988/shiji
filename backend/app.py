"""
诗语雅集 - App.Py
自动生成自 app.py
"""
# 本文件由 _split_app.py 自动生成，请勿手动编辑主逻辑部分

"""诗语雅集 - Flask 应用入口"""
import json
import logging
import os
import secrets
from datetime import datetime, timedelta, timezone
from functools import wraps

from flask import Flask, request, jsonify, g
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room
from sqlalchemy import create_engine, func, text
from sqlalchemy.orm import sessionmaker, scoped_session

from config import Config, IMAGERY_GROUPS, FEIHUALING_KEYWORDS, POET_CARDS
from models import (
    Base, User, UserSession, Room, RoomMember, GameTurn, 
    AnswerSubmission, AnswerResult, RoomUsedLine, GameResult,
    RoomStatus, GameMode, Poem, PoemLine, PoemLineTag, PoemLineAlias,
    Tag, SolarTerm, SolarTermKeyword, DailyTheme,
    UserFavorite, UserPoemUnlock, AuditEvent, ReviewStatus,
    Badge, UserBadge,
    init_db
)
from data.solar_terms import get_current_solar_term, SOLAR_TERMS
from data.poems import INITIAL_POEMS
from nlp.char_convert import to_simplified
from services.utils import get_today_date_cn

# Flask 应用
app = Flask(__name__)
app.config.from_object(Config)

# CORS - 使用配置文件中的来源限制
CORS(app, resources={r"/api/*": {"origins": Config.CORS_ORIGINS}}, supports_credentials=True)

# 数据库
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI, echo=Config.SQLALCHEMY_ECHO)
Session = scoped_session(sessionmaker(bind=engine))


def get_db():
    """全局数据库会话获取函数（多处路由依赖）"""
    return Session()

# Socket.IO
socketio = SocketIO(app, cors_allowed_origins=Config.CORS_ORIGINS, async_mode='eventlet')


# ============ 注册新路由 ============
# 接尾飞花令
from routes.tail_connect import tail_connect_bp
app.register_blueprint(tail_connect_bp, url_prefix='/v1/tail-connect')

# 诗词
from routes.poems import poems_bp
app.register_blueprint(poems_bp, url_prefix='/v1/poems')

# 认证
from routes.auth import auth_bp
app.register_blueprint(auth_bp, url_prefix='/v1/auth')

# 诗人
from routes.poet import poet_bp
app.register_blueprint(poet_bp, url_prefix='/v1/poet')

# 单人飞花令练习
from routes.solo import solo_bp
app.register_blueprint(solo_bp, url_prefix='/v1/solo')

# 诗词生成器（AI 自由生成）
from routes.poetry_generator import poetry_bp
app.register_blueprint(poetry_bp, url_prefix='/v1/poetry')

# 藏书阁
from routes.library import library_bp
app.register_blueprint(library_bp, url_prefix='/v1/library')

# 用户中心
from routes.user import user_bp
app.register_blueprint(user_bp, url_prefix='/v1/me')

# 探索页
from routes.explore import explore_bp
app.register_blueprint(explore_bp, url_prefix='/v1/explore')

# 房间/对战
from routes.room import room_bp
app.register_blueprint(room_bp, url_prefix='/v1/rooms')


# ============ Socket.IO 事件 ============

connected_users = {}           # user_id -> sid
connected_users_reverse = {}    # sid -> user_id (反向查找，加速鉴权)

# ============ 全局认证中间件 ============

# 不需要认证的路径（白名单）
PUBLIC_PATHS = [
    '/api/v1/auth/anonymous',
    '/api/v1/auth/login', 
    '/api/v1/auth/register',
    '/v1/auth/anonymous',
    '/v1/auth/login',
    '/v1/auth/register',
    '/v1/poems/random',      # 随机诗词预览
    '/v1/poems/daily',       # 每日推荐
    '/v1/library/dynasties', # 朝代列表（公开）
    '/v1/library/stats',      # 统计（公开）
    '/v1/library/categories',  # 分类（公开）
    '/v1/library',           # 藏书阁全部公开
    '/v1/explore',           # 探索页（公开）
    '/v1/explore/daily',     # 每日推荐
    '/v1/explore/filters',   # 筛选条件
    '/v1/practice',          # 练习
    '/v1/practice/keywords', # 关键词
    '/v1/practice/lines',    # 诗句练习
    '/v1/practice/peek',    # 查看诗句
    '/v1/poet',             # 诗人
    '/v1/poet/cards',       # 诗人卡片
    '/v1/poem',             # 诗词
    '/v1/poem/ambient',     # 静心诗境
    '/v1/poem/fortune',     # 诗签筒
    '/v1/solo',             # 飞花令
    '/v1/solo/keywords',    # 飞花令关键词
    '/v1/solo/poems',       # 飞花令诗句
    '/v1/daily-theme',      # 每日主题
    '/v1/challenge',        # 题库闯关（公开）
    '/v1/galaxy',           # 诗云星图（公开）
    '/api/v1/galaxy',       # 诗云星图（公开）
    '/v1/badges',           # 徽章
    '/v1/me',              # 个人中心
    '/v1/rooms',            # 房间列表
    '/static',               # 静态文件
]

@app.before_request
def check_auth():
    """全局认证检查"""
    # AI 功能统一开关（最高优先级，设置页可关）
    _ai_gates = [
        ('/v1/ai/poem-explain', 'explain'), ('/api/v1/ai/poem-explain', 'explain'),
        ('/v1/poet/roundtable', 'roundtable'), ('/api/v1/poet/roundtable', 'roundtable'),
    ]
    for _prefix, _feat in _ai_gates:
        if request.path.startswith(_prefix) and not _ai_feature_enabled(_feat):
            return jsonify({'code': 403, 'message': f'AI 功能「{AI_FEATURES[_feat]}」已在设置中关闭'}), 403

    # 允许白名单路径
    if any(request.path.startswith(p) for p in PUBLIC_PATHS):
        return None
    
    # 检查 Authorization header
    auth_header = request.headers.get('Authorization', '')
    if auth_header.startswith('Bearer '):
        token = auth_header[7:]  # 去掉 "Bearer " 前缀
        if token:
            # Token 验证逻辑可以在这里添加
            # 目前简化处理：有有效 token 即可
            return None
    
    # 可选：对于简单请求，返回 JSON 错误而不是重定向
    if request.path.startswith('/api/') or request.path.startswith('/v1/'):
        return jsonify({'error': 'UNAUTHORIZED', 'message': '需要登录或提供有效的认证令牌'}), 401
    
    return None


def require_auth(f):
    """简单的认证装饰器（用于特定端点）"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'error': 'UNAUTHORIZED'}), 401
        return f(*args, **kwargs)
    return decorated


# ============ AI 服务统一设置（设置页管理）============
AI_SETTINGS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ai_settings.json')
AI_FEATURES = {'explain': 'AI 诗词解读', 'roundtable': '诗人圆桌'}


def _load_ai_settings():
    try:
        with open(AI_SETTINGS_FILE, encoding='utf-8') as f:
            data = json.load(f)
    except Exception:
        data = {}
    feats = {k: bool(data.get('features', {}).get(k, True)) for k in AI_FEATURES}
    return {'features': feats}


def _save_ai_settings(settings):
    with open(AI_SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(settings, f, ensure_ascii=False, indent=2)


def _ai_feature_enabled(feature):
    return _load_ai_settings()['features'].get(feature, True)


def _update_env_key(key_name, value):
    """更新 backend/.env 中的键（不存在则追加），并同步 os.environ"""
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
    lines = []
    if os.path.exists(env_path):
        with open(env_path, encoding='utf-8') as f:
            lines = f.read().splitlines()
    replaced = False
    for i, line in enumerate(lines):
        if line.strip().startswith(f'{key_name}=') or line.strip().startswith(f'# {key_name}='):
            lines[i] = f'{key_name}={value}'
            replaced = True
            break
    if not replaced:
        lines.append(f'{key_name}={value}')
    with open(env_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')
    os.environ[key_name] = value
    setattr(Config, key_name, value)


@app.route('/v1/ai/settings', methods=['GET', 'POST'])
@app.route('/api/v1/ai/settings', methods=['GET', 'POST'])
def ai_settings_route():
    """AI 服务统一设置：功能开关 + DeepSeek Key 管理（Key 只写不读）"""
    if request.method == 'GET':
        s = _load_ai_settings()
        return jsonify({'data': {
            'provider': 'DeepSeek',
            'key_configured': bool(os.environ.get('DEEPSEEK_API_KEY') or Config.DEEPSEEK_API_KEY),
            'features': s['features'],
            'feature_names': AI_FEATURES,
        }})

    # POST：需要登录态
    if not request.headers.get('Authorization', '').replace('Bearer ', ''):
        return jsonify({'error': 'UNAUTHORIZED', 'message': '需要登录'}), 401

    body = request.get_json(silent=True) or {}
    s = _load_ai_settings()

    if 'features' in body:
        for k, v in body['features'].items():
            if k in AI_FEATURES:
                s['features'][k] = bool(v)
        _save_ai_settings(s)

    key_msg = None
    new_key = (body.get('api_key') or '').strip()
    if new_key:
        if not new_key.startswith('sk-'):
            return jsonify({'code': 400, 'message': 'DeepSeek Key 格式不正确（应以 sk- 开头）'}), 400
        _update_env_key('DEEPSEEK_API_KEY', new_key)
        key_msg = 'DeepSeek Key 已更新'

    return jsonify({'data': {'features': s['features'], 'key_configured': True, 'message': key_msg or '设置已保存'}})


@socketio.on('connect')
def on_connect():
    print(f'Client connected: {request.sid}')


@socketio.on('disconnect')
def on_disconnect():
    print(f'Client disconnected: {request.sid}')
    # 清理连接状态
    user_id = connected_users_reverse.pop(request.sid, None)
    if user_id:
        connected_users.pop(user_id, None)


@socketio.on('room:subscribe')
def on_room_subscribe(data):
    """订阅房间"""
    room_id = data.get('room_id')
    token = data.get('member_token') or data.get('access_token')
    
    if not room_id:
        emit('system:error', {'code': 'VALIDATION_ERROR', 'message': '缺少房间ID'})
        return
    
    db = Session()
    try:
        # 验证成员
        member = db.query(RoomMember).filter(
            RoomMember.room_id == room_id,
            RoomMember.user_id.in_(
                db.query(UserSession.user_id).filter_by(id=token)
            )
        ).first()
        
        if not member:
            emit('system:error', {'code': 'NOT_ROOM_MEMBER', 'message': '不是房间成员'})
            return
        
        # 加入房间
        join_room(room_id)
        member.connection_state = 'online'
        db.commit()
        
        # 记录连接
        connected_users[member.user_id] = request.sid
        connected_users_reverse[request.sid] = member.user_id
        
        # 发送房间快照
        room = db.query(Room).filter_by(id=room_id).first()
        members = db.query(RoomMember, User).join(User).filter(
            RoomMember.room_id == room_id
        ).all()
        
        member_list = []
        for m, u in members:
            member_list.append({
                'id': m.id,
                'user_id': u.id,
                'nickname': u.nickname,
                'role': m.role,
                'is_alive': m.is_alive,
                'is_online': m.connection_state == 'online'
            })
        
        emit('room:snapshot', {
            'room': {
                'id': room.id,
                'code': room.code,
                'mode': room.mode.value,
                'status': room.status.value,
                'keywords': room.keywords,
                'time_limit_sec': room.time_limit_sec,
                'current_turn_no': room.current_turn_no,
                'current_player_id': room.current_player_id
            },
            'members': member_list,
            'self': {
                'user_id': member.user_id,
                'role': member.role
            }
        })
        
        # 通知其他人
        emit('room:member-changed', {
            'room_id': room_id,
            'action': 'online',
            'user': {'id': member.user_id}
        }, room=room_id, include_self=False)
        
    finally:
        Session.remove()


@socketio.on('room:start')
def on_room_start(data):
    """开始游戏（Socket.IO 版本）"""
    room_id = data.get('room_id')
    token = data.get('access_token')
    
    if not room_id:
        emit('system:error', {'code': 'VALIDATION_ERROR', 'message': '缺少房间ID'})
        return
    
    db = Session()
    try:
        # 验证用户
        session = db.query(UserSession).filter_by(id=token).first()
        if not session:
            emit('system:error', {'code': 'UNAUTHORIZED', 'message': '未授权'})
            return
        
        user_id = session.user_id
        room = db.query(Room).filter_by(id=room_id).first()
        
        # 验证房主
        if room.host_user_id != user_id:
            emit('system:error', {'code': 'NOT_HOST', 'message': '只有房主可以开始游戏'})
            return
        
        # 验证状态
        if room.status != RoomStatus.WAITING:
            emit('system:error', {'code': 'ROOM_STATE_CONFLICT', 'message': '房间状态不允许开始'})
            return
        
        # 验证人数
        alive_members = db.query(RoomMember).filter(
            RoomMember.room_id == room_id,
            RoomMember.is_alive == True
        ).all()
        
        if len(alive_members) < Config.GAME_MIN_PLAYERS:
            emit('system:error', {'code': 'MIN_PLAYERS_NOT_MET',
                                  'message': f'至少需要 {Config.GAME_MIN_PLAYERS} 名玩家'})
            return
        
        # 开始游戏
        import random
        random.shuffle(alive_members)
        for i, m in enumerate(alive_members):
            m.seat_no = i
        
        theme = db.query(DailyTheme).filter_by(date_cn=get_today_date_cn()).first()
        room.status = RoomStatus.PLAYING
        room.started_at = datetime.now()
        room.current_turn_no = 0  # start_turn() 会 +=1 得到真正的第1回合
        room.current_player_id = alive_members[0].user_id
        room.config_version = theme.config_version if theme else 'v1'
        db.commit()
        
        socketio.emit('game:started', {
            'room_id': room_id,
            'started_at': room.started_at.isoformat(),
            'keywords': room.keywords,
            'time_limit_sec': room.time_limit_sec,
            'members': [{'user_id': m.user_id, 'seat_no': m.seat_no} for m in alive_members]
        }, room=room_id)
        
        # 发送第一个回合
        start_turn(room_id, db)
        
    except Exception as e:
        print(f'Room start error: {e}')
        import traceback; traceback.print_exc()
        emit('system:error', {'code': 'INTERNAL_ERROR', 'message': '开始游戏时出错'})
    finally:
        Session.remove()


@socketio.on('answer:submit')
def on_answer_submit(data):
    """提交答案"""
    room_id = data.get('room_id')
    text = data.get('text', '').strip()
    
    if not room_id or not text:
        emit('system:error', {'code': 'VALIDATION_ERROR', 'message': '缺少参数'})
        return
    
    db = Session()
    try:
        # 从 connected_users 获取用户
        user_id = connected_users_reverse.get(request.sid)
        if not user_id:
            emit('system:error', {'code': 'UNAUTHORIZED', 'message': '未授权'})
            return
        
        # 判题（已接入 QuestionGenerator）
        result = judge_answer(room_id, user_id, text, db)
        process_answer_result(room_id, user_id, result, db)
    
    except Exception as e:
        print(f'Answer submit error: {e}')
        import traceback; traceback.print_exc()
        emit('system:error', {'code': 'INTERNAL_ERROR', 'message': '处理答案时出错'})
    finally:
        Session.remove()



# ============ 判题逻辑 ============

def judge_answer(room_id: str, user_id: str, text: str, db) -> dict:
    """判题核心逻辑"""
    from models import RoomMember, GameTurn, AnswerResult
    
    room = db.query(Room).filter_by(id=room_id).first()
    
    # 检查是否是当前玩家
    if room.current_player_id != user_id:
        return {
            'result': AnswerResult.NOT_YOUR_TURN,
            'score_delta': 0,
            'element_bonus': False,
            'matched_line': None,
            'reason': '不是当前玩家',
            'raw_text': text
        }
    
    # 检查回合
    current_turn = db.query(GameTurn).filter(
        GameTurn.room_id == room_id,
        GameTurn.status == 'pending'
    ).first()
    
    if not current_turn:
        return {
            'result': AnswerResult.LATE,
            'score_delta': 0,
            'element_bonus': False,
            'matched_line': None,
            'reason': '回合不存在',
            'raw_text': text
        }
    
    # 检查是否超时
    now = get_current_time_cn()
    if now > current_turn.deadline_at:
        current_turn.status = 'timeout'
        db.commit()
        return {
            'result': AnswerResult.LATE,
            'score_delta': 0,
            'element_bonus': False,
            'matched_line': None,
            'reason': '已超时',
            'raw_text': text
        }
    
    # 规范化输入
    normalized = normalize_text(text)
    
    # 获取关键词
    keywords = room.keywords
    
    # 检查是否包含关键词
    has_keyword = any(kw in normalized for kw in keywords)
    if not has_keyword:
        return {
            'result': AnswerResult.INVALID,
            'score_delta': 0,
            'element_bonus': False,
            'matched_line': None,
            'reason': f'答案需包含关键词：{"或".join(keywords)}',
            'raw_text': text
        }
    
    # 使用 QuestionGenerator 的高效判题逻辑
    from nlp.question_generator import QuestionGenerator
    
    # 获取已用诗句ID
    used_rows = db.query(RoomUsedLine.poem_line_id).filter(
        RoomUsedLine.room_id == room_id
    ).all()
    used_line_ids = {row[0] for row in used_rows}
    
    # 飞花令：只用第一个关键字判定（简化版）
    keyword = keywords[0]
    
    qg = QuestionGenerator(db)
    quiz_result = qg.judge_feihua(text, keyword, used_line_ids)
    
    if quiz_result.correct and quiz_result.matched_line_id:
        # 检查是否是重复
        if quiz_result.matched_line_id in used_line_ids:
            return {
                'result': AnswerResult.DUPLICATE,
                'score_delta': 0,
                'element_bonus': False,
                'matched_line': None,
                'reason': '这句诗已被人说过',
                'raw_text': text
            }
        
        # 五行加成检测
        element_bonus = False
        if room.mode == GameMode.SOLAR_TERM_ELEMENT:
            theme = db.query(DailyTheme).filter_by(date_cn=get_today_date_cn()).first()
            if theme:
                term = db.query(SolarTerm).filter_by(id=theme.solar_term_id).first()
                if term:
                    element_keywords = {
                        '木': ['木', '春', '青', '东', '风', '柳', '芽', '松', '草'],
                        '火': ['火', '夏', '赤', '南', '热', '日', '炎', '荷', '暑'],
                        '金': ['金', '秋', '白', '西', '月', '霜', '菊', '枫', '寒'],
                        '水': ['水', '冬', '黑', '北', '雪', '冰', '夜', '寒'],
                        '土': ['土', '中', '黄', '山', '土', '田', '石', '地']
                    }
                    if term.primary_element in element_keywords:
                        if any(kw in normalized for kw in element_keywords[term.primary_element]):
                            element_bonus = True
        
        score_delta = Config.SCORE_VALID_ANSWER * (
            Config.SCORE_ELEMENT_BONUS_MULTIPLIER if element_bonus else 1
        )
        
        # 从 reason 中提取诗名和作者
        reason = quiz_result.reason
        poem_title = ''
        poem_author = ''
        if '！' in reason:
            parts = reason.split('！')
            if len(parts) >= 2:
                source = parts[1].strip()
                if ' - ' in source:
                    poem_title, poem_author = source.rsplit(' - ', 1)
                else:
                    poem_title = source
        
        return {
            'result': AnswerResult.VALID,
            'score_delta': score_delta,
            'element_bonus': element_bonus,
            'matched_line': {
                'id': quiz_result.matched_line_id,
                'content': quiz_result.raw_text,
                'poem_title': poem_title,
                'poem_author': poem_author
            },
            'reason': reason + ('（五行加成）' if element_bonus else ''),
            'raw_text': text
        }
    
    # 判题失败
    return {
        'result': AnswerResult.PENDING_REVIEW if quiz_result.matched_line_id else AnswerResult.INVALID,
        'score_delta': 0,
        'element_bonus': False,
        'matched_line': None,
        'reason': quiz_result.reason,
        'raw_text': text
    }
    

def process_answer_result(room_id: str, user_id: str, result: dict, db):
    """处理答案结果"""
    from models import RoomMember, GameTurn, AnswerSubmission, RoomUsedLine, User
    
    room = db.query(Room).filter_by(id=room_id).first()
    member = db.query(RoomMember).filter(
        RoomMember.room_id == room_id,
        RoomMember.user_id == user_id
    ).first()
    
    current_turn = db.query(GameTurn).filter(
        GameTurn.room_id == room_id,
        GameTurn.status == 'pending'
    ).first()
    
    if not current_turn:
        return
    
    # 记录提交
    submission = AnswerSubmission(
        room_id=room_id,
        turn_id=current_turn.id,
        user_id=user_id,
        client_request_id=secrets.token_hex(8),
        raw_text=result.get('raw_text', ''),
        normalized_text=normalize_text(result.get('raw_text', '')),
        result=result['result'],
        matched_line_id=result.get('matched_line', {}).get('id') if result.get('matched_line') else None,
        reason=result['reason'],
        score_delta=result['score_delta'],
        element_bonus=result['element_bonus']
    )
    db.add(submission)
    db.flush()  # 确保 submission.id 已生成（RoomUsedLine 需要引用它）
    
    current_turn.status = 'answered'
    current_turn.submitted_at = datetime.now()

    # 取消该回合的超时定时器（玩家已回答，不再触发超时淘汰）
    _cancel_timeout(current_turn.id)
    
    if result['result'] in [AnswerResult.VALID, AnswerResult.PENDING_REVIEW]:
        if result['result'] == AnswerResult.VALID:
            if result.get('matched_line'):
                used_line = RoomUsedLine(
                    room_id=room_id,
                    poem_line_id=result['matched_line']['id'],
                    submission_id=submission.id
                )
                db.add(used_line)
                
                # 记录冷门诗句解锁
                line = db.query(PoemLine).filter_by(id=result['matched_line']['id']).first()
                if line and line.is_rare:
                    unlock = UserPoemUnlock(
                        user_id=user_id,
                        poem_line_id=line.id,
                        unlock_reason='CORRECT_ANSWER'
                    )
                    db.merge(unlock)
            
            # 更新用户
            user = db.query(User).filter_by(id=user_id).first()
            if user:
                user.exp += result['score_delta']
                user.total_correct += 1
            
            start_turn(room_id, db)
    
    elif result['result'] in [AnswerResult.DUPLICATE, AnswerResult.INVALID, 
                               AnswerResult.LATE, AnswerResult.PENDING_REVIEW]:
        member.is_alive = False
        member.eliminated_at = datetime.now()
        member.eliminate_reason = result['result'].value
        
        socketio.emit('player:eliminated', {
            'room_id': room_id,
            'user_id': user_id,
            'reason': result['reason'],
            'matched_line': result.get('matched_line')
        }, room=room_id)
        
        alive_count = db.query(RoomMember).filter(
            RoomMember.room_id == room_id,
            RoomMember.is_alive == True
        ).count()
        
        if alive_count <= 1:
            finish_game(room_id, db)
        else:
            start_turn(room_id, db)
    
    db.commit()
    
    socketio.emit('answer:result', {
        'turn_id': current_turn.id,
        'user_id': user_id,
        'result': result['result'].value,
        'score_delta': result['score_delta'],
        'element_bonus': result['element_bonus'],
        'matched_line': result.get('matched_line'),
        'reason': result['reason']
    }, room=room_id)


def start_turn(room_id: str, db):
    """开始一个回合"""
    room = db.query(Room).filter_by(id=room_id).first()
    
    alive_members = db.query(RoomMember).filter(
        RoomMember.room_id == room_id,
        RoomMember.is_alive == True
    ).order_by(RoomMember.seat_no).all()
    
    if len(alive_members) <= 1:
        finish_game(room_id, db)
        return
    
    current_idx = next(
        (i for i, m in enumerate(alive_members) if m.user_id == room.current_player_id),
        -1
    )
    next_idx = (current_idx + 1) % len(alive_members)
    next_player = alive_members[next_idx]
    
    room.current_turn_no += 1
    room.current_player_id = next_player.user_id
    db.commit()
    
    deadline = get_current_time_cn() + timedelta(seconds=room.time_limit_sec)
    turn = GameTurn(
        room_id=room_id,
        turn_no=room.current_turn_no,
        player_id=next_player.user_id,
        deadline_at=deadline,
        status='pending'
    )
    db.add(turn)
    db.commit()
    
    socketio.emit('turn:started', {
        'turn_id': turn.id,
        'turn_no': turn.turn_no,
        'player_id': next_player.user_id,
        'deadline_at': turn.deadline_at.isoformat(),
        'time_limit_sec': room.time_limit_sec
    }, room=room_id)

    # 调度精确超时定时器（替代旧的全表轮询）
    _schedule_timeout(room_id, turn.id, deadline)


def finish_game(room_id: str, db):
    """结束游戏"""
    room = db.query(Room).filter_by(id=room_id).first()
    room.status = RoomStatus.SETTLING
    room.finished_at = datetime.now()
    
    members = db.query(RoomMember, User).join(User).filter(
        RoomMember.room_id == room_id
    ).all()
    
    scores = {}
    for m, u in members:
        correct_count = db.query(AnswerSubmission).filter(
            AnswerSubmission.room_id == room_id,
            AnswerSubmission.user_id == u.id,
            AnswerSubmission.result == AnswerResult.VALID
        ).count()
        
        element_bonus_count = db.query(AnswerSubmission).filter(
            AnswerSubmission.room_id == room_id,
            AnswerSubmission.user_id == u.id,
            AnswerSubmission.result == AnswerResult.VALID,
            AnswerSubmission.element_bonus == True
        ).count()
        
        score = correct_count * Config.SCORE_VALID_ANSWER + \
                element_bonus_count * Config.SCORE_VALID_ANSWER
        
        scores[u.id] = {
            'score': score,
            'correct_count': correct_count,
            'element_bonus_count': element_bonus_count
        }
    
    sorted_members = sorted(members, key=lambda x: (
        scores.get(x[1].id, {}).get('score', 0),
        x[0].eliminated_at or datetime.max
    ), reverse=True)
    
    results = []
    for placement, (m, u) in enumerate(sorted_members, 1):
        score_data = scores.get(u.id, {'score': 0, 'correct_count': 0, 'element_bonus_count': 0})
        is_winner = placement == 1
        
        result = GameResult(
            room_id=room_id,
            user_id=u.id,
            placement=placement,
            score=score_data['score'],
            correct_count=score_data['correct_count'],
            element_bonus_count=score_data['element_bonus_count'],
            is_winner=is_winner
        )
        db.add(result)
        
        u.total_games += 1
        if is_winner:
            u.total_wins += 1
        u.total_correct += score_data['correct_count']
        
        _update_rank(u, db)
        
        # 检查并颁发徽章
        game_result = {
            'won': is_winner,
            'total_games': u.total_games,
            'total_wins': u.total_wins,
            'total_correct': u.total_correct,
            'correct': score_data['correct_count'],
            'placement': placement,
            'keyword_correct_counts': {},
        }
        try:
            awarded = check_and_award_badges(u.id, game_result, db)
            if awarded:
                socketio.emit('badge:earned', {
                    'user_id': u.id,
                    'badges': awarded,
                    'room_id': room_id,
                }, room=room_id)
                audit_log(db, 'badge_earned', entity_type='user', entity_id=u.id,
                          payload={'badges': [b['code'] for b in awarded]})
        except Exception as badge_err:
            print(f'徽章颁发失败: {badge_err}')
        
        results.append({
            'placement': placement,
            'user_id': u.id,
            'nickname': u.nickname,
            'score': score_data['score'],
            'is_winner': is_winner
        })
    
    room.status = RoomStatus.FINISHED
    db.commit()
    
    socketio.emit('game:finished', {
        'room_id': room_id,
        'finished_at': room.finished_at.isoformat(),
        'results': results
    }, room=room_id)
    
    audit_log(db, 'game_finish', entity_type='room', entity_id=room_id,
              payload={'placements': [r['placement'] for r in results]})


def _update_rank(user: User, db):
    """更新用户段位"""
    exp = user.exp
    
    if exp >= 10000:
        new_rank = '雅客'
    elif exp >= 5000:
        new_rank = '翰林'
    elif exp >= 2000:
        new_rank = '进士'
    elif exp >= 1000:
        new_rank = '举人'
    elif exp >= 300:
        new_rank = '秀才'
    else:
        new_rank = '萌新'
    
    if new_rank != user.rank:
        user.rank = new_rank
        audit_log(db, 'rank_up', actor_type='user', actor_id=user.id,
                  payload={'new_rank': new_rank, 'exp': exp})



# ============ 认证（简化版）============
@app.route('/api/v1/auth/anonymous', methods=['POST'])
@app.route('/v1/auth/anonymous', methods=['POST'])
def anonymous_login():
    """匿名登录（简化版）"""
    device_id = request.json.get('device_id') if request.json else None
    if not device_id:
        device_id = f"anon_{secrets.token_hex(8)}"
    
    db = Session()
    try:
        user = db.query(User).filter_by(device_id=device_id).first()
        if not user:
            user = User(device_id=device_id)
            db.add(user)
            db.commit()
        
        token = secrets.token_hex(16)
        return jsonify({
            'data': {
                'user_id': user.id,
                'nickname': user.nickname,
                'token': token,
                'is_new': True
            }
        })
    finally:
        Session.remove()


# ============ 启动 ============

def init_data():
    """初始化数据库和数据"""
    db = Session()
    try:
        Base.metadata.create_all(engine)
        
        existing = db.query(Tag).first()
        if existing:
            print("数据已存在，跳过初始化")
            return
        
        # 导入诗词
        for poem_data in INITIAL_POEMS:
            poem = Poem(
                title=poem_data['title'],
                author=poem_data['author'],
                dynasty=poem_data.get('dynasty', '唐'),
                source_name=poem_data.get('source', 'chinese-poetry'),
                license_name=poem_data.get('license', 'MIT'),
                distribution_allowed=True,
                review_status=ReviewStatus.APPROVED
            )
            db.add(poem)
            db.commit()
            
            for i, line_data in enumerate(poem_data['lines'], 1):
                line = PoemLine(
                    poem_id=poem.id,
                    line_no=i,
                    content=line_data['content'],
                    normalized_content=normalize_text(line_data['content']),
                    is_rare=line_data.get('is_rare', False),
                    review_status=ReviewStatus.APPROVED
                )
                db.add(line)
                db.commit()
                
                for tag_name in line_data.get('tags', []):
                    tag = db.query(Tag).filter_by(
                        type='scene',
                        normalized_name=tag_name
                    ).first()
                    
                    if not tag:
                        tag = Tag(
                            type='scene',
                            name=tag_name,
                            normalized_name=tag_name,
                            active=True
                        )
                        db.add(tag)
                        db.commit()
                    
                    line_tag = PoemLineTag(
                        poem_line_id=line.id,
                        tag_id=tag.id,
                        confidence=100
                    )
                    db.add(line_tag)
            db.commit()
        
        # 导入节气
        for term_data in SOLAR_TERMS:
            term = SolarTerm(
                name=term_data['name'],
                start_date=term_data['start_date'],
                end_date=term_data['end_date'],
                season=term_data['season'],
                primary_element=term_data['primary_element'],
                description=term_data['description'],
                config_version='v1',
                active=True
            )
            db.add(term)
            db.commit()
            
            for i, kw in enumerate(term_data['keywords']):
                keyword = SolarTermKeyword(
                    solar_term_id=term.id,
                    keyword=kw,
                    imagery=term_data.get('imagery', ''),
                    sort_order=i,
                    enabled=True
                )
                db.add(keyword)
            db.commit()
        
        print(f"初始化完成：{len(INITIAL_POEMS)} 首诗词，{len(SOLAR_TERMS)} 个节气")
    
    finally:
        Session.remove()


# ══════════════════════════════════════════════
#  徽章系统
# ══════════════════════════════════════════════

@app.route('/v1/badges', methods=['GET'])
@app.route('/api/v1/badges', methods=['GET'])
def get_badge_list():
    """获取所有徽章列表"""
    db = get_db()
    badges = db.query(Badge).all()
    return jsonify({
        'data': {
            'badges': [{
                'id': b.id,
                'code': b.code,
                'name': b.name,
                'description': b.description,
                'icon': b.icon,
                'category': b.category,
                'rarity': b.rarity,
                'condition_type': b.condition_type,
                'condition_value': b.condition_value,
            } for b in badges]
        }
    })


@app.route('/v1/users/<user_id>/badges', methods=['GET'])
@app.route('/api/v1/users/<user_id>/badges', methods=['GET'])
@require_auth
def get_user_badges(user_id):
    """获取用户已获得的徽章"""
    db = get_db()

    owned = db.query(UserBadge).filter_by(user_id=user_id).all()
    owned_ids = {ub.badge_id for ub in owned}

    all_badges = db.query(Badge).all()
    badges = []
    for b in all_badges:
        earned = db.query(UserBadge).filter_by(user_id=user_id, badge_id=b.id).first()
        badges.append({
            'id': b.id,
            'code': b.code,
            'name': b.name,
            'description': b.description,
            'icon': b.icon,
            'category': b.category,
            'rarity': b.rarity,
            'earned': earned is not None,
            'earned_at': earned.earned_at if earned else None,
        })

    total = db.query(UserBadge).filter_by(user_id=user_id).count()
    return jsonify({
        'data': {
            'total': total,
            'badges': badges,
        }
    })


def check_and_award_badges(user_id: str, game_result: dict, db=None):
    """
    对局结束后检查徽章条件，奖励符合条件的徽章
    game_result: {'won': bool, 'correct': int, 'total_games': int, 'total_wins': int, ...}
    """
    import uuid
    _db = db or get_db()
    awarded = []

    # 已拥有的徽章
    owned = {ub.badge_id for ub in _db.query(UserBadge).filter_by(user_id=user_id).all()}

    # 查所有未拥有的徽章
    unowned = _db.query(Badge).filter(~Badge.id.in_(owned)).all()

    for badge in unowned:
        earned = False

        if badge.condition_type == 'correct_count':
            earned = game_result.get('total_correct', 0) >= badge.condition_value

        elif badge.condition_type == 'games_total':
            earned = game_result.get('total_games', 0) >= badge.condition_value

        elif badge.condition_type == 'win_streak':
            # 简化版：连胜 >= condition_value
            earned = game_result.get('win_streak', 0) >= badge.condition_value

        elif badge.condition_type == 'keyword_master':
            # 特定关键字正确数 >= condition_value（通过 keyword_correct_counts 传入）
            kwd_correct = game_result.get('keyword_correct_counts', {})
            earned = kwd_correct.get(badge.code.split('_')[-1], 0) >= badge.condition_value

        elif badge.condition_type == 'first_blood':
            # 首次获胜 或 首次达成某成就
            if badge.code == 'FIRST_WIN':
                earned = game_result.get('won') and game_result.get('total_wins', 0) == 1
            elif badge.code == 'COME_BACK':
                earned = game_result.get('won') and game_result.get('came_back', False)
            else:
                earned = False

        if earned:
            ub = UserBadge(id=str(uuid.uuid4()), user_id=user_id, badge_id=badge.id)
            _db.add(ub)
            awarded.append({
                'id': badge.id,
                'code': badge.code,
                'name': badge.name,
                'icon': badge.icon,
                'rarity': badge.rarity,
            })

    if awarded:
        if db is None:
            _db.commit()
            print(f'用户 {user_id} 获得新徽章: {[b["name"] for b in awarded]}')
        else:
            print(f'用户 {user_id} 获得新徽章: {[b["name"] for b in awarded]}')

    return awarded


# ══════════════════════════════════════════════════════
# 练习 / Solo 模式
# ══════════════════════════════════════════════════════
@app.route('/v1/practice/keywords', methods=['GET'])
@app.route('/api/v1/practice/keywords', methods=['GET'])
def get_practice_keywords():
    """飞花令关键字池"""
    return jsonify({'data': {'keywords': FEIHUALING_KEYWORDS}})


@app.route('/v1/practice/peek', methods=['GET'])
@app.route('/api/v1/practice/peek', methods=['GET'])
def peek_practice_lines():
    """查看含某关键字的所有诗句（分页，供「查看」功能）"""
    db = get_db()
    keyword = (request.args.get('keyword') or '').strip()
    page = max(int(request.args.get('page', 1)), 1)
    page_size = min(int(request.args.get('page_size', 20)), 50)

    if not keyword:
        return jsonify({'data': {
            'keyword': keyword, 'page': page, 'page_size': page_size,
            'lines': [], 'has_more': False,
        }})

    offset = (page - 1) * page_size
    rows = db.execute(text('''
        SELECT pl.id, pl.content, pl.normalized_content,
               p.id as poem_id, p.title, p.author, p.dynasty
        FROM poem_lines pl
        JOIN poems p ON p.id = pl.poem_id
        WHERE p.review_status = 'APPROVED'
          AND pl.normalized_content LIKE :kw
          AND pl.content NOT LIKE '%・%'
          AND pl.content NOT LIKE '%/%'
          AND pl.content NOT LIKE '%【%'
        ORDER BY p.id DESC
        LIMIT :lim OFFSET :off
    '''), {'kw': f'%{keyword}%', 'lim': page_size, 'off': offset}).fetchall()

    lines = [{
        'id': r.id,
        'line': r.normalized_content,
        'original': r.content,
        'poem_title': r.title,
        'poem_author': r.author,
        'dynasty': r.dynasty,
    } for r in rows]

    return jsonify({'data': {
        'keyword': keyword,
        'page': page,
        'page_size': page_size,
        'lines': lines,
        'has_more': len(lines) == page_size,
    }})


@app.route('/v1/practice/lines', methods=['GET'])
@app.route('/api/v1/practice/lines', methods=['GET'])
def get_practice_lines():
    """获取练习诗句（按关键字过滤）"""
    db = get_db()
    keywords = request.args.getlist('keyword')
    limit = min(int(request.args.get('limit', 20)), 50)

    if not keywords:
        # 没传关键字则用今日节气关键字
        month_day = get_today_date_cn()[5:]
        term_info = get_current_solar_term(month_day)
        keywords = term_info.get('keywords', [])

    results = []
    for kw in keywords:
        rows = db.execute(text('''
            SELECT pl.id, pl.content, pl.normalized_content,
                   p.id as poem_id, p.title, p.author
            FROM poem_lines pl
            JOIN poems p ON p.id = pl.poem_id
            WHERE p.review_status = 'APPROVED'
              AND pl.normalized_content LIKE :kw
            ORDER BY RAND()
            LIMIT :lim
        '''), {'kw': f'%{kw}%', 'lim': limit}).fetchall()

        for row in rows:
            results.append({
                'id': row.id,
                'line': row.content,
                'normalized': row.normalized_content,
                'poem_id': row.poem_id,
                'poem_title': row.title,
                'poem_author': row.author,
                'keyword': kw,
            })

    # 打乱顺序
    import random
    random.shuffle(results)

    return jsonify({'data': {
        'lines': results[:limit],
        'keywords': keywords,
    }})


@app.route('/v1/practice/validate', methods=['POST'])
@app.route('/api/v1/practice/validate', methods=['POST'])
def validate_practice_answer():
    """飞花令 Solo 验证：用户输入的诗句是否在数据库中（且含关键字）"""
    data = request.json or {}
    user_line = (data.get('line') or '').strip()
    keyword = (data.get('keyword') or '').strip()

    if not user_line:
        return jsonify({'error': '请输入诗句'}), 400

    db = get_db()

    # 繁简统一：用户输入统一转简体；去空格后比对 normalized_content
    user_norm = user_line.replace(' ', '').replace('\u3000', '')
    user_simp = to_simplified(user_norm)
    kw_simp = to_simplified(keyword)

    # Step 1：精确匹配（简体归一化后）
    match_row = db.execute(text('''
        SELECT pl.id, pl.content, pl.normalized_content,
               p.id as poem_id, p.title, p.author, p.dynasty
        FROM poem_lines pl
        JOIN poems p ON p.id = pl.poem_id
        WHERE p.review_status = 'APPROVED'
          AND pl.normalized_content = :simp
          AND pl.normalized_content LIKE :kw
        LIMIT 1
    '''), {'simp': user_simp, 'kw': f'%{kw_simp}%'}).fetchone()

    # 兜底：库里 normalized_content 可能残留繁体，逐条 to_simplified 后比较
    if not match_row:
        candidates = db.execute(text('''
            SELECT pl.id, pl.content, pl.normalized_content,
                   p.id as poem_id, p.title, p.author, p.dynasty
            FROM poem_lines pl
            JOIN poems p ON p.id = pl.poem_id
            WHERE p.review_status = 'APPROVED'
              AND pl.normalized_content LIKE :kw
            LIMIT 2000
        '''), {'kw': f'%{kw_simp}%'}).fetchall()
        for c in candidates:
            if to_simplified(c.normalized_content).replace(' ', '').replace('\u3000', '') == user_simp:
                match_row = c
                break

    if match_row:
        # Step 2：获取该诗的完整诗句（按 line_no 排序）
        all_lines = db.execute(text('''
            SELECT content, normalized_content FROM poem_lines
            WHERE poem_id = :pid
            ORDER BY line_no
        '''), {'pid': match_row.poem_id}).fetchall()

        # 全诗用繁体原文展示；行号用简体 normalized_content 匹配用户输入
        poem_lines = [r.content for r in all_lines]
        try:
            line_order = next(i + 1 for i, r in enumerate(all_lines)
                              if r.normalized_content.replace(' ', '').replace('\u3000', '') == user_simp)
        except StopIteration:
            line_order = 1

        return jsonify({'data': {
            'correct': True,
            'line': match_row.normalized_content,
            'line_id': match_row.id,
            'poem_title': match_row.title,
            'poem_author': match_row.author,
            'poem_dynasty': match_row.dynasty,
            'poem_id': match_row.poem_id,
            'full_poem': poem_lines,
            'line_order': line_order,
        }})

    # 匹配失败：给出 3 条含该关键字的诗句提示
    hints = db.execute(text('''
        SELECT pl.normalized_content, p.title, p.author
        FROM poem_lines pl
        JOIN poems p ON p.id = pl.poem_id
        WHERE p.review_status = 'APPROVED'
          AND pl.normalized_content LIKE :kw
        ORDER BY RAND()
        LIMIT 3
    '''), {'kw': f'%{keyword}%'}).fetchall()

    return jsonify({'data': {
        'correct': False,
        'hint_lines': [{'line': r.normalized_content, 'title': r.title, 'author': r.author} for r in hints],
        'message': f'这句诗不在库中，或不含关键字「{keyword}」',
    }})


# ══════════════════════════════════════════════════════
# 诗词浏览 / 推荐
# ══════════════════════════════════════════════════════
@app.route('/v1/explore/daily', methods=['GET'])
@app.route('/api/v1/explore/daily', methods=['GET'])
def get_daily_recommend():
    """今日推荐：根据节气/节日智能推荐诗词"""
    db = get_db()
    month_day = get_today_date_cn()[5:]  # MM-DD
    term_info = get_current_solar_term(month_day)
    term_name = term_info['name']
    keywords = term_info.get('keywords', [])

    # 特殊节日映射（月-日 → 关键字）
    festival_map = {
        '01-01': '元日', '01-15': '元宵', '04-05': '清明', '05-05': '端午',
        '08-15': '明月', '09-09': '重阳', '12-30': '除夕',
    }
    festival_kw = festival_map.get(month_day, '')

    # 节气名本身也是一个强关键字
    all_kws = keywords + ([festival_kw] if festival_kw else []) + [term_name]

    results = []
    seen = set()
    for kw in all_kws:
        rows = db.execute(text('''
            SELECT p.id, p.title, p.author, p.dynasty, pl.content, pl.normalized_content
            FROM poem_lines pl
            JOIN poems p ON p.id = pl.poem_id
            WHERE p.review_status = 'APPROVED'
              AND pl.normalized_content LIKE :kw
              AND p.id NOT IN :seen_ids
            ORDER BY RAND()
            LIMIT 5
        '''), {'kw': f'%{kw}%', 'seen_ids': tuple(seen) if seen else ('__none__',)}).fetchall()

        for row in rows:
            seen.add(row.id)
            results.append({
                'poem_id': row.id,
                'title': row.title,
                'author': row.author,
                'dynasty': row.dynasty,
                'line': row.content,
                'keyword': kw,
                'reason': '节日' if kw == festival_kw else '节气',
            })

        if len(results) >= 20:
            break

    # 补足 8 首（不够就随机补）
    if len(results) < 8:
        extras = db.execute(text('''
            SELECT p.id, p.title, p.author, p.dynasty, pl.content
            FROM poem_lines pl
            JOIN poems p ON p.id = pl.poem_id
            WHERE p.review_status = 'APPROVED'
              AND p.id NOT IN :seen_ids
            ORDER BY RAND()
            LIMIT :lim
        '''), {'seen_ids': tuple(seen) if seen else ('__none__',), 'lim': 8 - len(results)}).fetchall()
        for row in extras:
            results.append({
                'poem_id': row.id,
                'title': row.title,
                'author': row.author,
                'dynasty': row.dynasty,
                'line': row.content,
                'keyword': '',
                'reason': '精选',
            })

    return jsonify({'data': {
        'term': term_name,
        'poems': results[:8],
    }})


@app.route('/v1/explore/poems', methods=['GET'])
@app.route('/api/v1/explore/poems', methods=['GET'])
def explore_poems():
    """诗词浏览：支持按朝代/意象/作者筛选"""
    db = get_db()
    dynasty  = request.args.get('dynasty')
    author   = request.args.get('author')
    tag_type = request.args.get('tag_type')
    tag_name = request.args.get('tag_name')
    page     = max(int(request.args.get('page', 1)), 1)
    page_size = min(int(request.args.get('page_size', 20)), 50)

    params: dict = {'lim': page_size, 'off': (page - 1) * page_size}
    where_clauses = ["p.review_status = 'APPROVED'"]

    if dynasty:
        where_clauses.append("p.dynasty = :dynasty")
        params['dynasty'] = dynasty
    if author:
        where_clauses.append("p.author LIKE CONCAT('%', :author, '%')")
        params['author'] = author

    where_sql = ' AND '.join(where_clauses)

    # 子查询处理标签筛选
    tag_sql = ''
    if tag_type and tag_name:
        tag_sql = '''
            AND p.id IN (
                SELECT DISTINCT plt.poem_line_id
                FROM poem_line_tags plt
                JOIN tags t ON t.id = plt.tag_id
                WHERE t.type = :tag_type AND t.normalized_name = :tag_name
            )
        '''
        params['tag_type'] = tag_type
        params['tag_name'] = tag_name.lower()

    # 直接 raw SQL 按 id 分页，避免 ORM distinct() 全表去重
    sql = text(f'''
        SELECT p.id, p.title, p.author, p.dynasty, p.created_at
        FROM poems p
        WHERE {where_sql} {tag_sql}
        ORDER BY p.id DESC
        LIMIT :lim OFFSET :off
    ''')

    rows = db.execute(sql, params).fetchall()
    if not rows:
        return jsonify({'data': {'poems': [], 'page': page, 'page_size': page_size}})

    poem_ids = [r.id for r in rows]
    # 批量取每首诗的第一句
    lines_rows = db.execute(text('''
        SELECT pl.poem_id, pl.content
        FROM poem_lines pl
        WHERE pl.id IN (
            SELECT MIN(id) FROM poem_lines
            WHERE poem_id IN :ids
            GROUP BY poem_id
        )
    '''), {'ids': tuple(poem_ids)}).fetchall()
    lines_map = {row.poem_id: row.content for row in lines_rows}

    def is_drama(title: str) -> bool:
        if not title:
            return False
        return '・' in title or '／' in title or '/' in title or '【' in title or '】' in title

    items = []
    for r in rows:
        if not is_drama(r.title):
            items.append({
                'id': r.id,
                'title': r.title,
                'author': r.author,
                'dynasty': r.dynasty,
                'preview': lines_map.get(r.id, ''),
            })

    # 如果过滤后为空，回退（防止默认全是戏曲的情况）
    if not items:
        items = [{
            'id': r.id,
            'title': r.title,
            'author': r.author,
            'dynasty': r.dynasty,
            'preview': lines_map.get(r.id, ''),
        } for r in rows]

    return jsonify({'data': {
        'poems': items,
        'page': page,
        'page_size': page_size,
    }})


@app.route('/v1/explore/filters', methods=['GET'])
@app.route('/api/v1/explore/filters', methods=['GET'])
def get_explore_filters():
    """获取浏览页筛选条件：朝代、意象标签"""
    db = get_db()

    # 已有朝代列表（按历史顺序）
    dynasty_order = ['先秦', '汉', '魏晋', '南北朝', '隋', '唐', '宋', '元', '明', '清']
    dynasties = db.execute(text('''
        SELECT DISTINCT dynasty FROM poems
        WHERE review_status = 'APPROVED' AND dynasty IS NOT NULL AND dynasty != ''
    ''')).fetchall()
    # Python 端按历史顺序排
    dynasty_names = [r.dynasty for r in dynasties]
    dynasty_names.sort(key=lambda x: dynasty_order.index(x) if x in dynasty_order else 99)

    # 意象标签：返回精选分组结构（过滤噪音，按类别归类）
    return jsonify({'data': {
        'dynasties': dynasty_names,
        'imagery_groups': IMAGERY_GROUPS,
        # 兼容旧字段：平铺所有精选意象
        'imagery': [item for g in IMAGERY_GROUPS for item in g['items']],
    }})


# ══════════════════════════════════════════════════════
# AI 诗歌解读接口
# ══════════════════════════════════════════════════════
@app.route('/v1/ai/poem-explain', methods=['POST'])
@app.route('/api/v1/ai/poem-explain', methods=['POST'])
def ai_poem_explain():
    """深度解读一首诗：5 大板块 + 作者生平时间轴 + 作品集"""
    data = request.get_json() or {}
    poem = data.get('poem', '')
    source = data.get('source', '')
    title = data.get('title', '')
    author = data.get('author', '')
    dynasty = data.get('dynasty', '')
    poem_id = data.get('poem_id', '')

    # 兜底：从 source 解析「标题 - 作者」
    if (not title or not author) and source:
        if ' - ' in source:
            try:
                title, author = source.rsplit(' - ', 1)
            except Exception:
                pass

    if not poem:
        return jsonify({'code': 400, 'message': '缺少 poem 参数'}), 400

    api_key = os.environ.get('DEEPSEEK_API_KEY') or Config.DEEPSEEK_API_KEY
    if not api_key:
        return jsonify({
            'code': 500, 'message': 'AI 服务未配置',
            'data': {'content': 'AI 解读服务正在配置中，请稍后再试。'}
        })

    # ── 作者作品集：从库中查该作者其他代表作（可点击跳转）──
    works = []
    try:
        db = get_db()
        if author:
            def _is_drama(t):
                if not t:
                    return False
                return any(c in t for c in ('・', '／', '/', '【', '】'))
            rows = db.execute(text('''
                SELECT p.id, p.title, p.author, p.dynasty
                FROM poems p
                WHERE p.author = :author AND p.review_status = 'APPROVED'
                ORDER BY RAND()
                LIMIT 200
            '''), {'author': author}).fetchall()
            seen = set()
            for r in rows:
                if _is_drama(r.title):
                    continue
                if poem_id and str(r.id) == str(poem_id):
                    continue
                if r.id in seen:
                    continue
                seen.add(r.id)
                works.append({
                    'id': r.id,
                    'title': r.title,
                    'author': r.author,
                    'dynasty': r.dynasty,
                })
                if len(works) >= 8:
                    break
    except Exception:
        works = []

    prompt = f"""你是一位精通中国古典诗词的学者，兼擅考据、鉴赏与文学批评。请对下面这首诗做一次深度、详实、有学术分量的解读，杜绝空泛套话。

【诗题】{title}
【作者】{author}（{dynasty}）
【全诗】
{poem}

请严格按以下 5 个板块输出，每块用「## 板块名」作为 Markdown 二级标题：

## 诗作时节与场景
明确指出本诗的时节、时间、地理环境与人物处境，必须引用诗中原句作为证据，说明判断依据，不要只给结论。

## 作者生平时间轴
按时间升序逐条列出与理解本诗相关的作者生平节点，每条格式为「- 公元年份 · 事件简述」；与本诗直接相关或作者一生转折点的条目，在末尾标注「【重点】」。至少列出 6 条。

## 创作背景
精确到大致年份，交代作者当时的年龄、官职、境遇与心境，以及触发创作的具体事件（如科举、贬谪、送别、纪游等），并说明这些背景如何反映在诗中。

## 分层诗文赏析
逐联（或逐句）赏析，每联先引用原句，再分「表层」与「深层」两层：表层解释字面意思，深层揭示意象、用典、情感递进与艺术手法。最后单独挑出全诗最精彩的一句作为「名句」，做一段深度鉴赏。

## 主旨与后世评价
提炼全诗核心主旨，并引述 1—2 条后世有代表性的评价（注明评论者或出处）。

要求：每个板块都要充实具体，赏析要有洞见；避免"情景交融""意境优美"这类空话；总篇幅不少于 800 字。"""

    try:
        import urllib.request
        req = urllib.request.Request(
            'https://api.deepseek.com/chat/completions',
            data=json.dumps({
                'model': 'deepseek-chat',
                'messages': [
                    {'role': 'system', 'content': '你是一位博古通今的中国古典文学学者，擅长诗词考据与深度鉴赏，行文严谨而富有文气。'},
                    {'role': 'user', 'content': prompt}
                ],
                'temperature': 0.7,
                'max_tokens': 2200,
            }).encode('utf-8'),
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {api_key}',
            },
            method='POST'
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read().decode('utf-8'))
        content = result['choices'][0]['message']['content']
        return jsonify({'code': 200, 'data': {
            'content': content,
            'author': author,
            'works': works,
        }})
    except Exception as e:
        return jsonify({
            'code': 500, 'message': str(e),
            'data': {'content': f'解读生成失败：{str(e)}', 'works': works}
        })


# ══════════════════════════════════════════════════════
# 诗人雅集（角色卡 + 角色扮演对话）
# ══════════════════════════════════════════════════════
@app.route('/v1/poet/cards', methods=['GET'])
@app.route('/api/v1/poet/cards', methods=['GET'])
def poet_cards():
    """返回诗人角色卡展示信息（不含人设 prompt）"""
    cards = []
    for c in POET_CARDS:
        cards.append({
            'id': c['id'],
            'name': c['name'],
            'dynasty': c['dynasty'],
            'title': c['title'],
            'avatar': c['avatar'],
            'first_message': c['first_message'],
            'masterpieces': c['masterpieces'],
            'voice': c['voice'],
        })
    return jsonify({'code': 200, 'data': {'cards': cards}})


def _search_poet_refs(author, messages):
    """检索该作者与当前话题相关的真实诗句，供 AI 引用（RAG）"""
    import re
    last_user = ''
    for m in reversed(messages):
        if m.get('role') == 'user' and m.get('content'):
            last_user = m['content']
            break
    if not last_user:
        return ''

    simp = to_simplified(last_user)
    words = re.findall(r'[\u4e00-\u9fff]{2,}', simp)
    stop = {'什么', '哪里', '怎么', '为何', '如何', '是否', '请问', '先生', '诗人',
            '一首', '你的', '这首', '那首', '为什么', '能不能', '可以', '是哪首',
            '最喜欢', '喜欢', '得意', '爱喝', '爱读', '说说', '跟我', '聊聊'}
    keywords = []
    seen = set()
    for w in words:
        if w in stop or w in seen:
            continue
        seen.add(w)
        keywords.append(w)
    keywords = keywords[:6]

    try:
        db = get_db()
        if keywords:
            conds = ' OR '.join([f'pl.normalized_content LIKE :k{i}' for i in range(len(keywords))])
            params = {'author': author}
            for i, k in enumerate(keywords):
                params[f'k{i}'] = f'%{k}%'
            sql = f'''
                SELECT p.title, pl.content
                FROM poem_lines pl
                JOIN poems p ON p.id = pl.poem_id
                WHERE p.author = :author
                  AND p.review_status = 'APPROVED'
                  AND ({conds})
                ORDER BY RAND()
                LIMIT 6
            '''
        else:
            params = {'author': author}
            sql = '''
                SELECT p.title, pl.content
                FROM poem_lines pl
                JOIN poems p ON p.id = pl.poem_id
                WHERE p.author = :author
                  AND p.review_status = 'APPROVED'
                ORDER BY RAND()
                LIMIT 6
            '''
        rows = db.execute(text(sql), params).fetchall()
        lines = []
        for r in rows:
            lines.append(f'《{r.title}》：「{r.content}」')
        return '\n'.join(lines)
    except Exception:
        return ''


@app.route('/v1/poet/chat', methods=['POST'])
@app.route('/api/v1/poet/chat', methods=['POST'])
def poet_chat():
    """与诗人角色卡对话（DeepSeek 角色扮演）"""
    data = request.get_json() or {}
    poet_id = data.get('poet_id', '')
    messages = data.get('messages', [])

    if not poet_id or not messages:
        return jsonify({'code': 400, 'message': '缺少 poet_id 或 messages'}), 400

    card = next((c for c in POET_CARDS if c['id'] == poet_id), None)
    if not card:
        return jsonify({'code': 404, 'message': '未找到该诗人'}), 404

    api_key = os.environ.get('DEEPSEEK_API_KEY') or Config.DEEPSEEK_API_KEY
    if not api_key:
        return jsonify({'code': 500, 'message': 'AI 服务未配置',
                        'data': {'reply': 'AI 服务正在配置中，请稍后再试。'}})

    # ── RAG：检索该作者真实诗句，注入系统提示 ──
    refs = _search_poet_refs(card['name'], messages)
    system_content = card['persona']
    if refs:
        system_content += (
            '\n\n【可引用的真实诗作素材】以下是' + card['name'] +
            '本人的真实诗句，回复中如需引用诗句，请优先从这些素材中选原句，'
            '不要编造或杜撰不存在于素材中的诗句：\n' + refs
        )

    # 构造消息：system 人设 + 最近历史
    chat_messages = [{'role': 'system', 'content': system_content}]
    recent = messages[-20:]
    for m in recent:
        role = m.get('role', 'user')
        content = m.get('content', '')
        if role not in ('user', 'assistant'):
            role = 'user'
        if content:
            chat_messages.append({'role': role, 'content': content})

    try:
        import urllib.request
        req = urllib.request.Request(
            'https://api.deepseek.com/chat/completions',
            data=json.dumps({
                'model': 'deepseek-chat',
                'messages': chat_messages,
                'temperature': 0.9,
                'max_tokens': 600,
            }).encode('utf-8'),
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {api_key}',
            },
            method='POST'
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read().decode('utf-8'))
        reply = result['choices'][0]['message']['content']
        return jsonify({'code': 200, 'data': {'reply': reply}})
    except Exception as e:
        return jsonify({
            'code': 500, 'message': str(e),
            'data': {'reply': f'诗人暂不在线：{str(e)}'}
        })


def _deepseek_reply(chat_messages, api_key, max_tokens=600, temperature=0.9):
    """调用 DeepSeek chat completions，返回回复文本"""
    import urllib.request
    req = urllib.request.Request(
        'https://api.deepseek.com/chat/completions',
        data=json.dumps({
            'model': 'deepseek-chat',
            'messages': chat_messages,
            'temperature': temperature,
            'max_tokens': max_tokens,
        }).encode('utf-8'),
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}',
        },
        method='POST'
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        result = json.loads(resp.read().decode('utf-8'))
    return result['choices'][0]['message']['content']


@app.route('/v1/poet/roundtable', methods=['POST'])
@app.route('/api/v1/poet/roundtable', methods=['POST'])
def poet_roundtable():
    """多位诗人同席对谈：按顺序依次发言，后者可见前者发言"""
    data = request.get_json() or {}
    poet_ids = data.get('poet_ids', [])
    topic = (data.get('topic') or '').strip()
    rounds = int(data.get('rounds', 1))

    if not isinstance(poet_ids, list) or len(poet_ids) < 2:
        return jsonify({'code': 400, 'message': '至少需要两位诗人'}), 400

    cards = [c for c in POET_CARDS if c['id'] in poet_ids]
    if len(cards) < 2:
        return jsonify({'code': 404, 'message': '未找到足够的诗人'}), 404
    cards = sorted(cards, key=lambda c: poet_ids.index(c['id']))

    api_key = os.environ.get('DEEPSEEK_API_KEY') or Config.DEEPSEEK_API_KEY
    if not api_key:
        return jsonify({'code': 500, 'message': 'AI 服务未配置'}), 500

    transcript = []       # 已产生的发言：{'name', 'content'}
    history = data.get('history', [])
    if isinstance(history, list):
        for h in history:
            name = h.get('poet_name') or h.get('name') or '诗友'
            content = h.get('content', '')
            if content:
                transcript.append({'name': name, 'content': content})

    result_messages = []  # 返回给前端

    try:
        for _ in range(rounds):
            for card in cards:
                # RAG：基于话题 + 已有发言，检索该作者真实诗句
                search_text = (topic + ' ' + ' '.join(t['content'] for t in transcript)).strip()
                refs = ''
                if search_text:
                    refs = _search_poet_refs(card['name'], [{'role': 'user', 'content': search_text}])
                system_content = card['persona']
                if refs:
                    system_content += (
                        '\n\n【可引用的真实诗作素材】以下是' + card['name'] +
                        '本人的真实诗句，发言中如需引用诗句，请优先从这些素材中选原句，'
                        '不要编造或杜撰不存在于素材中的诗句：\n' + refs
                    )

                chat_messages = [{'role': 'system', 'content': system_content}]
                if topic:
                    chat_messages.append({
                        'role': 'user',
                        'content': '今日诗友雅集，众人围坐共谈一个话题，请你以「' + card['name'] +
                                   '」的身份发表自己的见解（若前面已有人发言，请针对他们的观点回应、补充或反驳，'
                                   '保持各自性情与交情）。话题是：' + topic,
                    })
                for t in transcript:
                    chat_messages.append({
                        'role': 'user',
                        'content': '【' + t['name'] + '】' + t['content'],
                    })

                reply = (_deepseek_reply(chat_messages, api_key, max_tokens=400) or '').strip()
                if not reply:
                    reply = '（' + card['name'] + ' 抚须沉吟，未发一言。）'
                transcript.append({'name': card['name'], 'content': reply})
                result_messages.append({
                    'poet_id': card['id'],
                    'poet_name': card['name'],
                    'avatar': card['avatar'],
                    'dynasty': card['dynasty'],
                    'voice': card['voice'],
                    'content': reply,
                })

        return jsonify({'code': 200, 'data': {'topic': topic, 'messages': result_messages}})
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e),
                        'data': {'topic': topic, 'messages': result_messages}})


@app.route('/v1/poet/feihualing', methods=['POST'])
@app.route('/api/v1/poet/feihualing', methods=['POST'])
def poet_feihualing():
    """诗人飞花令：轮流接含令字的真实诗句（RAG 保证真实，AI 只生成引介语）"""
    data = request.get_json() or {}
    poet_ids = data.get('poet_ids', [])
    keyword = (data.get('keyword') or '').strip()
    exclude_lines = set(data.get('exclude_lines', []) or [])

    if not isinstance(poet_ids, list) or len(poet_ids) < 2:
        return jsonify({'code': 400, 'message': '至少需要两位诗人'}), 400
    if not keyword or len(keyword) != 1:
        return jsonify({'code': 400, 'message': '令字需为单个汉字'}), 400

    cards = [c for c in POET_CARDS if c['id'] in poet_ids]
    if len(cards) < 2:
        return jsonify({'code': 404, 'message': '未找到足够的诗人'}), 404
    cards = sorted(cards, key=lambda c: poet_ids.index(c['id']))

    api_key = os.environ.get('DEEPSEEK_API_KEY') or Config.DEEPSEEK_API_KEY
    if not api_key:
        return jsonify({'code': 500, 'message': 'AI 服务未配置'}), 500

    result_messages = []

    def _pick_line(author):
        """检索该作者含令字的真实诗句，优先未用过"""
        try:
            db = get_db()
            rows = db.execute(text('''
                SELECT p.title, pl.content
                FROM poem_lines pl
                JOIN poems p ON p.id = pl.poem_id
                WHERE p.author = :author
                  AND p.review_status = 'APPROVED'
                  AND pl.normalized_content LIKE :kw
                ORDER BY RAND()
                LIMIT 10
            '''), {'author': author, 'kw': f'%{keyword}%'}).fetchall()
            for r in rows:
                key = f'{r.title}|{r.content}'
                if key not in exclude_lines:
                    return r.title, r.content
            if rows:
                return rows[0].title, rows[0].content
        except Exception:
            pass
        return None, None

    try:
        for card in cards:
            title, line = _pick_line(card['name'])
            if not line:
                comment = f'（{card["name"]} 捻须沉吟，一时竟想不起含「{keyword}」的句子。）'
                result_messages.append({
                    'poet_id': card['id'], 'poet_name': card['name'],
                    'avatar': card['avatar'], 'dynasty': card['dynasty'],
                    'voice': card['voice'], 'line': '', 'title': '', 'comment': comment,
                })
                continue

            system_content = card['persona'] + (
                '\n\n你现在正在行飞花令，令字是「' + keyword + '」。'
                '请用一两句话以你的口吻引出下面这句你自己的诗，'
                '要自然、有韵味，但【不要重复或改写这句诗本身】，诗句会单独展示。'
                f'\n诗句：{line}\n出自：《{title}》'
            )
            chat_messages = [{'role': 'system', 'content': system_content}]
            chat_messages.append({'role': 'user', 'content': '轮到你行令了，请引出你的诗句。'})
            comment = (_deepseek_reply(chat_messages, api_key, max_tokens=120, temperature=0.9) or '').strip()
            if not comment:
                comment = f'{card["name"]} 起身吟道——'

            exclude_lines.add(f'{title}|{line}')
            result_messages.append({
                'poet_id': card['id'], 'poet_name': card['name'],
                'avatar': card['avatar'], 'dynasty': card['dynasty'],
                'voice': card['voice'], 'line': line, 'title': title, 'comment': comment,
            })

        return jsonify({'code': 200, 'data': {'keyword': keyword, 'messages': result_messages}})
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e),
                        'data': {'keyword': keyword, 'messages': result_messages}})



# ============ 每日主题 ============
def _get_daily_theme_data() -> dict:
    """今日主题数据（节气 + 意象关键字），供 /v1/daily-theme 与静心诗境等共用"""
    today = get_today_date_cn()
    st = get_current_solar_term(today[5:])  # MM-DD
    return {
        'date': today,
        'solar_term': {
            'name': st['name'],
            'season': st.get('season', ''),
            'primary_element': st.get('primary_element', ''),
            'description': st.get('description', ''),
            'imagery': st.get('imagery', ''),
        },
        'keywords': st.get('keywords', []),
    }


@app.route('/v1/daily-theme', methods=['GET'])
@app.route('/api/v1/daily-theme', methods=['GET'])
def get_daily_theme_api():
    """每日主题（节气 + 关键字）"""
    try:
        return jsonify({'code': 200, 'data': _get_daily_theme_data()})
    except Exception as e:
        logging.error(f"daily-theme error: {e}", exc_info=True)
        return jsonify({'code': 500, 'message': '获取每日主题失败'}), 500


# ============ 静心诗境 ============
@app.route('/v1/poem/ambient', methods=['GET'])
@app.route('/api/v1/poem/ambient', methods=['GET'])
def get_ambient_poem():
    """静心诗境：取今日推荐诗，适合沉浸式慢读"""
    db = get_db()
    try:
        today = get_today_date_cn()
        theme_data = _get_daily_theme_data()
        
        # 随机取一首今日意象相关的诗
        kw = theme_data.get('keywords', [])
        mood_kw = kw[0] if kw else '月'
        
        row = db.execute(text('''
            SELECT p.id, p.title, p.author, p.dynasty,
                   GROUP_CONCAT(pl.content ORDER BY pl.line_no) as lines
            FROM poems p
            JOIN poem_lines pl ON pl.poem_id = p.id
            LEFT JOIN poem_line_tags plt ON plt.poem_line_id = pl.id
            LEFT JOIN tags t ON t.id = plt.tag_id
            WHERE p.review_status = 'APPROVED'
              AND p.category != '戏曲'
              AND (t.name = :kw OR pl.normalized_content LIKE :pat)
            GROUP BY p.id
            ORDER BY RAND()
            LIMIT 1
        '''), {'kw': mood_kw, 'pat': f'%{mood_kw}%'}).fetchone()
        
        if not row:
            # 回退：直接随机取
            row = db.execute(text('''
                SELECT p.id, p.title, p.author, p.dynasty,
                       GROUP_CONCAT(pl.content ORDER BY pl.line_no) as lines
                FROM poems p
                JOIN poem_lines pl ON pl.poem_id = p.id
                WHERE p.review_status = 'APPROVED' AND p.category != '戏曲'
                GROUP BY p.id
                ORDER BY RAND()
                LIMIT 1
            ''')).fetchone()
        
        poem_lines = row.lines.split(',') if row else []
        # 取前 4 句（适合静心）
        display_lines = poem_lines[:4]
        
        # AI 生成一段意境简介（沉浸式引导语）
        try:
            from config import Config
            api_key = Config.DEEPSEEK_API_KEY
            system_prompt = (
                '你是诗语雅集的「静心引读师」。用户请求一段诗境引导语，'
                '用于沉浸式冥想场景。请用 1-2 句话，以舒缓、温柔的语气描绘这首诗的意境，'
                '像在对一个需要安静陪伴的人轻声说话。回复要简短（不超过 40 字），有意境，不评判。'
            )
            user_prompt = f'请为这首诗写一段静心引导语。诗题：《{row.title}》。诗句：{" / ".join(poem_lines[:4])}'
            resp = _deepseek_reply(
                [{'role': 'system', 'content': system_prompt},
                 {'role': 'user', 'content': user_prompt}],
                api_key, max_tokens=80, temperature=0.8
            )
            intro = resp.strip() if resp else '静下心来，听诗。'
        except Exception:
            intro = '静下心来，听诗。'
        
        return jsonify({'code': 200, 'data': {
            'poem_id': row.id,
            'title': row.title,
            'author': row.author,
            'dynasty': row.dynasty,
            'lines': display_lines,
            'intro': intro,
            'solar_term': theme_data.get('solar_term', {}).get('name', ''),
        }})
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e), 'data': None})
    finally:
        db.close()



# ============ 诗签筒 ============
@app.route('/v1/poem/fortune', methods=['GET'])
@app.route('/api/v1/poem/fortune', methods=['GET'])
def get_poem_fortune():
    """诗签筒：按心情取随机诗句"""
    db = get_db()
    try:
        mood = request.args.get('mood', '平静')
        
        # 心情 -> 意象关键词映射
        mood_map = {
            '欢喜': ['春风', '桃花', '芳草', '莺', '蝶', '鹊', '红', '新'],
            '忧愁': ['秋', '月', '雁', '落叶', '孤灯', '长亭', '雨', '白发'],
            '平静': ['山', '云', '松', '竹', '清泉', '禅', '静', '闲'],
            '迷茫': ['江', '烟', '路', '舟', '雾', '关', '远', '梦'],
        }
        keywords = mood_map.get(mood, ['月', '山', '云'])
        kw = keywords[0]
        
        row = db.execute(text('''
            SELECT p.id, p.title, p.author, p.dynasty,
                   pl.content as line,
                   (SELECT GROUP_CONCAT(t2.name) FROM poem_line_tags plt2
                    JOIN tags t2 ON t2.id = plt2.tag_id
                    WHERE plt2.poem_line_id = pl.id) as tags
            FROM poems p
            JOIN poem_lines pl ON pl.poem_id = p.id
            WHERE p.review_status = 'APPROVED'
              AND p.category != '戏曲'
              AND pl.normalized_content LIKE :pat
            ORDER BY RAND()
            LIMIT 1
        '''), {'pat': f'%{kw}%'}).fetchone()
        
        if not row:
            row = db.execute(text('''
                SELECT p.id, p.title, p.author, p.dynasty,
                       pl.content as line, '' as tags
                FROM poems p
                JOIN poem_lines pl ON pl.poem_id = p.id
                WHERE p.review_status = 'APPROVED' AND p.category != '戏曲'
                ORDER BY RAND()
                LIMIT 1
            ''')).fetchone()
        
        return jsonify({'code': 200, 'data': {
            'poem_id': row.id,
            'title': row.title,
            'author': row.author,
            'dynasty': row.dynasty,
            'line': row.line,
            'tags': row.tags or '',
            'mood': mood,
        }})
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e), 'data': None})
    finally:
        db.close()



# ============ 私人诗摘 ============
@app.route('/v1/poem/notes', methods=['GET'])
@app.route('/api/v1/poem/notes', methods=['GET'])
@require_auth
def get_poem_notes():
    """获取当前用户的诗摘列表"""
    db = get_db()
    try:
        user = g.user
        notes = db.execute(text('''
            SELECT id, poem_id, line_text, poem_title, poet_name, note, mood_tag, created_at, updated_at
            FROM poem_notes
            WHERE user_id = :uid
            ORDER BY created_at DESC
            LIMIT 100
        '''), {'uid': user.id}).fetchall()
        
        return jsonify({'code': 200, 'data': {
            'notes': [_note_dict(n) for n in notes]
        }})
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e), 'data': {'notes': []}})
    finally:
        db.close()


@app.route('/v1/poem/notes', methods=['POST'])
@app.route('/api/v1/poem/notes', methods=['POST'])
@require_auth
def create_poem_note():
    """新增诗摘"""
    db = get_db()
    try:
        user = g.user
        data = request.get_json() or {}
        import uuid
        note_id = str(uuid.uuid4())
        
        db.execute(text('''
            INSERT INTO poem_notes (id, user_id, poem_id, line_text, poem_title, poet_name, note, mood_tag)
            VALUES (:id, :uid, :pid, :line, :title, :poet, :note, :mood)
        '''), {
            'id': note_id,
            'uid': user.id,
            'pid': data.get('poem_id', ''),
            'line': data.get('line_text', ''),
            'title': data.get('poem_title', ''),
            'poet': data.get('poet_name', ''),
            'note': data.get('note', ''),
            'mood': data.get('mood_tag', ''),
        })
        db.commit()
        
        row = db.execute(text('SELECT * FROM poem_notes WHERE id = :id'), {'id': note_id}).fetchone()
        return jsonify({'code': 200, 'data': _note_dict(row)})
    except Exception as e:
        db.rollback()
        return jsonify({'code': 500, 'message': str(e), 'data': None})
    finally:
        db.close()


@app.route('/v1/poem/notes/<note_id>', methods=['PUT'])
@app.route('/api/v1/poem/notes/<note_id>', methods=['PUT'])
@require_auth
def update_poem_note(note_id):
    """更新诗摘"""
    db = get_db()
    try:
        user = g.user
        row = db.execute(text('''
            SELECT * FROM poem_notes WHERE id = :id AND user_id = :uid
        '''), {'id': note_id, 'uid': user.id}).fetchone()
        
        if not row:
            return jsonify({'code': 404, 'message': '未找到', 'data': None})
        
        data = request.get_json() or {}
        db.execute(text('''
            UPDATE poem_notes
            SET note = :note, mood_tag = :mood_tag, updated_at = NOW()
            WHERE id = :id AND user_id = :uid
        '''), {
            'note': data.get('note', row.note),
            'mood_tag': data.get('mood_tag', row.mood_tag),
            'id': note_id,
            'uid': user.id,
        })
        db.commit()
        
        updated = db.execute(text('SELECT * FROM poem_notes WHERE id = :id'), {'id': note_id}).fetchone()
        return jsonify({'code': 200, 'data': _note_dict(updated)})
    except Exception as e:
        db.rollback()
        return jsonify({'code': 500, 'message': str(e), 'data': None})
    finally:
        db.close()


@app.route('/v1/poem/notes/<note_id>', methods=['DELETE'])
@app.route('/api/v1/poem/notes/<note_id>', methods=['DELETE'])
@require_auth
def delete_poem_note(note_id):
    """删除诗摘"""
    db = get_db()
    try:
        user = g.user
        db.execute(text('''
            DELETE FROM poem_notes WHERE id = :id AND user_id = :uid
        '''), {'id': note_id, 'uid': user.id})
        db.commit()
        return jsonify({'code': 200, 'data': {'id': note_id}})
    except Exception as e:
        db.rollback()
        return jsonify({'code': 500, 'message': str(e), 'data': None})
    finally:
        db.close()


def _note_dict(row):
    """诗摘行转字典"""
    if hasattr(row, '_mapping'):
        m = dict(row._mapping)
    else:
        m = {c.name: getattr(row, c.name) for c in row.__table__.columns}
    return {
        'id': m['id'],
        'poem_id': m['poem_id'],
        'line_text': m['line_text'],
        'poem_title': m['poem_title'],
        'poet_name': m['poet_name'],
        'note': m['note'] or '',
        'mood_tag': m['mood_tag'] or '',
        'created_at': str(m['created_at']) if m.get('created_at') else '',
        'updated_at': str(m['updated_at']) if m.get('updated_at') else '',
    }


# ============ 全局错误处理 ============

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'NOT_FOUND', 'message': '请求的资源不存在'}), 404

@app.errorhandler(500)
def internal_error(e):
    logging.error(f"Internal server error: {str(e)}")
    return jsonify({'error': 'INTERNAL_ERROR', 'message': '服务器内部错误'}), 500

@app.errorhandler(Exception)
def handle_exception(e):
    """捕获所有未处理的异常"""
    logging.error(f"Unhandled exception: {str(e)}", exc_info=True)
    return jsonify({'error': 'SERVER_ERROR', 'message': '请求处理失败'}), 500


# ============ 题库闯关（数据库版，745k 已审核诗句）============

import random as _random
from functools import lru_cache as _lru
from sqlalchemy import text as _sqltext

# 派系 → 诗人映射
CHALLENGE_FACTIONS = {
    'shanshui':  {'name': '山水田园', 'poets': ['王维', '孟浩然', '柳宗元']},
    'biansai':   {'name': '边塞征战', 'poets': ['王昌龄', '王之涣', '王翰']},
    'langman':   {'name': '浪漫豪放', 'poets': ['李白', '贺知章']},
    'chenyu':    {'name': '沉郁现实', 'poets': ['杜甫', '李绅', '张继']},
    'yongshi':   {'name': '咏史抒怀', 'poets': ['杜牧', '李商隐', '骆宾王']},
}

challenge_sessions = {}   # session_id -> {'questions': [...]}


@_lru(maxsize=1)
def _db_author_map():
    """简体作者名 -> 库中原始写法集合（处理繁体：王維→王维）"""
    db = Session()
    rows = db.execute(_sqltext("SELECT DISTINCT author FROM poems")).fetchall()
    db.close()
    m = {}
    for (a,) in rows:
        if a:
            m.setdefault(to_simplified(a), set()).add(a)
    return m


def _resolve_poets(names):
    """把简体诗人名解析成库中的原始写法列表"""
    amap = _db_author_map()
    out = []
    for n in names:
        out.extend(amap.get(n, []))
    return out


@_lru(maxsize=1)
def _db_form_counts():
    """诗歌形式分布（行数 → 诗数），进程内缓存"""
    db = Session()
    rows = db.execute(_sqltext(
        "SELECT cnt, COUNT(*) FROM (SELECT poem_id, COUNT(*) cnt FROM poem_lines GROUP BY poem_id) GROUP BY cnt"
    )).fetchall()
    db.close()
    return dict(rows)


# ---------- 诗云星图（3D Galaxy） ----------

@_lru(maxsize=1)
def _galaxy_poets_payload():
    """全库作者聚合：作者 / 朝代 / 作品数（名气），进程内缓存"""
    db = Session()
    try:
        rows = db.execute(_sqltext(
            "SELECT author, dynasty, COUNT(*) c FROM poems "
            "WHERE author IS NOT NULL AND author != '' "
            "GROUP BY author, dynasty ORDER BY c DESC")).fetchall()
    finally:
        db.close()
    poets = []
    for a, d, c in rows:
        poets.append({'id': a, 'name': to_simplified(a), 'dynasty': d or '未知', 'count': c})
    return poets


@app.route('/api/v1/galaxy/poets', methods=['GET'])
@app.route('/v1/galaxy/poets', methods=['GET'])
def galaxy_poets():
    """星图全量诗人（前端做坐标/大小映射）"""
    poets = _galaxy_poets_payload()
    db = Session()
    try:
        total = db.execute(_sqltext("SELECT COUNT(*) FROM poems")).scalar()
    finally:
        db.close()
    return jsonify({'data': {'poets': poets, 'total_poets': len(poets), 'total_poems': total}})


@app.route('/api/v1/galaxy/poems', methods=['GET'])
@app.route('/v1/galaxy/poems', methods=['GET'])
def galaxy_author_poems():
    """点星取某位作者的代表作（最多 5 首，各取前 4 句）"""
    name = (request.args.get('author') or '').strip()
    if not name:
        return jsonify({'error': 'MISSING_AUTHOR', 'message': '缺少 author 参数'}), 400
    db = Session()
    try:
        rows = db.execute(_sqltext(
            "SELECT id, title FROM poems WHERE author = :a ORDER BY title LIMIT 5"),
            {'a': name}).fetchall()
        if not rows:
            for raw in _resolve_poets([name]):
                rows = db.execute(_sqltext(
                    "SELECT id, title FROM poems WHERE author = :a ORDER BY title LIMIT 5"),
                    {'a': raw}).fetchall()
                if rows:
                    break
        out = []
        for pid, title in rows:
            lines = db.execute(_sqltext(
                "SELECT content FROM poem_lines WHERE poem_id = :pid AND review_status = 'APPROVED' "
                "ORDER BY line_no LIMIT 4"), {'pid': pid}).fetchall()
            out.append({'id': pid, 'title': to_simplified(title),
                        'lines': [to_simplified(l[0]) for l in lines]})
        return jsonify({'data': {'author': to_simplified(name), 'poems': out}})
    finally:
        db.close()


@app.route('/v1/challenge/dimensions', methods=['GET'])
def challenge_dimensions():
    """题库维度：朝代 / 派系 / 主题意象 / 诗歌形式（实时查库）"""
    db = Session()
    try:
        dynasties = [{'id': r[0], 'name': r[0], 'desc': f'{r[0]}诗', 'count': r[1]}
                     for r in db.execute(_sqltext(
            "SELECT dynasty, COUNT(*) FROM poems WHERE dynasty IS NOT NULL AND dynasty != '' "
            "GROUP BY dynasty ORDER BY COUNT(*) DESC")).fetchall()]

        # 派系：只保留库中真实存在的诗人（自动处理繁简体）
        factions = []
        for fid, info in CHALLENGE_FACTIONS.items():
            found = sorted(_resolve_poets(info['poets']))
            if found:
                factions.append({'id': fid, 'name': info['name'],
                                 'poets': [to_simplified(p) for p in found]})

        themes = [{'id': r[0], 'name': r[0]} for r in db.execute(_sqltext(
            "SELECT t.name, COUNT(*) c FROM poem_line_tags plt "
            "JOIN tags t ON t.id = plt.tag_id WHERE t.type = 'scene' "
            "GROUP BY t.name ORDER BY c DESC LIMIT 12")).fetchall()]

        counts = _db_form_counts()
        forms = []
        for size, label in ((4, '绝句'), (8, '律诗')):
            if counts.get(size):
                forms.append({'id': label, 'name': label, 'count': counts[size]})
        return jsonify({'data': {
            'dynasties': dynasties, 'factions': factions,
            'themes': themes, 'forms': forms,
        }})
    finally:
        db.close()


def _db_filter_sql(dynasty=None, faction=None, theme=None, form=None):
    """构造按维度过滤 poems 的 WHERE 子句与参数"""
    where, params = [], {}
    if dynasty:
        where.append("p.dynasty = :dynasty")
        params['dynasty'] = dynasty
    if faction:
        poets = _resolve_poets(CHALLENGE_FACTIONS.get(faction, {}).get('poets', []))
        if poets:
            ph = ','.join(':fp%d' % i for i in range(len(poets)))
            where.append(f"p.author IN ({ph})")
            params.update({'fp%d' % i: p for i, p in enumerate(poets)})
    if theme:
        where.append(
            "EXISTS (SELECT 1 FROM poem_lines pl JOIN poem_line_tags plt ON plt.poem_line_id = pl.id "
            "JOIN tags t ON t.id = plt.tag_id WHERE pl.poem_id = p.id AND t.name = :theme)")
        params['theme'] = theme
    if form:
        size = {'绝句': 4, '律诗': 8}.get(form)
        if size:
            where.append("(SELECT COUNT(*) FROM poem_lines pl3 WHERE pl3.poem_id = p.id) = :nlines")
            params['nlines'] = size
    return where, params


def _db_fetch_lines(db, poem_id):
    return [r[1] for r in db.execute(_sqltext(
        "SELECT line_no, content FROM poem_lines WHERE poem_id = :pid AND review_status = 'APPROVED' "
        "ORDER BY CAST(line_no AS INTEGER)"), {'pid': poem_id}).fetchall()]


def _db_gen_question(db, poem_row, distractor_pool, title_pool):
    """一道题：随机取诗的一句（非末句考下一句，末句考出处）"""
    pid, title, author, dynasty = poem_row
    lines = _db_fetch_lines(db, pid)
    if len(lines) < 2:
        return None
    s_title, s_author = to_simplified(title), to_simplified(author)
    own = [to_simplified(l) for l in lines]

    idx = _random.randrange(len(lines) - 1) if len(lines) > 2 and _random.random() < 0.8 else len(lines) - 1
    if idx < len(lines) - 1:
        answer = own[idx + 1]
        q_text = f"「{own[idx]}」，下一句是？"
        cands = [c for c in distractor_pool
                 if c != answer and c not in own and abs(len(c) - len(answer)) <= 3]
    else:
        answer = s_title
        q_text = f"「{own[idx]}」出自哪首诗？"
        cands = [t for t in title_pool if t != s_title]

    if len(cands) < 3:
        return None
    options = _random.sample(cands, 3) + [answer]
    _random.shuffle(options)
    return {
        'poem_id': pid,
        'line_id': f"{pid}-{idx}",
        'question': q_text,
        'title': s_title,
        'author': s_author,
        'dynasty': dynasty,
        'options': options,
        'answer': answer,
    }


@app.route('/v1/challenge/start', methods=['POST'])
def challenge_start():
    """开始闯关：从数据库按维度抽题"""
    payload = request.get_json(silent=True) or {}
    try:
        count = min(int(payload.get('count', 10) or 10), 20)
    except (TypeError, ValueError):
        count = 10

    db = Session()
    try:
        where, params = _db_filter_sql(
            dynasty=payload.get('dynasty'),
            faction=payload.get('faction'),
            theme=payload.get('theme'),
            form=payload.get('form'),
        )
        wsql = (" WHERE " + " AND ".join(where)) if where else ""
        base = f"FROM poems p{wsql}"
        total = db.execute(_sqltext(f"SELECT COUNT(*) {base}"), params).scalar()
        if not total:
            return jsonify({'error': 'NO_POEMS', 'message': '该维度下暂无诗句，请换个维度试试'}), 404

        # 抽诗（随机采样，数量冗余 3 倍以过滤单行诗）
        fetch_n = min(count * 3, total)
        rows = db.execute(_sqltext(
            f"SELECT p.id, p.title, p.author, p.dynasty {base} ORDER BY RANDOM() LIMIT :n"),
            {**params, 'n': fetch_n}).fetchall()

        # 干扰项池：随机诗句 + 随机诗题（简体化后使用）
        raw_lines = [to_simplified(r[0]) for r in db.execute(_sqltext(
            "SELECT content FROM poem_lines WHERE review_status = 'APPROVED' "
            "AND LENGTH(content) BETWEEN 3 AND 20 ORDER BY RANDOM() LIMIT 400")).fetchall()]
        raw_titles = [to_simplified(r[0]) for r in db.execute(_sqltext(
            "SELECT title FROM poems ORDER BY RANDOM() LIMIT 200")).fetchall()]

        questions = []
        for row in rows:
            if len(questions) >= count:
                break
            q = _db_gen_question(db, row, raw_lines, raw_titles)
            if q:
                questions.append(q)

        if not questions:
            return jsonify({'error': 'NO_POEMS', 'message': '该维度下暂时出不了题，请换个维度试试'}), 404

        session_id = secrets.token_hex(16)
        challenge_sessions[session_id] = {'questions': questions}
        return jsonify({'data': {'session_id': session_id, 'questions': questions}})
    finally:
        db.close()


@app.route('/v1/challenge/submit', methods=['POST'])
def challenge_submit():
    """提交闯关：服务端判分（不信任前端答案）"""
    payload = request.get_json(silent=True) or {}
    sid = payload.get('session_id')
    session = challenge_sessions.pop(sid, None)
    if not session:
        return jsonify({'error': 'SESSION_NOT_FOUND', 'message': '会话已过期，请重新开始'}), 404

    answers = {a.get('line_id'): a.get('answer') for a in payload.get('answers', [])}
    results, correct = [], 0
    for q in session['questions']:
        ua = answers.get(q['line_id'])
        ok = ua == q['answer']
        if ok:
            correct += 1
        results.append({
            'line_id': q['line_id'],
            'title': q['title'],
            'author': q['author'],
            'question': q['question'],
            'user_answer': ua,
            'correct_answer': q['answer'],
            'correct': ok,
        })
    total = len(session['questions'])
    score = correct * 10
    exp_gain = correct * 5
    return jsonify({'data': {
        'total': total, 'correct': correct,
        'score': score, 'exp_gain': exp_gain, 'results': results,
    }})


# ============ 启动 ============

if __name__ == '__main__':
    init_data()
    print("=" * 50)
    print("诗语雅集服务启动中...")
    print(f"CORS允许的来源: {Config.CORS_ORIGINS}")
    print("=" * 50)
    print("API: http://localhost:5000/")
    # 使用标准 Flask 服务器 (Werkzeug) 避免 eventlet 问题
    import os as _os
    app.run(host='0.0.0.0', port=int(_os.environ.get('PORT', 5000)), debug=False)