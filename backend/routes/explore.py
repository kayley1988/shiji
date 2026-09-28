"""探索页 API"""
from flask import Blueprint, request, jsonify
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, scoped_session
from models import Poem
import random

explore_bp = Blueprint('explore', __name__)

# 创建本地Session
engine = create_engine('sqlite:///shiyayaji.db')
Session = scoped_session(sessionmaker(bind=engine))

@explore_bp.route('/daily', methods=['GET'])
def get_daily():
    """每日推荐诗词"""
    count = Session.query(Poem).count()
    if count == 0:
        return jsonify({'success': True, 'data': {'poems': []}})
    
    random_offset = random.randint(0, max(0, count - 1))
    poem = Session.query(Poem).offset(random_offset).first()

    # 诗句内容在 poem_lines 表（poems 表无 content 字段），取首句作为今日推荐
    line = ''
    if poem:
        row = Session.execute(
            text('SELECT content FROM poem_lines WHERE poem_id = :pid ORDER BY line_no LIMIT 1'),
            {'pid': poem.id}
        ).fetchone()
        line = row[0] if row else ''

    return jsonify({
        'success': True,
        'data': {
            'poems': [{
                'id': poem.id,
                'title': poem.title,
                'author': poem.author,
                'dynasty': poem.dynasty,
                'line': line,
                'content': line,
                'tags': getattr(poem, 'tags', [])
            }] if poem else []
        }
    })

@explore_bp.route('/filters', methods=['GET'])
def get_filters():
    """获取筛选条件"""
    return jsonify({
        'success': True,
        'data': {
            'dynasties': ['唐', '宋', '元', '明', '清'],
            'imagery': ['月', '花', '春', '秋', '风', '雨', '山', '水', '云', '雪'],
            'themes': ['思乡', '送别', '怀古', '山水', '田园', '爱情']
        }
    })

@explore_bp.route('/poems', methods=['GET'])
def get_poems():
    """获取诗词列表"""
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 20, type=int)
    dynasty = request.args.get('dynasty')
    
    query = Session.query(Poem)
    if dynasty:
        query = query.filter_by(dynasty=dynasty)
    
    total = query.count()
    poems = query.offset((page - 1) * page_size).limit(page_size).all()
    
    return jsonify({
        'success': True,
        'data': {
            'poems': [{
                'id': p.id,
                'title': p.title,
                'author': p.author,
                'dynasty': p.dynasty
            } for p in poems]
        }
    })
