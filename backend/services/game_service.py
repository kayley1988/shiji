"""
游戏核心服务 - 统一的游戏状态管理
"""
import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


class GameType(Enum):
    """游戏类型"""
    FEIHUALING = "feihualing"           # 传统飞花令（单字令）
    TAIL_CONNECT = "tail_connect"       # 接尾飞花令
    SOLAR_TERM = "solar_term"          # 节气五行飞花令


class GamePhase(Enum):
    """游戏阶段"""
    WAITING = "waiting"      # 等待开始
    STARTING = "starting"    # 即将开始
    PLAYING = "playing"      # 进行中
    ROUND_END = "round_end"  # 回合结束
    FINISHED = "finished"    # 游戏结束


@dataclass
class PlayerState:
    """玩家状态"""
    user_id: str
    nickname: str
    score: int = 0
    correct_count: int = 0
    streak: int = 0          # 连续答对
    max_streak: int = 0
    is_alive: bool = True
    eliminated_at: Optional[datetime] = None
    eliminate_reason: Optional[str] = None


@dataclass
class TurnState:
    """回合状态"""
    turn_id: str
    round_no: int
    player_id: str
    keyword: str
    start_time: datetime
    deadline: datetime
    submissions: List[Dict] = field(default_factory=list)
    result: Optional[str] = None  # PLAYING, VALID, INVALID, DUPLICATE, TIMEOUT


@dataclass
class GameState:
    """游戏状态"""
    room_id: str
    game_type: GameType
    phase: GamePhase
    keywords: List[str]
    current_keyword: str
    
    players: Dict[str, PlayerState] = field(default_factory=dict)
    current_turn: Optional[TurnState] = None
    turn_history: List[Dict] = field(default_factory=list)
    used_lines: List[str] = field(default_factory=list)
    
    config: Dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'room_id': self.room_id,
            'game_type': self.game_type.value,
            'phase': self.phase.value,
            'keywords': self.keywords,
            'current_keyword': self.current_keyword,
            'players': {
                uid: {
                    'user_id': p.user_id,
                    'nickname': p.nickname,
                    'score': p.score,
                    'correct_count': p.correct_count,
                    'streak': p.streak,
                    'is_alive': p.is_alive
                }
                for uid, p in self.players.items()
            },
            'current_turn': {
                'turn_id': t.turn_id,
                'round_no': t.round_no,
                'player_id': t.player_id,
                'keyword': t.keyword,
                'deadline': t.deadline.isoformat() if t.deadline else None
            } if self.current_turn else None,
            'created_at': self.created_at.isoformat(),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'finished_at': self.finished_at.isoformat() if self.finished_at else None
        }


