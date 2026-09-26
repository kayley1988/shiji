"""诗语雅集 - 数据库模型"""
from datetime import datetime, timezone
from enum import Enum as PyEnum
from typing import Optional
import uuid

from sqlalchemy import (
    Column, String, Integer, Boolean, DateTime, ForeignKey, 
    Text, JSON, Enum, UniqueConstraint, Index, create_engine
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

Base = declarative_base()


def utcnow():
    return datetime.now(timezone.utc)


def gen_uuid():
    return str(uuid.uuid4())


class User(Base):
    """用户表"""
    __tablename__ = 'users'
    
    id = Column(String(36), primary_key=True, default=gen_uuid)
    nickname = Column(String(50), default='匿名雅客')
    rank = Column(String(20), default='萌新')
    exp = Column(Integer, default=0)
    total_games = Column(Integer, default=0)
    total_wins = Column(Integer, default=0)
    total_correct = Column(Integer, default=0)
    avatar_url = Column(String(500), nullable=True)
    device_id = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)
    
    # 关系
    sessions = relationship('UserSession', back_populates='user', cascade='all, delete-orphan')
    room_memberships = relationship('RoomMember', back_populates='user')
    results = relationship('GameResult', back_populates='user')
    favorites = relationship('UserFavorite', back_populates='user')
    poem_unlocks = relationship('UserPoemUnlock', back_populates='user')


class UserSession(Base):
    """用户会话表"""
    __tablename__ = 'user_sessions'
    
    id = Column(String(36), primary_key=True, default=gen_uuid)
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    refresh_token_hash = Column(String(128), nullable=True)
    expires_at = Column(DateTime, nullable=False)
    revoked_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=utcnow)
    
    # 关系
    user = relationship('User', back_populates='sessions')
    
    __table_args__ = (
        Index('ix_user_sessions_user_id', 'user_id'),
        Index('ix_user_sessions_expires_at', 'expires_at'),
    )


class RoomStatus(PyEnum):
    CREATED = 'CREATED'
    WAITING = 'WAITING'
    STARTING = 'STARTING'
    PLAYING = 'PLAYING'
    SETTLING = 'SETTLING'
    FINISHED = 'FINISHED'
    DISSOLVED = 'DISSOLVED'
    EXPIRED = 'EXPIRED'
    ABORTED = 'ABORTED'


class GameMode(PyEnum):
    CLASSIC = 'CLASSIC'           # 经典飞花令
    SOLAR_TERM_ELEMENT = 'SOLAR_TERM_ELEMENT'  # 节气五行飞花令


class Room(Base):
    """房间表"""
    __tablename__ = 'rooms'
    
    id = Column(String(36), primary_key=True, default=gen_uuid)
    code = Column(String(8), unique=True, nullable=False)  # 邀请码
    host_user_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    mode = Column(Enum(GameMode), default=GameMode.SOLAR_TERM_ELEMENT)
    status = Column(Enum(RoomStatus), default=RoomStatus.WAITING)
    
    # 配置快照（开局时锁定）
    keywords = Column(JSON, default=list)  # ["春", "风"]
    time_limit_sec = Column(Integer, default=15)
    max_players = Column(Integer, default=4)
    config_version = Column(String(20), nullable=True)  # 节气配置版本
    
    # 当前游戏状态
    current_turn_no = Column(Integer, default=0)
    current_player_id = Column(String(36), nullable=True)
    
    created_at = Column(DateTime, default=utcnow)
    started_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)
    
    # 关系
    host = relationship('User', foreign_keys=[host_user_id])
    members = relationship('RoomMember', back_populates='room', cascade='all, delete-orphan')
    turns = relationship('GameTurn', back_populates='room', cascade='all, delete-orphan')
    results = relationship('GameResult', back_populates='room', cascade='all, delete-orphan')
    used_lines = relationship('RoomUsedLine', back_populates='room', cascade='all, delete-orphan')
    
    __table_args__ = (
        Index('ix_rooms_status_created_at', 'status', 'created_at'),
        Index('ix_rooms_host_user_id', 'host_user_id'),
    )


