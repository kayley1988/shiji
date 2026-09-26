"""
藏书阁 - 个人诗词书架模块
包含：金句卡片、书架收藏、诗词分类
"""

from datetime import datetime, timezone
from enum import Enum as PyEnum
from typing import Optional
import uuid

from sqlalchemy import (
    Column, String, Integer, Boolean, DateTime, ForeignKey, 
    Text, JSON, Enum, UniqueConstraint, Index
)
from sqlalchemy.orm import relationship

from models import Base  # 导入主 Base


def utcnow():
    return datetime.now(timezone.utc)


def gen_uuid():
    return str(uuid.uuid4())


# ═══════════════════════════════════════════════════════════════════
# 藏书阁相关枚举
# ═══════════════════════════════════════════════════════════════════

class CardStyle(PyEnum):
    """卡片风格"""
    CLASSIC = 'classic'           # 经典拍立得
    RETRO = 'retro'             # 复古胶片
    INK = 'ink'                 # 水墨古卷
    MODERN = 'modern'            # 现代简约


class CardSize(PyEnum):
    """卡片尺寸"""
    SMALL = 'small'             # 小卡片 (3:4)
    MEDIUM = 'medium'           # 中卡片 (2:3)
    LARGE = 'large'             # 大卡片 (1:1)


class CollectionType(PyEnum):
    """收藏类型"""
    POEM = 'poem'               # 诗词
    GOLDEN_QUOTE = 'golden_quote'  # 金句卡片
    POEM_LINE = 'poem_line'     # 单句
    AUTHOR = 'author'            # 作者专辑


# ═══════════════════════════════════════════════════════════════════
# 藏书阁 - 金句卡片
# ═══════════════════════════════════════════════════════════════════

class GoldenQuote(Base):
    """金句卡片表"""
    __tablename__ = 'golden_quotes'
    
    id = Column(String(36), primary_key=True, default=gen_uuid)
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    
    # 诗句内容
    poem_line_id = Column(String(36), ForeignKey('poem_lines.id'), nullable=True)  # 关联诗句
    content = Column(Text, nullable=False)  # 诗句内容
    poem_title = Column(String(200), nullable=True)  # 诗题
    author = Column(String(100), nullable=True)  # 作者
    
    # 卡片样式
    style = Column(String(20), default=CardStyle.CLASSIC.value)  # 风格
    size = Column(String(20), default=CardSize.MEDIUM.value)  # 尺寸
    
    # AI 生成图片
    image_url = Column(String(500), nullable=True)
    image_prompt = Column(Text, nullable=True)  # 原始提示词
    image_generated_at = Column(DateTime, nullable=True)
    
    # 用户自定义
    title = Column(String(200), nullable=True)  # 自定义标题
    note = Column(Text, nullable=True)  # 心得笔记
    tags = Column(JSON, default=list)  # 自定义标签
    
    # 统计
    view_count = Column(Integer, default=0)
    share_count = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)
    
    # 关系
    user = relationship('User', foreign_keys=[user_id])
    poem_line = relationship('PoemLine', foreign_keys=[poem_line_id])
    
    __table_args__ = (
        Index('ix_golden_quotes_user', 'user_id'),
        Index('ix_golden_quotes_created', 'created_at'),
    )


# ═══════════════════════════════════════════════════════════════════
# 藏书阁 - 书架
# ═══════════════════════════════════════════════════════════════════

class Bookshelf(Base):
    """书架表"""
    __tablename__ = 'bookshelves'
    
    id = Column(String(36), primary_key=True, default=gen_uuid)
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    
    name = Column(String(100), nullable=False)  # 书架名称
    description = Column(String(500), nullable=True)  # 描述
    cover_url = Column(String(500), nullable=True)  # 封面图
    
    # 书架类型
    shelf_type = Column(String(20), default='custom')  # custom, favorite, golden_quotes, author, dynasty
    icon = Column(String(10), nullable=True)  # emoji 图标
    
    # 权限
    is_public = Column(Boolean, default=False)  # 是否公开
    is_default = Column(Boolean, default=False)  # 是否默认书架
    
    # 排序
    sort_order = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)
    
    # 关系
    user = relationship('User', foreign_keys=[user_id])
    items = relationship('BookshelfItem', back_populates='bookshelf', cascade='all, delete-orphan')
    
    __table_args__ = (
        UniqueConstraint('user_id', 'name', name='uq_bookshelf_user_name'),
        Index('ix_bookshelves_user', 'user_id'),
        Index('ix_bookshelves_sort', 'user_id', 'sort_order'),
    )


