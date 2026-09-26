"""飞花令练习 API"""
from flask import Blueprint, request, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from models import Poem, PoemLine
import random

solo_bp = Blueprint('solo', __name__)

engine = create_engine('sqlite:///shiyayaji.db')
Session = scoped_session(sessionmaker(bind=engine))

# 常用飞花令关键词
FEIHUA_KEYWORDS = [
    '月', '花', '春', '秋', '风', '雨', '山', '水', '云', '雪',
    '酒', '酒', '酒',  # 酒出现多次增加概率
    '江', '湖', '海', '河',
    '鸟', '鱼', '蝶', '蜂',
    '日', '星', '天', '地',
    '人', '心', '情', '思',
    '梅', '兰', '竹', '菊', '桃', '柳',
    '马', '舟', '楼', '亭', '桥'
]

@solo_bp.route('/keywords', methods=['GET'])
def get_keywords():
    """获取飞花令关键词"""
    return jsonify({
        'success': True,
        'data': {
            'keywords': FEIHUA_KEYWORDS
        }
    })

@solo_bp.route('/poems', methods=['GET'])
def get_poems_by_keyword():
    """根据关键词获取诗句"""
    keyword = request.args.get('keyword', '')
    limit = request.args.get('limit', 10, type=int)
    
    if not keyword:
        return jsonify({'success': False, 'error': '请提供关键词'}), 400
    
    # 搜索包含该关键词的诗句
    lines = Session.query(PoemLine).filter(
        PoemLine.content.like(f'%{keyword}%')
    ).limit(limit * 2).all()
    
    result = []
    for line in lines:
        result.append({
            'id': line.id,
            'content': line.content,
            'poem_id': line.poem_id
        })
    
    # 随机选择
    random.shuffle(result)
    result = result[:limit]
    
    return jsonify({
        'success': True,
        'data': {
            'poems': result,
            'keyword': keyword
        }
    })