class RoomMember(Base):
    """房间成员表"""
    __tablename__ = 'room_members'
    
    id = Column(String(36), primary_key=True, default=gen_uuid)
    room_id = Column(String(36), ForeignKey('rooms.id'), nullable=False)
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    seat_no = Column(Integer, nullable=True)  # 入座序号
    role = Column(String(20), default='member')  # host, member
    is_alive = Column(Boolean, default=True)
    connection_state = Column(String(20), default='offline')  # online, offline, reconnecting
    joined_at = Column(DateTime, default=utcnow)
    eliminated_at = Column(DateTime, nullable=True)
    eliminate_reason = Column(String(50), nullable=True)  # TIMEOUT, DUPLICATE, INVALID
    
    # 关系
    room = relationship('Room', back_populates='members')
    user = relationship('User', back_populates='room_memberships')
    
    __table_args__ = (
        UniqueConstraint('room_id', 'user_id', name='uq_room_member'),
        Index('ix_room_members_room_id_alive', 'room_id', 'is_alive'),
    )


class GameTurn(Base):
    """游戏回合表"""
    __tablename__ = 'game_turns'
    
    id = Column(String(36), primary_key=True, default=gen_uuid)
    room_id = Column(String(36), ForeignKey('rooms.id'), nullable=False)
    turn_no = Column(Integer, nullable=False)
    player_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    deadline_at = Column(DateTime, nullable=False)
    status = Column(String(20), default='pending')  # pending, answered, timeout, skipped
    submitted_at = Column(DateTime, nullable=True)
    
    # 关系
    room = relationship('Room', back_populates='turns')
    submissions = relationship('AnswerSubmission', back_populates='turn')
    
    __table_args__ = (
        UniqueConstraint('room_id', 'turn_no', name='uq_room_turn'),
        Index('ix_game_turns_room_status', 'room_id', 'status'),
    )


class AnswerResult(PyEnum):
    VALID = 'VALID'                     # 有效答案
    DUPLICATE = 'DUPLICATE'             # 重复
    INVALID = 'INVALID'                 # 无效
    PENDING_REVIEW = 'PENDING_REVIEW'   # 待审核
    LATE = 'LATE'                       # 超时
    NOT_YOUR_TURN = 'NOT_YOUR_TURN'     # 非当前玩家


class AnswerSubmission(Base):
    """答案提交表"""
    __tablename__ = 'answer_submissions'
    
    id = Column(String(36), primary_key=True, default=gen_uuid)
    room_id = Column(String(36), ForeignKey('rooms.id'), nullable=False)
    turn_id = Column(String(36), ForeignKey('game_turns.id'), nullable=False)
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    client_request_id = Column(String(36), nullable=False)  # 幂等键
    
    raw_text = Column(Text, nullable=False)  # 原始输入
    normalized_text = Column(Text, nullable=False)  # 规范化后的文本
    result = Column(Enum(AnswerResult), nullable=False)
    matched_line_id = Column(String(36), ForeignKey('poem_lines.id'), nullable=True)
    reason = Column(String(200), nullable=True)
    score_delta = Column(Integer, default=0)
    element_bonus = Column(Boolean, default=False)
    created_at = Column(DateTime, default=utcnow)
    
    # 关系
    turn = relationship('GameTurn', back_populates='submissions')
    matched_line = relationship('PoemLine', foreign_keys=[matched_line_id])
    
    __table_args__ = (
        UniqueConstraint('user_id', 'client_request_id', name='uq_user_client_request'),
        Index('ix_answer_submissions_room_turn', 'room_id', 'turn_id'),
        Index('ix_answer_submissions_matched_line', 'matched_line_id'),
    )


class RoomUsedLine(Base):
    """房间已用诗句行（防重复）"""
    __tablename__ = 'room_used_lines'
    
    room_id = Column(String(36), ForeignKey('rooms.id'), primary_key=True)
    poem_line_id = Column(String(36), ForeignKey('poem_lines.id'), primary_key=True)
    submission_id = Column(String(36), ForeignKey('answer_submissions.id'), nullable=False)
    
    room = relationship('Room', back_populates='used_lines')
    poem_line = relationship('PoemLine', back_populates='used_in_rooms')
    
    __table_args__ = (
        UniqueConstraint('room_id', 'poem_line_id', name='uq_room_used_line'),
    )


