"""
后端路由初始化
"""
from .tail_connect import tail_connect_bp
from .art import art_bp
from .poems import poems_bp

__all__ = ['tail_connect_bp', 'art_bp', 'poems_bp']