class BookshelfItem(Base):
    """书架条目表"""
    __tablename__ = 'bookshelf_items'
    
    id = Column(String(36), primary_key=True, default=gen_uuid)
    bookshelf_id = Column(String(36), ForeignKey('bookshelves.id'), nullable=False)
    
    # 收藏内容类型
    item_type = Column(String(20), nullable=False)  # poem, golden_quote, poem_line, author
    item_id = Column(String(36), nullable=False)  # 对应内容的 ID
    
    # 冗余存储（方便查询）
    title = Column(String(200), nullable=True)  # 标题
    author = Column(String(100), nullable=True)  # 作者
    excerpt = Column(Text, nullable=True)  # 摘要/首句
    cover_url = Column(String(500), nullable=True)  # 封面
    
    # 用户备注
    note = Column(Text, nullable=True)
    rating = Column(Integer, nullable=True)  # 1-5 星
    
    # 统计
    view_count = Column(Integer, default=0)
    
    # 排序
    sort_order = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=utcnow)
    
    # 关系
    bookshelf = relationship('Bookshelf', back_populates='items')
    
    __table_args__ = (
        UniqueConstraint('bookshelf_id', 'item_type', 'item_id', name='uq_bookshelf_item'),
        Index('ix_bookshelf_items_bookshelf', 'bookshelf_id'),
        Index('ix_bookshelf_items_type', 'item_type'),
    )


# ═══════════════════════════════════════════════════════════════════
# 藏书阁 - 诗词分类
# ═══════════════════════════════════════════════════════════════════

class PoemCategory(Base):
    """诗词分类表"""
    __tablename__ = 'poem_categories'
    
    id = Column(String(36), primary_key=True, default=gen_uuid)
    
    name = Column(String(50), nullable=False)  # 分类名称
    slug = Column(String(50), unique=True, nullable=False)  # URL slug
    icon = Column(String(10), nullable=True)  # emoji
    
    # 层级
    parent_id = Column(String(36), ForeignKey('poem_categories.id'), nullable=True)
    level = Column(Integer, default=1)  # 1=一级, 2=二级
    
    # 描述
    description = Column(String(500), nullable=True)
    
    # 统计
    poem_count = Column(Integer, default=0)
    
    sort_order = Column(Integer, default=0)
    active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=utcnow)
    
    # 自关联
    children = relationship('PoemCategory', backref='parent', remote_side=[id])
    
    __table_args__ = (
        Index('ix_poem_categories_parent', 'parent_id'),
        Index('ix_poem_categories_active', 'active'),
    )


class AuthorProfile(Base):
    """诗人专辑"""
    __tablename__ = 'author_profiles'
    
    id = Column(String(36), primary_key=True, default=gen_uuid)
    name = Column(String(100), nullable=False, unique=True)
    alias = Column(String(200), nullable=True)  # 别号
    dynasty = Column(String(50), nullable=True)
    
    # 生平
    birth_year = Column(String(20), nullable=True)  # 生年
    death_year = Column(String(20), nullable=True)  # 卒年
    bio = Column(Text, nullable=True)  # 简介
    
    # 头像
    avatar_url = Column(String(500), nullable=True)
    
    # 统计
    poem_count = Column(Integer, default=0)
    
    # 标签
    tags = Column(JSON, default=list)  # 如 ["豪放派", "诗仙"]
    
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utcnow)
    
    __table_args__ = (
        Index('ix_author_profiles_name', 'name'),
        Index('ix_author_profiles_dynasty', 'dynasty'),
    )


# ═══════════════════════════════════════════════════════════════════
# 阅读记录
# ═══════════════════════════════════════════════════════════════════

class ReadingHistory(Base):
    """阅读历史"""
    __tablename__ = 'reading_history'
    
    id = Column(String(36), primary_key=True, default=gen_uuid)
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    
    # 阅读内容
    item_type = Column(String(20), nullable=False)  # poem, golden_quote, poem_line
    item_id = Column(String(36), nullable=False)
    title = Column(String(200), nullable=True)
    author = Column(String(100), nullable=True)
    
    # 阅读时长（秒）
    duration = Column(Integer, default=0)
    
    # 是否完成
    finished = Column(Boolean, default=False)
    
    read_at = Column(DateTime, default=utcnow)
    
    __table_args__ = (
        Index('ix_reading_history_user', 'user_id'),
        Index('ix_reading_history_read_at', 'read_at'),
    )