class GameResult(Base):
    """游戏结果表"""
    __tablename__ = 'game_results'
    
    id = Column(String(36), primary_key=True, default=gen_uuid)
    room_id = Column(String(36), ForeignKey('rooms.id'), nullable=False)
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    placement = Column(Integer, nullable=False)  # 名次
    score = Column(Integer, default=0)
    correct_count = Column(Integer, default=0)
    element_bonus_count = Column(Integer, default=0)
    is_winner = Column(Boolean, default=False)
    created_at = Column(DateTime, default=utcnow)
    
    # 关系
    room = relationship('Room', back_populates='results')
    user = relationship('User', back_populates='results')
    
    __table_args__ = (
        UniqueConstraint('room_id', 'user_id', name='uq_room_user_result'),
        Index('ix_game_results_user_created', 'user_id', 'created_at'),
    )


class ReviewStatus(PyEnum):
    DRAFT = 'DRAFT'
    PENDING = 'PENDING'
    APPROVED = 'APPROVED'
    REJECTED = 'REJECTED'
    OFFLINE = 'OFFLINE'


class TagType(PyEnum):
    SEASON = 'season'           # 季节
    SOLAR_TERM = 'solar_term'   # 节气
    ELEMENT = 'element'         # 五行
    REGION = 'region'           # 地域
    SCENE = 'scene'             # 场景
    DIFFICULTY = 'difficulty'   # 难度
    HEAT = 'heat'               # 热度


class Tag(Base):
    """标签表"""
    __tablename__ = 'tags'
    
    id = Column(String(36), primary_key=True, default=gen_uuid)
    type = Column(String(20), nullable=False)  # season, solar_term, element, region, scene, difficulty, heat
    name = Column(String(50), nullable=False)
    normalized_name = Column(String(50), nullable=False)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utcnow)
    
    __table_args__ = (
        UniqueConstraint('type', 'normalized_name', name='uq_tag_type_name'),
        Index('ix_tags_type_active', 'type', 'active'),
    )


class Poem(Base):
    """诗词表"""
    __tablename__ = 'poems'
    
    id = Column(String(36), primary_key=True, default=gen_uuid)
    title = Column(String(200), nullable=False)
    author = Column(String(100), nullable=False)
    dynasty = Column(String(50), nullable=True)
    
    # 来源与许可（必须记录）
    source_name = Column(String(200), nullable=True)
    source_url = Column(String(500), nullable=True)
    license_name = Column(String(100), nullable=True)
    license_url = Column(String(500), nullable=True)
    distribution_allowed = Column(Boolean, default=False)  # 是否允许分发
    
    # 审核状态
    review_status = Column(Enum(ReviewStatus), default=ReviewStatus.PENDING)
    
    created_at = Column(DateTime, default=utcnow)
    
    # 关系
    lines = relationship('PoemLine', back_populates='poem', cascade='all, delete-orphan')
    
    __table_args__ = (
        Index('ix_poems_review_distribution', 'review_status', 'distribution_allowed'),
    )


class PoemLine(Base):
    """诗句行表"""
    __tablename__ = 'poem_lines'
    
    id = Column(String(36), primary_key=True, default=gen_uuid)
    poem_id = Column(String(36), ForeignKey('poems.id'), nullable=False)
    line_no = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)  # 原始诗句
    normalized_content = Column(Text, nullable=False)  # 规范化（去标点、统一大小写）
    is_rare = Column(Boolean, default=False)  # 是否为冷门诗句
    review_status = Column(Enum(ReviewStatus), default=ReviewStatus.PENDING)
    source_locator = Column(String(100), nullable=True)  # 来源定位（如行号）
    
    created_at = Column(DateTime, default=utcnow)
    
    # 关系
    poem = relationship('Poem', back_populates='lines')
    tags = relationship('PoemLineTag', back_populates='poem_line', cascade='all, delete-orphan')
    aliases = relationship('PoemLineAlias', back_populates='poem_line', cascade='all, delete-orphan')
    used_in_rooms = relationship('RoomUsedLine', back_populates='poem_line')
    
    __table_args__ = (
        UniqueConstraint('poem_id', 'line_no', name='uq_poem_line_no'),
        Index('ix_poem_lines_normalized', 'normalized_content'),
        Index('ix_poem_lines_rare_review', 'is_rare', 'review_status'),
    )


