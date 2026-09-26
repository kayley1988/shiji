"""诗人 API"""
from flask import Blueprint, request, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from models import Poem

poet_bp = Blueprint('poet', __name__)

engine = create_engine('sqlite:///shiyayaji.db')
Session = scoped_session(sessionmaker(bind=engine))

@poet_bp.route('/cards', methods=['GET'])
def poet_cards():
    """获取诗人卡片列表"""
    dynasty = request.args.get('dynasty')
    
    # 获取著名诗人
    famous_authors = [
        {'name': '李白', 'dynasty': '唐', 'desc': '诗仙', 'poems': 1190},
        {'name': '杜甫', 'dynasty': '唐', 'desc': '诗圣', 'poems': 1458},
        {'name': '白居易', 'dynasty': '唐', 'desc': '诗魔', 'poems': 2841},
        {'name': '王维', 'dynasty': '唐', 'desc': '诗佛', 'poems': 383},
        {'name': '苏轼', 'dynasty': '宋', 'desc': '东坡居士', 'poems': 2892},
        {'name': '李清照', 'dynasty': '宋', 'desc': '千古第一才女', 'poems': 88},
        {'name': '辛弃疾', 'dynasty': '宋', 'desc': '词中之龙', 'poems': 646},
        {'name': '王安石', 'dynasty': '宋', 'desc': '唐宋八大家', 'poems': 1580},
    ]
    
    if dynasty:
        famous_authors = [p for p in famous_authors if p['dynasty'] == dynasty]
    
    return jsonify({
        'success': True,
        'data': {
            'poets': famous_authors
        }
    })

@poet_bp.route('/<author_name>', methods=['GET'])
def poet_detail(author_name):
    """获取诗人详情"""
    count = Session.query(Poem).filter(Poem.author.like(f'%{author_name}%')).count()
    
    return jsonify({
        'success': True,
        'data': {
            'name': author_name,
            'poem_count': count
        }
    })