class GameService:
    """
    游戏核心服务
    
    职责：
    1. 管理游戏状态
    2. 处理回合逻辑
    3. 计分和排名
    4. 广播事件
    """
    
    def __init__(self):
        self._games: Dict[str, GameState] = {}
        self._room_to_game: Dict[str, str] = {}  # room_id -> game_id
    
    def create_game(self, room_id: str, game_type: GameType,
                   keywords: List[str], players: List[Dict],
                   config: Dict = None) -> GameState:
        """
        创建游戏
        
        Args:
            room_id: 房间ID
            game_type: 游戏类型
            keywords: 关键词列表
            players: 玩家列表 [{user_id, nickname}]
            config: 游戏配置
        """
        import uuid
        
        game_id = str(uuid.uuid4())
        
        # 初始化玩家
        player_states = {
            p['user_id']: PlayerState(
                user_id=p['user_id'],
                nickname=p['nickname']
            )
            for p in players
        }
        
        # 选择第一个关键词
        current_keyword = keywords[0] if keywords else '月'
        
        # 创建游戏状态
        game = GameState(
            room_id=room_id,
            game_type=game_type,
            phase=GamePhase.WAITING,
            keywords=keywords,
            current_keyword=current_keyword,
            players=player_states,
            config=config or {}
        )
        
        self._games[game_id] = game
        self._room_to_game[room_id] = game_id
        
        logger.info(f"创建游戏 {game_id}，房间 {room_id}，类型 {game_type.value}")
        
        return game
    
    def start_game(self, room_id: str) -> Dict:
        """开始游戏"""
        game = self._get_game_by_room(room_id)
        if not game:
            return {'error': 'GAME_NOT_FOUND'}
        
        if game.phase != GamePhase.WAITING:
            return {'error': 'INVALID_PHASE', 'message': f'当前阶段: {game.phase.value}'}
        
        # 切换到 PLAYING 阶段
        game.phase = GamePhase.PLAYING
        game.started_at = datetime.now()
        
        # 创建第一个回合
        self._start_turn(room_id)
        
        return {
            'status': 'playing',
            'game': game.to_dict(),
            'message': f'游戏开始！当前关键字：「{game.current_keyword}」'
        }
    
    def _start_turn(self, room_id: str) -> TurnState:
        """开始新回合"""
        game = self._get_game_by_room(room_id)
        if not game:
            raise ValueError("游戏不存在")
        
        import uuid
        
        # 获取当前玩家
        alive_players = [p for p in game.players.values() if p.is_alive]
        if not alive_players:
            self._finish_game(room_id)
            return None
        
        current_player = alive_players[0]
        
        # 计算截止时间
        time_limit = game.config.get('time_limit_sec', 15)
        now = datetime.now()
        deadline = now + timedelta(seconds=time_limit)
        
        # 创建回合
        turn = TurnState(
            turn_id=str(uuid.uuid4()),
            round_no=len(game.turn_history) + 1,
            player_id=current_player.user_id,
            keyword=game.current_keyword,
            start_time=now,
            deadline=deadline
        )
        
        game.current_turn = turn
        
        return turn
    
    def submit_answer(self, room_id: str, user_id: str, 
                     answer: str, client_time: datetime = None) -> Dict:
        """
        提交答案
        
        Args:
            room_id: 房间ID
            user_id: 用户ID
            answer: 答案
            client_time: 客户端时间（用于计算延迟）
        """
        game = self._get_game_by_room(room_id)
        if not game:
            return {'error': 'GAME_NOT_FOUND'}
        
        if game.phase != GamePhase.PLAYING:
            return {'error': 'INVALID_PHASE'}
        
        if not game.current_turn:
            return {'error': 'NO_ACTIVE_TURN'}
        
        # 检查是否是当前玩家
        if game.current_turn.player_id != user_id:
            return {
                'error': 'NOT_YOUR_TURN',
                'current_player': game.current_turn.player_id
            }
        
        # 检查是否超时
        now = datetime.now()
        if now > game.current_turn.deadline:
            return self._handle_timeout(room_id, user_id)
        
        # 清理答案
        answer = answer.strip()
        if not answer:
            return {'error': 'EMPTY_ANSWER'}
        
        # 验证答案（简化版本，实际需要调用题库）
        is_valid, result, details = self._validate_answer(
            answer, game.current_keyword, game.used_lines
        )
        
        player = game.players.get(user_id)
        if not player:
            return {'error': 'PLAYER_NOT_FOUND'}
        
        if is_valid:
            # 计分
            score = self._calculate_score(game, player, now)
            player.score += score
            player.correct_count += 1
            player.streak += 1
            player.max_streak = max(player.max_streak, player.streak)
            
            # 记录已用诗句
            game.used_lines.append(answer)
            
            # 记录回合历史
            game.turn_history.append({
                'turn_id': game.current_turn.turn_id,
                'player_id': user_id,
                'answer': answer,
                'result': 'VALID',
                'score': score,
                'timestamp': now.isoformat()
            })
            
            # 更新关键词（如果是接尾模式）
            if game.game_type == GameType.TAIL_CONNECT:
                # 从答案中提取尾字
                tail_char = self._extract_tail_char(answer)
                if tail_char:
                    game.current_keyword = tail_char
            
            # 下一回合
            next_turn = self._start_turn(room_id)
            
            return {
                'result': 'VALID',
                'score_delta': score,
                'total_score': player.score,
                'streak': player.streak,
                'next_keyword': game.current_keyword,
                'message': f'正确！+{score}分'
            }
        else:
            # 答错 - 淘汰
            player.streak = 0
            player.is_alive = False
            player.eliminated_at = now
            player.eliminate_reason = result
            
            # 记录回合历史
            game.turn_history.append({
                'turn_id': game.current_turn.turn_id,
                'player_id': user_id,
                'answer': answer,
                'result': result,
                'timestamp': now.isoformat()
            })
            
            # 检查游戏是否结束
            alive = [p for p in game.players.values() if p.is_alive]
            if len(alive) <= 1:
                return self._finish_game(room_id, winner=alive[0] if alive else None)
            
            # 下一回合
            self._start_turn(room_id)
            
            return {
                'result': result,
                'eliminated': True,
                'player': player.nickname,
                'message': self._get_result_message(result),
                'next_player': game.current_turn.player_id if game.current_turn else None
            }
    
    def _validate_answer(self, answer: str, keyword: str, 
                        used_lines: List[str]) -> tuple:
        """
        验证答案
        
        Returns:
            (is_valid, result_code, details)
        """
        import re
        
        # 清理答案
        clean = re.sub(r'[，。！？；：""''【】（）、…—]', '', answer.strip())
        
        # 检查是否包含关键词
        if keyword not in clean:
            return False, 'KEYWORD_NOT_FOUND', {'keyword': keyword}
        
        # 检查是否已使用
        if clean in used_lines:
            return False, 'DUPLICATE', {'line': clean}
        
        # 检查长度
        if len(clean) < 5:
            return False, 'TOO_SHORT', {'length': len(clean)}
        
        # 检查是否全为汉字
        if not re.search(r'[\u4e00-\u9fff]', clean):
            return False, 'INVALID_FORMAT', {}
        
        return True, 'VALID', {'line': clean}
    
    def _calculate_score(self, game: GameState, player: PlayerState,
                        submit_time: datetime) -> int:
        """计算得分"""
        base_score = 10
        
        # 速度加成
        if game.current_turn:
            time_remaining = (game.current_turn.deadline - submit_time).total_seconds()
            if time_remaining > 10:
                base_score += 3
            elif time_remaining > 5:
                base_score += 1
        
        # 连续加成
        if player.streak > 1:
            base_score += player.streak * 2
        
        # 五行加成（节气模式）
        if game.game_type == GameType.SOLAR_TERM:
            base_score *= 2
        
        return base_score
    
    def _extract_tail_char(self, line: str) -> Optional[str]:
        """提取诗句尾字"""
        import re
        clean = re.sub(r'[，。！？；：""''【】（）、…—]', '', line.strip())
        
        if len(clean) < 2:
            return None
        
        # 返回最后一个有意义的汉字
        for i in range(len(clean) - 1, -1, -1):
            char = clean[i]
            if '\u4e00' <= char <= '\u9fff':
                return char
        
        return None
    
    def _handle_timeout(self, room_id: str, user_id: str) -> Dict:
        """处理超时"""
        game = self._get_game_by_room(room_id)
        if not game:
            return {'error': 'GAME_NOT_FOUND'}
        
        player = game.players.get(user_id)
        if player:
            player.streak = 0
            player.is_alive = False
            player.eliminated_at = datetime.now()
            player.eliminate_reason = 'TIMEOUT'
        
        # 检查游戏是否结束
        alive = [p for p in game.players.values() if p.is_alive]
        if len(alive) <= 1:
            return self._finish_game(room_id, winner=alive[0] if alive else None)
        
        # 下一回合
        self._start_turn(room_id)
        
        return {
            'result': 'TIMEOUT',
            'eliminated': True,
            'player': player.nickname if player else user_id,
            'message': '超时了！被淘汰',
            'next_player': game.current_turn.player_id if game.current_turn else None
        }
    
    def _finish_game(self, room_id: str, winner: PlayerState = None) -> Dict:
        """结束游戏"""
        game = self._get_game_by_room(room_id)
        if not game:
            return {'error': 'GAME_NOT_FOUND'}
        
        game.phase = GamePhase.FINISHED
        game.finished_at = datetime.now()
        
        # 排序玩家
        ranking = sorted(
            game.players.values(),
            key=lambda p: (p.score, p.correct_count),
            reverse=True
        )
        
        return {
            'status': 'finished',
            'winner': {
                'user_id': winner.user_id,
                'nickname': winner.nickname,
                'score': winner.score
            } if winner else None,
            'ranking': [
                {
                    'rank': i + 1,
                    'user_id': p.user_id,
                    'nickname': p.nickname,
                    'score': p.score,
                    'correct_count': p.correct_count,
                    'is_winner': p.user_id == winner.user_id if winner else False
                }
                for i, p in enumerate(ranking)
            ],
            'stats': {
                'total_turns': len(game.turn_history),
                'total_lines': len(game.used_lines),
                'duration_seconds': (
                    (game.finished_at - game.started_at).total_seconds()
                    if game.started_at else 0
                )
            }
        }
    
    def _get_result_message(self, result: str) -> str:
        """获取结果描述"""
        messages = {
            'KEYWORD_NOT_FOUND': '诗句中没有包含关键字',
            'DUPLICATE': '这句诗已经用过了',
            'TOO_SHORT': '诗句太短了',
            'INVALID_FORMAT': '格式不正确',
            'TIMEOUT': '超时了'
        }
        return messages.get(result, '答案无效')
    
    def _get_game_by_room(self, room_id: str) -> Optional[GameState]:
        """通过房间ID获取游戏"""
        game_id = self._room_to_game.get(room_id)
        if game_id:
            return self._games.get(game_id)
        return None
    
    def get_game_state(self, room_id: str) -> Optional[Dict]:
        """获取游戏状态"""
        game = self._get_game_by_room(room_id)
        if game:
            return game.to_dict()
        return None
    
    def get_current_turn_info(self, room_id: str) -> Optional[Dict]:
        """获取当前回合信息"""
        game = self._get_game_by_room(room_id)
        if not game or not game.current_turn:
            return None
        
        turn = game.current_turn
        return {
            'turn_id': turn.turn_id,
            'round_no': turn.round_no,
            'player_id': turn.player_id,
            'player_nickname': game.players[turn.player_id].nickname if turn.player_id in game.players else '',
            'keyword': turn.keyword,
            'deadline': turn.deadline.isoformat() if turn.deadline else None,
            'time_remaining': max(0, (turn.deadline - datetime.now()).total_seconds()) if turn.deadline else 0
        }
