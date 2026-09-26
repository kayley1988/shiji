"""
接尾飞花令服务 - 接龙模式的诗句对战
核心玩法：
1. 系统给出一个起始字
2. 玩家需要说出包含这个字的诗句
3. 下一位玩家需要用上一句的尾字作为新的起始字继续
4. 循环往复，直到有人超时/错误/重复
"""
import re
import random
import logging
from datetime import datetime
from typing import Optional, List, Dict, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class TailConnectStatus(Enum):
    """接尾游戏状态"""
    WAITING = "waiting"           # 等待开始
    PLAYING = "playing"           # 进行中
    ROUND_ACTIVE = "round_active" # 当前回合活跃
    ROUND_END = "round_end"       # 回合结束
    FINISHED = "finished"         # 游戏结束


@dataclass
class TailConnectTurn:
    """接尾回合数据"""
    turn_id: str
    round_no: int
    player_id: str
    start_char: str              # 本轮起始字（上一句的尾字）
    submitted_line: Optional[str] # 本轮提交的诗句
    result: Optional[str]        # VALID / INVALID / DUPLICATE / TIMEOUT
    score_delta: int
    created_at: datetime


@dataclass  
class TailConnectState:
    """接尾游戏状态"""
    room_id: str
    status: TailConnectStatus
    current_char: str            # 当前需要接的字
    current_player_id: str       # 当前回合玩家
    round_no: int
    used_lines: List[str]        # 本局已使用的诗句
    used_chars: List[str]        # 本局已使用的接字
    player_scores: Dict[str, int]  # 玩家分数
    player_stats: Dict[str, Dict]  # 玩家统计（答对数、连续数等）
    turn_history: List[TailConnectTurn]
    config_version: str


