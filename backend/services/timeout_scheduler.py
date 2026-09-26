"""
超时调度器 - 事件驱动方案
替代旧的每2秒全表轮询，改用 threading.Timer 精确调度

用法: from services.timeout_scheduler import schedule_timeout, cancel_timeout
"""
import threading
import time as _time_module
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from flask_socketio import SocketIO
    from sqlalchemy.orm import Session
    from models import Room, RoomMember, GameTurn

# 全局定时器表：turn_id -> threading.Timer
_timeout_timers: dict = {}
_timer_lock = threading.Lock()

# 全局引用（由 app.py 注入）
_socketio: 'SocketIO' = None
_get_session = None
_Room = None
_RoomMember = None
_GameTurn = None
_RoomStatus = None
finish_game_func = None
start_turn_func = None
get_current_time_cn = None


def init_scheduler(socketio, get_session, models, funcs):
    """由 app.py 调用，注入依赖"""
    global _socketio, _get_session, _Room, _RoomMember, _GameTurn, _RoomStatus
    global finish_game_func, start_turn_func, get_current_time_cn
    _socketio = socketio
    _get_session = get_session
    _Room = models['Room']
    _RoomMember = models['RoomMember']
    _GameTurn = models['GameTurn']
    _RoomStatus = models['RoomStatus']
    finish_game_func = funcs['finish_game']
    start_turn_func = funcs['start_turn']
    get_current_time_cn = funcs['get_current_time_cn']


def schedule_timeout(room_id: str, turn_id: str, deadline_at: datetime):
    """为指定回合调度超时检测定时器"""
    delay = (deadline_at - get_current_time_cn()).total_seconds()
    if delay <= 0:
        delay = 0.1  # 已过期，0.1秒后立即触发

    def _on_timeout():
        """定时器回调：处理超时"""
        try:
            db = _get_session()
            try:
                turn = db.query(_GameTurn).filter_by(id=turn_id).first()
                if not turn or turn.status != 'pending':
                    return  # 已处理过，跳过

                room = db.query(_Room).filter_by(id=room_id).first()
                if not room or room.status != _RoomStatus.PLAYING:
                    return
                if room.current_player_id != turn.player_id:
                    return

                member = db.query(_RoomMember).filter(
                    _RoomMember.room_id == room_id,
                    _RoomMember.user_id == turn.player_id
                ).first()

                if member and member.is_alive:
                    member.is_alive = False
                    member.eliminated_at = datetime.now()
                    member.eliminate_reason = 'TIMEOUT'
                    turn.status = 'timeout'
                    db.commit()

                    _socketio.emit('player:eliminated', {
                        'room_id': room_id,
                        'user_id': turn.player_id,
                        'reason': '回答超时'
                    }, room=room_id)

                    alive_count = db.query(_RoomMember).filter(
                        _RoomMember.room_id == room_id,
                        _RoomMember.is_alive == True
                    ).count()

                    if alive_count <= 1:
                        finish_game_func(room_id, db)
                    else:
                        start_turn_func(room_id, db)
            finally:
                _get_session.remove()
        except Exception as e:
            print(f'Timeout handler error: {e}')

    with _timer_lock:
        if turn_id in _timeout_timers:
            _timeout_timers[turn_id].cancel()
        timer = _time_module.Timer(delay, _on_timeout)
        _timeout_timers[turn_id] = timer
        timer.start()


def cancel_timeout(turn_id: str):
    """取消某个回合的超时定时器（玩家已回答时调用）"""
    with _timer_lock:
        if turn_id in _timeout_timers:
            _timeout_timers[turn_id].cancel()
            del _timeout_timers[turn_id]