class PoemLineTag(Base):
    """诗句-标签关联表"""
    __tablename__ = 'poem_line_tags'
    
    poem_line_id = Column(String(36), ForeignKey('poem_lines.id'), primary_key=True)
    tag_id = Column(String(36), ForeignKey('tags.id'), primary_key=True)
    confidence = Column(Integer, default=100)  # 置信度 0-100
    reviewed_by = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=utcnow)
    
    poem_line = relationship('PoemLine', back_populates='tags')
    tag = relationship('Tag')
    
    __table_args__ = (
        Index('ix_poem_line_tags_tag', 'tag_id'),
        Index('ix_poem_line_tags_line', 'poem_line_id'),
    )


class PoemLineAlias(Base):
    """诗句等价别名表（人工审核）"""
    __tablename__ = 'poem_line_aliases'
    
    id = Column(String(36), primary_key=True, default=gen_uuid)
    poem_line_id = Column(String(36), ForeignKey('poem_lines.id'), nullable=False)
    normalized_alias = Column(Text, nullable=False)
    review_status = Column(Enum(ReviewStatus), default=ReviewStatus.PENDING)
    created_at = Column(DateTime, default=utcnow)
    
    poem_line = relationship('PoemLine', back_populates='aliases')
    
    __table_args__ = (
        Index('ix_poem_line_aliases_alias_review', 'normalized_alias', 'review_status'),
    )


class SolarTerm(Base):
    """节气表"""
    __tablename__ = 'solar_terms'
    
    id = Column(String(36), primary_key=True, default=gen_uuid)
    name = Column(String(20), unique=True, nullable=False)
    start_date = Column(String(10), nullable=False)  # MM-DD 格式
    end_date = Column(String(10), nullable=False)
    season = Column(String(20), nullable=False)  # 春/夏/秋/冬
    primary_element = Column(String(10), nullable=False)  # 木/火/土/金/水
    description = Column(Text, nullable=True)
    config_version = Column(String(20), nullable=False)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utcnow)
    
    # 关系
    keywords = relationship('SolarTermKeyword', back_populates='solar_term', cascade='all, delete-orphan')
    
    __table_args__ = (
        Index('ix_solar_terms_start_date', 'start_date'),
        Index('ix_solar_terms_active', 'active'),
    )


class SolarTermKeyword(Base):
    """节气推荐关键词表"""
    __tablename__ = 'solar_term_keywords'
    
    id = Column(String(36), primary_key=True, default=gen_uuid)
    solar_term_id = Column(String(36), ForeignKey('solar_terms.id'), nullable=False)
    keyword = Column(String(20), nullable=False)
    imagery = Column(String(100), nullable=True)  # 意象描述，如"春风、杨柳"
    sort_order = Column(Integer, default=0)
    enabled = Column(Boolean, default=True)
    
    solar_term = relationship('SolarTerm', back_populates='keywords')
    
    __table_args__ = (
        UniqueConstraint('solar_term_id', 'keyword', name='uq_solar_term_keyword'),
        Index('ix_solar_term_keywords_term_enabled', 'solar_term_id', 'enabled'),
    )


class DailyTheme(Base):
    """每日主题表"""
    __tablename__ = 'daily_themes'
    
    date_cn = Column(String(10), primary_key=True)  # YYYY-MM-DD 中国日期
    solar_term_id = Column(String(36), ForeignKey('solar_terms.id'), nullable=False)
    keywords = Column(JSON, nullable=False)  # 当日推荐关键词
    imagery = Column(JSON, nullable=True)  # 最佳意象
    config_version = Column(String(20), nullable=False)
    created_at = Column(DateTime, default=utcnow)
    
    __table_args__ = (
        Index('ix_daily_themes_solar_term', 'solar_term_id'),
    )


class UserFavorite(Base):
    """用户收藏表"""
    __tablename__ = 'user_favorites'
    
    id = Column(String(36), primary_key=True, default=gen_uuid)
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    target_type = Column(String(20), nullable=False)  # poem, solar_term, poem_line
    target_id = Column(String(36), nullable=False)
    created_at = Column(DateTime, default=utcnow)
    
    user = relationship('User', back_populates='favorites')
    
    __table_args__ = (
        UniqueConstraint('user_id', 'target_type', 'target_id', name='uq_user_favorite'),
        Index('ix_user_favorites_user_type', 'user_id', 'target_type'),
    )