class TailConnectService:
    """
    接尾飞花令核心服务
    
    玩法规则：
    1. 模式A - 单字接尾：尾字 = 下一句首字（如"月" -> "海上生明月" -> "月"）
    2. 模式B - 双字接尾：尾字 = 下一句首两字（如"明月" -> "明日"）
    3. 模式C - 意象接尾：尾字匹配意象库中的任意字
    
    计分规则：
    - 基础分：答对 +10 分
    - 连续加成：连续答对 N 句，额外 +N 分
    - 意象加成：包含当前节气意象 +5 分
    - 速度加成：剩余时间 > 5秒 +3 分
    """
    
    # 常用接尾映射（基于诗词大数据统计）
    COMMON_TAIL_CONNECTIONS = {
        '月': ['圆', '明', '光', '色', '夜', '下', '中', '上', '高', '生'],
        '明': ['月', '珠', '镜', '灭', '朗', '媚', '春', '发', '朝'],
        '圆': ['月', '魄', '光', '折', '规', '荷', '方'],
        '光': ['阴', '辉', '照', '寒', '射', '入', '转'],
        '夜': ['色', '深', '静', '长', '阑', '半', '凉', '雨', '风'],
        '春': ['风', '雨', '来', '去', '色', '晓', '暮', '眠', '归', '深'],
        '风': ['吹', '起', '来', '雨', '云', '声', '送', '过', '吹'],
        '雨': ['声', '落', '来', '打', '滴', '晴', '过', '寒', '细'],
        '秋': ['风', '月', '色', '声', '意', '心', '思', '叶', '水'],
        '花': ['开', '落', '香', '红', '白', '黄', '春', '飞', '发'],
        '鸟': ['啼', '鸣', '飞', '宿', '去', '来', '声'],
        '山': ['上', '下', '中', '高', '青', '水', '色', '顶'],
        '水': ['流', '深', '清', '长', '远', '东', '阔', '寒'],
        '云': ['飞', '去', '来', '卷', '舒', '深', '淡', '归'],
        '心': ['中', '上', '里', '意', '情', '乱', '伤', '寒'],
        '情': ['深', '长', '意', '真', '浓', '薄', '老', '在'],
        '思': ['念', '故', '乡', '君', '人', '归', '家', '子'],
        '酒': ['醉', '杯', '香', '浓', '醇', '熟', '倾'],
        '人': ['生', '间', '去', '老', '来', '在', '心', '中'],
        '天': ['上', '下', '空', '涯', '地', '长', '高'],
        '江': ['上', '水', '南', '北', '流', '天', '潮', '阔'],
        '归': ['去', '来', '程', '隐', '鸟', '帆', '思'],
        '来': ['去', '风', '人', '春', '雁', '月'],
        '去': ['国', '年', '人', '声', '日', '留'],
        '生': ['死', '涯', '年', '春', '机', '意'],
        '死': ['生', '别', '日', '心'],
        '柳': ['色', '枝', '棉', '风', '絮'],
        '梅': ['花', '香', '影', '骨', '边'],
        '竹': ['风', '声', '影', '林', '里'],
        '松': ['下', '风', '声', '柏', '间'],
        '雪': ['落', '飞', '白', '寒', '消'],
        '霜': ['落', '降', '寒', '重', '白'],
        '日': ['出', '落', '斜', '暮', '照', '长', '高'],
        '星': ['光', '稀', '河', '空', '乱'],
    }
    
    # 需要过滤的停用字（作为单字没有实际含义）
    STOP_CHARS = {'的', '了', '着', '过', '在', '是', '有', '和', '与', '或', '但', '而', '之'}
    
    def __init__(self, db_session):
        self.db = db_session
    
    def get_next_char(self, line: str) -> Optional[str]:
        """
        从诗句获取接尾字
        返回最后两个有意义的汉字
        """
        # 移除标点和空白
        line = re.sub(r'[，。！？；：""''【】（）、…—]', '', line.strip())
        
        if len(line) < 2:
            return None
        
        # 从后往前找有意义的字
        for i in range(len(line) - 1, -1, -1):
            char = line[i]
            if self._is_meaningful_char(char):
                # 尝试获取前一个有意义字组成双字词
                if i > 0:
                    prev_char = line[i-1]
                    if self._is_meaningful_char(prev_char):
                        return prev_char + char
                return char
        
        return None
    
    def _is_meaningful_char(self, char: str) -> bool:
        """判断是否是有意义的汉字"""
        if not char or len(char) != 1:
            return False
        # Unicode 汉字范围
        if '\u4e00' <= char <= '\u9fff':
            return char not in self.STOP_CHARS
        return False
    
    def validate_answer(self, answer: str, required_char: str, mode: str = 'single') -> Tuple[bool, str, Dict]:
        """
        验证答案是否正确
        
        Returns:
            (is_valid, result_code, details)
        """
        answer = answer.strip()
        if not answer:
            return False, 'EMPTY', {}
        
        # 移除标点
        clean_answer = re.sub(r'[，。！？；：""''【】（）、…—]', '', answer)
        
        # 检查是否包含必需的字
        if required_char not in clean_answer:
            return False, 'CHAR_NOT_FOUND', {
                'required': required_char,
                'submitted': answer[:20]
            }
        
        # 检查是否本局已使用
        if clean_answer in self.db.get('used_lines', []):
            return False, 'DUPLICATE', {
                'line': clean_answer,
                'used_count': self.db['used_lines'].count(clean_answer)
            }
        
        # 验证是否为有效诗句（简化：长度 >= 7 且有一定语义）
        if len(clean_answer) < 5:
            return False, 'TOO_SHORT', {'length': len(clean_answer)}
        
        # 验证通过
        return True, 'VALID', {
            'line': clean_answer,
            'tail_char': self.get_next_char(clean_answer)
        }
    
    def get_recommended_chars(self, current_char: str, limit: int = 5) -> List[str]:
        """
        获取推荐的下一步接字
        基于常用接尾映射和诗词数据库统计
        """
        recommendations = []
        
        # 1. 直接从映射获取
        if current_char in self.COMMON_TAIL_CONNECTIONS:
            recommendations.extend(self.COMMON_TAIL_CONNECTIONS[current_char][:3])
        
        # 2. 反向查找：哪些字经常接在当前字后面
        # 这个需要数据库支持，暂时用预设映射
        
        # 3. 过滤已使用的字
        used_chars = self.db.get('used_chars', [])
        recommendations = [c for c in recommendations if c not in used_chars]
        
        # 4. 打乱顺序
        random.shuffle(recommendations)
        
        return recommendations[:limit]
    
    def calculate_score(self, is_correct: bool, time_remaining: int, 
                        streak: int, has_imagery: bool, mode: str) -> int:
        """
        计算本轮得分
        
        Args:
            is_correct: 是否答对
            time_remaining: 剩余时间（秒）
            streak: 当前连续答对数
            has_imagery: 是否包含节气意象
            mode: 游戏模式
        """
        if not is_correct:
            return 0
        
        base_score = 15 if mode == 'tail_connect' else 10
        
        score = base_score
        
        # 连续加成
        if streak > 1:
            score += streak * 2
        
        # 速度加成
        if time_remaining > 5:
            score += 3
        
        # 意象加成
        if has_imagery:
            score += 5
        
        return score
    
    def generate_hint(self, current_char: str, difficulty: str = 'medium') -> Dict:
        """
        生成提示信息
        帮助卡住的玩家
        """
        hints = {
            'easy': [
                f'提示：这是一个常用字，可以组成很多词',
                f'提示：想想带有这个字的成语',
                f'提示：从这个字能想到什么场景？'
            ],
            'medium': [
                f'提示：常见的诗句开头',
                f'提示：和自然、情感相关的词',
            ],
            'hard': [
                f'提示：需要一点诗词储备',
                f'提示：想想诗人常用的表达'
            ]
        }
        
        return {
            'hint': random.choice(hints.get(difficulty, hints['medium'])),
            'recommended_chars': self.get_recommended_chars(current_char)[:2],
            'remaining_hints': self.db.get('hints_remaining', 3)
        }
    
    def create_room(self, room_id: str, mode: str, difficulty: str, 
                   host_id: str, player_ids: List[str]) -> TailConnectState:
        """创建接尾游戏房间"""
        # 选择起始字（排除停用字）
        available_chars = [c for c in self.COMMON_TAIL_CONNECTIONS.keys() 
                          if c not in self.STOP_CHARS]
        start_char = random.choice(available_chars)
        
        # 初始化玩家状态
        player_scores = {pid: 0 for pid in player_ids}
        player_stats = {
            pid: {'correct': 0, 'streak': 0, 'max_streak': 0} 
            for pid in player_ids
        }
        
        state = TailConnectState(
            room_id=room_id,
            status=TailConnectStatus.WAITING,
            current_char=start_char,
            current_player_id=player_ids[0] if player_ids else '',
            round_no=0,
            used_lines=[],
            used_chars=[start_char],
            player_scores=player_scores,
            player_stats=player_stats,
            turn_history=[],
            config_version='v1'
        )
        
        # 存储状态
        self.db[room_id] = state
        
        return state
    
    def start_game(self, room_id: str) -> Dict:
        """开始游戏"""
        if room_id not in self.db:
            return {'error': 'ROOM_NOT_FOUND'}
        
        state = self.db[room_id]
        state.status = TailConnectStatus.PLAYING
        state.round_no = 1
        
        return {
            'status': 'playing',
            'current_char': state.current_char,
            'current_player_id': state.current_player_id,
            'round_no': state.round_no,
            'message': f'游戏开始！请用包含「{state.current_char}」字的诗句来接龙'
        }
    
    def submit_answer(self, room_id: str, player_id: str, answer: str,
                     time_limit: int = 8) -> Dict:
        """提交答案"""
        if room_id not in self.db:
            return {'error': 'ROOM_NOT_FOUND'}
        
        state = self.db[room_id]
        
        # 检查是否是当前玩家
        if state.current_player_id != player_id:
            return {'error': 'NOT_YOUR_TURN', 'current_player': state.current_player_id}
        
        # 验证答案
        is_valid, result, details = self.validate_answer(
            answer, state.current_char
        )
        
        if is_valid:
            # 计算得分
            score = self.calculate_score(
                is_correct=True,
                time_remaining=time_limit,
                streak=state.player_stats[player_id]['streak'],
                has_imagery=False,
                mode='tail_connect'
            )
            
            # 更新状态
            state.player_scores[player_id] += score
            state.player_stats[player_id]['correct'] += 1
            state.player_stats[player_id]['streak'] += 1
            state.player_stats[player_id]['max_streak'] = max(
                state.player_stats[player_id]['max_streak'],
                state.player_stats[player_id]['streak']
            )
            
            # 获取下一轮接字
            next_char = details.get('tail_char', state.current_char)
            if next_char and next_char not in state.used_chars:
                state.used_chars.append(next_char)
                state.current_char = next_char
            else:
                # 如果尾字已使用或无效，随机选一个新字
                available = [c for c in self.COMMON_TAIL_CONNECTIONS.keys() 
                            if c not in state.used_chars]
                if available:
                    state.current_char = random.choice(available)
                    state.used_chars.append(state.current_char)
            
            # 更新当前玩家（轮转到下一个存活玩家）
            alive_players = [pid for pid in state.player_scores.keys() 
                           if state.player_stats[pid]['streak'] >= 0]  # 简化逻辑
            current_idx = alive_players.index(player_id) if player_id in alive_players else 0
            next_idx = (current_idx + 1) % len(alive_players)
            state.current_player_id = alive_players[next_idx]
            
            state.used_lines.append(details['line'])
            state.round_no += 1
            
            return {
                'result': 'VALID',
                'score_delta': score,
                'total_score': state.player_scores[player_id],
                'next_char': state.current_char,
                'next_player': state.current_player_id,
                'line': details['line'],
                'message': f'正确！+{score}分，下一句需包含「{state.current_char}」'
            }
        else:
            # 答错：重置连续数
            state.player_stats[player_id]['streak'] = 0
            
            # 轮转到下一个玩家
            alive_players = list(state.player_scores.keys())
            current_idx = alive_players.index(player_id) if player_id in alive_players else 0
            next_idx = (current_idx + 1) % len(alive_players)
            state.current_player_id = alive_players[next_idx]
            
            return {
                'result': result,
                'score_delta': 0,
                'total_score': state.player_scores[player_id],
                'details': details,
                'next_player': state.current_player_id,
                'message': f'答错！{self._get_result_message(result)}'
            }
    
    def _get_result_message(self, result: str) -> str:
        """获取结果描述"""
        messages = {
            'CHAR_NOT_FOUND': f'诗句中需要包含「当前字」',
            'DUPLICATE': '这句诗已经用过了，换一句吧',
            'TOO_SHORT': '诗句太短了，需要更完整的诗句',
            'EMPTY': '请输入诗句'
        }
        return messages.get(result, '答案无效')
    
    def timeout(self, room_id: str, player_id: str) -> Dict:
        """处理超时"""
        if room_id not in self.db:
            return {'error': 'ROOM_NOT_FOUND'}
        
        state = self.db[room_id]
        state.player_stats[player_id]['streak'] = 0
        
        # 轮转到下一个玩家
        alive_players = list(state.player_scores.keys())
        current_idx = alive_players.index(player_id) if player_id in alive_players else 0
        next_idx = (current_idx + 1) % len(alive_players)
        state.current_player_id = alive_players[next_idx]
        
        return {
            'result': 'TIMEOUT',
            'next_player': state.current_player_id,
            'current_char': state.current_char,
            'message': '超时了！轮到下一位'
        }
    
    def eliminate_player(self, room_id: str, player_id: str, reason: str) -> Dict:
        """淘汰玩家"""
        if room_id not in self.db:
            return {'error': 'ROOM_NOT_FOUND'}
        
        state = self.db[room_id]
        
        # 从存活玩家中移除
        alive_players = [pid for pid in state.player_scores.keys() 
                        if state.player_stats[pid]['streak'] >= 0 and pid != player_id]
        
        if len(alive_players) <= 1:
            # 游戏结束
            state.status = TailConnectStatus.FINISHED
            winner_id = alive_players[0] if alive_players else None
            
            return {
                'game_over': True,
                'winner_id': winner_id,
                'winner_score': state.player_scores.get(winner_id, 0),
                'final_scores': state.player_scores,
                'total_rounds': state.round_no,
                'message': f'游戏结束！{"恭喜 " + winner_id + " 获胜！" if winner_id else "平局！"}'
            }
        
        # 轮转到下一个存活玩家
        if state.current_player_id == player_id:
            state.current_player_id = alive_players[0]
        
        return {
            'game_over': False,
            'eliminated_id': player_id,
            'reason': reason,
            'remaining_players': alive_players,
            'next_player': state.current_player_id
        }
    
    def get_state(self, room_id: str) -> Optional[Dict]:
        """获取游戏状态"""
        if room_id not in self.db:
            return None
        
        state = self.db[room_id]
        return {
            'room_id': state.room_id,
            'status': state.status.value,
            'current_char': state.current_char,
            'current_player_id': state.current_player_id,
            'round_no': state.round_no,
            'player_scores': state.player_scores,
            'used_chars': state.used_chars,
            'used_lines_count': len(state.used_lines)
        }