class UserPoemUnlock(Base):
    """用户诗句解锁记录"""
    __tablename__ = 'user_poem_unlocks'
    
    user_id = Column(String(36), ForeignKey('users.id'), primary_key=True)
    poem_line_id = Column(String(36), ForeignKey('poem_lines.id'), primary_key=True)
    unlock_reason = Column(String(50), nullable=False)  # CORRECT_ANSWER, ELIMINATED_KNOWLEDGE
    unlocked_at = Column(DateTime, default=utcnow)
    
    user = relationship('User', back_populates='poem_unlocks')
    poem_line = relationship('PoemLine')
    
    __table_args__ = (
        Index('ix_user_poem_unlocks_user', 'user_id'),
    )


class AuditEvent(Base):
    """审计事件表"""
    __tablename__ = 'audit_events'
    
    id = Column(String(36), primary_key=True, default=gen_uuid)
    actor_type = Column(String(20), nullable=False)  # user, system, admin
    actor_id = Column(String(36), nullable=True)
    action = Column(String(100), nullable=False)
    entity_type = Column(String(50), nullable=True)
    entity_id = Column(String(36), nullable=True)
    payload = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=utcnow)
    
    __table_args__ = (
        Index('ix_audit_events_entity', 'entity_type', 'entity_id'),
        Index('ix_audit_events_created', 'created_at'),
    )


class BadgeRarity(PyEnum):
    COMMON = 'common'
    RARE   = 'rare'
    EPIC   = 'epic'
    LEGEND = 'legend'


class BadgeCategory(PyEnum):
    FEIHUA     = 'feihua'
    SOLAR_TERM = 'solar_term'
    SOCIAL     = 'social'
    SPECIAL    = 'special'


class BadgeConditionType(PyEnum):
    CORRECT_COUNT    = 'correct_count'
    WIN_STREAK       = 'win_streak'
    GAMES_TOTAL      = 'games_total'
    KEYWORD_MASTER   = 'keyword_master'
    FIRST_BLOOD      = 'first_blood'


class Badge(Base):
    """徽章定义表"""
    __tablename__ = 'badges'

    id              = Column(String(36), primary_key=True, default=gen_uuid)
    code            = Column(String(50), unique=True, nullable=False)
    name            = Column(String(50), nullable=False)
    description     = Column(String(200), nullable=False)
    icon            = Column(String(10), nullable=False)   # emoji
    category        = Column(String(20), nullable=False)   # feihua / social / special
    rarity          = Column(String(20), nullable=False, default='common')
    condition_type  = Column(String(30), nullable=False)
    condition_value = Column(Integer, nullable=False, default=0)
    created_at      = Column(DateTime, default=utcnow)


class UserBadge(Base):
    """用户徽章表"""
    __tablename__ = 'user_badges'

    id       = Column(String(36), primary_key=True, default=gen_uuid)
    user_id  = Column(String(36), ForeignKey('users.id'), nullable=False)
    badge_id = Column(String(36), ForeignKey('badges.id'), nullable=False)
    earned_at = Column(DateTime, default=utcnow)

    __table_args__ = (
        UniqueConstraint('user_id', 'badge_id', name='uq_user_badge'),
        Index('ix_user_badges_user', 'user_id'),
        Index('ix_user_badges_badge', 'badge_id'),
    )


class PoemNote(Base):
    """私人诗摘"""
    __tablename__ = 'poem_notes'

    id          = Column(String(36), primary_key=True, default=gen_uuid)
    user_id     = Column(String(36), ForeignKey('users.id'), nullable=False)
    poem_id     = Column(String(36), ForeignKey('poems.id'), nullable=False)
    line_text   = Column(String(500), nullable=False)
    poem_title  = Column(String(200), nullable=True)
    poet_name   = Column(String(100), nullable=True)
    note        = Column(Text, nullable=True)
    mood_tag    = Column(String(50), nullable=True)
    created_at  = Column(DateTime, default=utcnow)
    updated_at  = Column(DateTime, default=utcnow, onupdate=utcnow)

    __table_args__ = (
        Index('ix_poem_notes_user', 'user_id'),
        Index('ix_poem_notes_mood', 'mood_tag'),
    )


def init_db(engine):
    """初始化数据库"""
    Base.metadata.create_all(engine)


if __name__ == '__main__':
    from sqlalchemy import create_engine
    engine = create_engine('sqlite:///shiyayaji.db', echo=True)
    init_db(engine)
    print("数据库初始化完成")
