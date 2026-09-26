"""
藏书阁 API - 个人诗词书架
包含：金句卡片、书架管理、诗词分类
"""

from flask import Blueprint, request, jsonify, g
from sqlalchemy import or_, and_, func, create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from models import Poem, PoemLine, User, Base
from models_library import GoldenQuote, Bookshelf, BookshelfItem, PoemCategory, AuthorProfile, ReadingHistory

# 创建本地Session
engine = create_engine('sqlite:///shiyayaji.db')
Session = scoped_session(sessionmaker(bind=engine))

library_bp = Blueprint('library', __name__)


# ── 简化查询的辅助函数 ─────────────────────────────────────
def q(Model):
    """返回 Model 的查询对象"""
    return Session.query(Model)


# ── 分页辅助函数 ──────────────────────────────────────────
def paginate_query(query, page, per_page):
    """SQLAlchemy 分页辅助函数"""
    total = query.count()
    items = query.offset((page - 1) * per_page).limit(per_page).all()
    return items, total


# ═══════════════════════════════════════════════════════════════════
# 辅助函数
# ═══════════════════════════════════════════════════════════════════

def get_user_id():
    """获取当前用户 ID（简化版，假设已登录）"""
    # 实际应该从 g.user 或 session 获取
    return request.headers.get('X-User-ID') or 'default_user'


# ═══════════════════════════════════════════════════════════════════
# 书架管理
# ═══════════════════════════════════════════════════════════════════

@library_bp.route('/bookshelves', methods=['GET'])
def get_bookshelves():
    """获取用户书架列表"""
    user_id = get_user_id()
    
    shelves = q(Bookshelf).filter_by(user_id=user_id).order_by(Bookshelf.sort_order).all()
    
    result = []
    for shelf in shelves:
        # 统计条目数
        item_count = q(BookshelfItem).filter_by(bookshelf_id=shelf.id).count()
        
        result.append({
            'id': shelf.id,
            'name': shelf.name,
            'description': shelf.description,
            'cover_url': shelf.cover_url,
            'shelf_type': shelf.shelf_type,
            'icon': shelf.icon,
            'is_public': shelf.is_public,
            'is_default': shelf.is_default,
            'item_count': item_count,
            'sort_order': shelf.sort_order,
            'created_at': shelf.created_at.isoformat() if shelf.created_at else None
        })
    
    return jsonify({
        'success': True,
        'bookshelves': result
    })


@library_bp.route('/bookshelves', methods=['POST'])
def create_bookshelf():
    """创建书架"""
    user_id = get_user_id()
    data = request.get_json()
    
    name = data.get('name', '').strip()
    if not name:
        return jsonify({'success': False, 'error': '书架名称不能为空'}), 400
    
    shelf = Bookshelf(
        user_id=user_id,
        name=name,
        description=data.get('description'),
        shelf_type=data.get('shelf_type', 'custom'),
        icon=data.get('icon'),
        is_public=data.get('is_public', False)
    )
    
    Session().add(shelf)
    Session().commit()
    
    return jsonify({
        'success': True,
        'bookshelf': {
            'id': shelf.id,
            'name': shelf.name,
            'description': shelf.description,
            'shelf_type': shelf.shelf_type,
            'icon': shelf.icon
        }
    })


@library_bp.route('/bookshelves/<shelf_id>', methods=['PUT'])
def update_bookshelf(shelf_id):
    """更新书架"""
    user_id = get_user_id()
    data = request.get_json()
    
    shelf = q(Bookshelf).filter_by(id=shelf_id, user_id=user_id).first()
    if not shelf:
        return jsonify({'success': False, 'error': '书架不存在'}), 404
    
    if 'name' in data:
        shelf.name = data['name']
    if 'description' in data:
        shelf.description = data['description']
    if 'icon' in data:
        shelf.icon = data['icon']
    if 'cover_url' in data:
        shelf.cover_url = data['cover_url']
    if 'is_public' in data:
        shelf.is_public = data['is_public']
    if 'sort_order' in data:
        shelf.sort_order = data['sort_order']
    
    Session().commit()
    
    return jsonify({'success': True, 'bookshelf': {
        'id': shelf.id,
        'name': shelf.name,
        'description': shelf.description
    }})


@library_bp.route('/bookshelves/<shelf_id>', methods=['DELETE'])
def delete_bookshelf(shelf_id):
    """删除书架"""
    user_id = get_user_id()
    
    shelf = q(Bookshelf).filter_by(id=shelf_id, user_id=user_id).first()
    if not shelf:
        return jsonify({'success': False, 'error': '书架不存在'}), 404
    
    Session().delete(shelf)
    Session().commit()
    
    return jsonify({'success': True})


# ═══════════════════════════════════════════════════════════════════
# 书架条目
# ═══════════════════════════════════════════════════════════════════

@library_bp.route('/bookshelves/<shelf_id>/items', methods=['GET'])
def get_shelf_items(shelf_id):
    """获取书架内容"""
    user_id = get_user_id()
    
    shelf = Session.query(Bookshelf).filter_by(id=shelf_id, user_id=user_id).first()
    if not shelf:
        return jsonify({'success': False, 'error': '书架不存在'}), 404
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    item_type = request.args.get('type')  # 筛选类型
    
    query = Session.query(BookshelfItem).filter_by(bookshelf_id=shelf_id)
    
    if item_type:
        query = query.filter_by(item_type=item_type)
    
    items, total = paginate_query(
        query.order_by(BookshelfItem.sort_order, BookshelfItem.created_at.desc()),
        page, per_page
    )
    
    result = []
    for item in items:
        result.append({
            'id': item.id,
            'item_type': item.item_type,
            'item_id': item.item_id,
            'title': item.title,
            'author': item.author,
            'excerpt': item.excerpt,
            'cover_url': item.cover_url,
            'note': item.note,
            'rating': item.rating,
            'sort_order': item.sort_order,
            'created_at': item.created_at.isoformat() if item.created_at else None
        })
    
    return jsonify({
        'success': True,
        'items': result,
        'total': total,
        'page': page,
        'pages': (total + per_page - 1) // per_page if per_page > 0 else 0
    })


@library_bp.route('/bookshelves/<shelf_id>/items', methods=['POST'])
def add_shelf_item(shelf_id):
    """添加条目到书架"""
    user_id = get_user_id()
    data = request.get_json()
    
    shelf = q(Bookshelf).filter_by(id=shelf_id, user_id=user_id).first()
    if not shelf:
        return jsonify({'success': False, 'error': '书架不存在'}), 404
    
    item_type = data.get('item_type')
    item_id = data.get('item_id')
    
    if not item_type or not item_id:
        return jsonify({'success': False, 'error': '缺少必要参数'}), 400
    
    # 检查是否已存在
    exists = q(BookshelfItem).filter_by(
        bookshelf_id=shelf_id,
        item_type=item_type,
        item_id=item_id
    ).first()
    
    if exists:
        return jsonify({'success': False, 'error': '该内容已在书架中'}), 400
    
    item = BookshelfItem(
        bookshelf_id=shelf_id,
        item_type=item_type,
        item_id=item_id,
        title=data.get('title'),
        author=data.get('author'),
        excerpt=data.get('excerpt'),
        cover_url=data.get('cover_url'),
        note=data.get('note'),
        rating=data.get('rating')
    )
    
    Session().add(item)
    Session().commit()
    
    return jsonify({
        'success': True,
        'item': {
            'id': item.id,
            'item_type': item.item_type,
            'item_id': item.item_id,
            'title': item.title,
            'author': item.author
        }
    })


@library_bp.route('/bookshelves/<shelf_id>/items/<item_id>', methods=['DELETE'])
def remove_shelf_item(shelf_id, item_id):
    """从书架移除条目"""
    user_id = get_user_id()
    
    shelf = q(Bookshelf).filter_by(id=shelf_id, user_id=user_id).first()
    if not shelf:
        return jsonify({'success': False, 'error': '书架不存在'}), 404
    
    item = q(BookshelfItem).filter_by(id=item_id, bookshelf_id=shelf_id).first()
    if not item:
        return jsonify({'success': False, 'error': '条目不存在'}), 404
    
    Session().delete(item)
    Session().commit()
    
    return jsonify({'success': True})


# ═══════════════════════════════════════════════════════════════════
# 金句卡片
# ═══════════════════════════════════════════════════════════════════

@library_bp.route('/golden-quotes', methods=['GET'])
def get_golden_quotes():
    """获取用户的金句卡片"""
    user_id = get_user_id()
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    query = Session.query(GoldenQuote).filter_by(user_id=user_id)\
        .order_by(GoldenQuote.created_at.desc())
    quotes, total = paginate_query(query, page, per_page)
    
    result = []
    for quote in quotes:
        result.append({
            'id': quote.id,
            'content': quote.content,
            'poem_title': quote.poem_title,
            'author': quote.author,
            'style': quote.style,
            'size': quote.size,
            'image_url': quote.image_url,
            'image_prompt': quote.image_prompt,
            'title': quote.title,
            'note': quote.note,
            'tags': quote.tags or [],
            'view_count': quote.view_count,
            'share_count': quote.share_count,
            'created_at': quote.created_at.isoformat() if quote.created_at else None
        })
    
    return jsonify({
        'success': True,
        'quotes': result,
        'total': total,
        'page': page,
        'pages': (total + per_page - 1) // per_page if per_page > 0 else 0
    })


@library_bp.route('/golden-quotes', methods=['POST'])
def create_golden_quote():
    """创建金句卡片"""
    user_id = get_user_id()
    data = request.get_json()
    
    content = data.get('content', '').strip()
    if not content:
        return jsonify({'success': False, 'error': '诗句内容不能为空'}), 400
    
    quote = GoldenQuote(
        user_id=user_id,
        poem_line_id=data.get('poem_line_id'),
        content=content,
        poem_title=data.get('poem_title'),
        author=data.get('author'),
        style=data.get('style', 'classic'),
        size=data.get('size', 'medium'),
        title=data.get('title'),
        note=data.get('note'),
        tags=data.get('tags', [])
    )
    
    Session().add(quote)
    Session().commit()
    
    return jsonify({
        'success': True,
        'quote': {
            'id': quote.id,
            'content': quote.content,
            'poem_title': quote.poem_title,
            'author': quote.author,
            'style': quote.style
        }
    })


@library_bp.route('/golden-quotes/<quote_id>', methods=['GET'])
def get_golden_quote(quote_id):
    """获取金句卡片详情"""
    user_id = get_user_id()
    
    quote = q(GoldenQuote).filter_by(id=quote_id, user_id=user_id).first()
    if not quote:
        return jsonify({'success': False, 'error': '卡片不存在'}), 404
    
    # 增加浏览次数
    quote.view_count += 1
    Session().commit()
    
    return jsonify({
        'success': True,
        'quote': {
            'id': quote.id,
            'content': quote.content,
            'poem_line_id': quote.poem_line_id,
            'poem_title': quote.poem_title,
            'author': quote.author,
            'style': quote.style,
            'size': quote.size,
            'image_url': quote.image_url,
            'image_prompt': quote.image_prompt,
            'title': quote.title,
            'note': quote.note,
            'tags': quote.tags or [],
            'view_count': quote.view_count,
            'share_count': quote.share_count,
            'created_at': quote.created_at.isoformat() if quote.created_at else None
        }
    })


@library_bp.route('/golden-quotes/<quote_id>', methods=['PUT'])
def update_golden_quote(quote_id):
    """更新金句卡片"""
    user_id = get_user_id()
    data = request.get_json()
    
    quote = q(GoldenQuote).filter_by(id=quote_id, user_id=user_id).first()
    if not quote:
        return jsonify({'success': False, 'error': '卡片不存在'}), 404
    
    if 'title' in data:
        quote.title = data['title']
    if 'note' in data:
        quote.note = data['note']
    if 'tags' in data:
        quote.tags = data['tags']
    if 'style' in data:
        quote.style = data['style']
    if 'image_url' in data:
        quote.image_url = data['image_url']
    
    Session().commit()
    
    return jsonify({'success': True, 'quote': {
        'id': quote.id,
        'title': quote.title,
        'note': quote.note
    }})


@library_bp.route('/golden-quotes/<quote_id>', methods=['DELETE'])
def delete_golden_quote(quote_id):
    """删除金句卡片"""
    user_id = get_user_id()
    
    quote = q(GoldenQuote).filter_by(id=quote_id, user_id=user_id).first()
    if not quote:
        return jsonify({'success': False, 'error': '卡片不存在'}), 404
    
    Session().delete(quote)
    Session().commit()
    
    return jsonify({'success': True})


@library_bp.route('/golden-quotes/from-line/<line_id>', methods=['POST'])
def create_quote_from_line(line_id):
    """从诗句创建金句卡片"""
    user_id = get_user_id()
    
    poem_line = q(PoemLine).get(line_id)
    if not poem_line:
        return jsonify({'success': False, 'error': '诗句不存在'}), 404
    
    poem = q(Poem).get(poem_line.poem_id)
    
    quote = GoldenQuote(
        user_id=user_id,
        poem_line_id=line_id,
        content=poem_line.line,
        poem_title=poem.title if poem else None,
        author=poem.author if poem else None,
        style='classic',
        size='medium'
    )
    
    Session().add(quote)
    Session().commit()
    
    return jsonify({
        'success': True,
        'quote': {
            'id': quote.id,
            'content': quote.content,
            'poem_title': quote.poem_title,
            'author': quote.author
        }
    })


# ═══════════════════════════════════════════════════════════════════
# 诗词分类浏览
# ═══════════════════════════════════════════════════════════════════

@library_bp.route('/categories', methods=['GET'])
def get_categories():
    """获取诗词分类"""
    categories = q(PoemCategory).filter_by(active=True, level=1)\
        .order_by(PoemCategory.sort_order).all()
    
    result = []
    for cat in categories:
        children = q(PoemCategory).filter_by(parent_id=cat.id, active=True)\
            .order_by(PoemCategory.sort_order).all()
        
        result.append({
            'id': cat.id,
            'name': cat.name,
            'slug': cat.slug,
            'icon': cat.icon,
            'description': cat.description,
            'poem_count': cat.poem_count,
            'children': [{
                'id': c.id,
                'name': c.name,
                'slug': c.slug,
                'icon': c.icon,
                'poem_count': c.poem_count
            } for c in children]
        })
    
    return jsonify({
        'success': True,
        'categories': result
    })


@library_bp.route('/poems/by-category/<slug>', methods=['GET'])
def get_poems_by_category(slug):
    """按分类获取诗词"""
    category = q(PoemCategory).filter_by(slug=slug, active=True).first()
    if not category:
        return jsonify({'success': False, 'error': '分类不存在'}), 404
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    # 获取该分类及子分类的所有 ID
    category_ids = [category.id]
    children = q(PoemCategory).filter_by(parent_id=category.id, active=True).all()
    category_ids.extend([c.id for c in children])
    
    # TODO: 需要 Poem 表有 category_id 外键
    # poems = q(Poem).filter(Poem.category_id.in_(category_ids))...
    
    # 临时方案：返回该分类信息
    return jsonify({
        'success': True,
        'category': {
            'id': category.id,
            'name': category.name,
            'slug': category.slug,
            'description': category.description
        },
        'poems': [],
        'page': page,
        'pages': 0,
        'total': 0
    })


@library_bp.route('/poems/by-dynasty/<dynasty>', methods=['GET'])
def get_poems_by_dynasty(dynasty):
    """按朝代获取诗词"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    query = Session.query(Poem).filter_by(dynasty=dynasty)
    
    poems, total = paginate_query(query.order_by(Poem.id.desc()), page, per_page)
    
    result = []
    for poem in poems:
        result.append({
            'id': poem.id,
            'title': poem.title,
            'author': poem.author,
            'dynasty': poem.dynasty,
            'content': getattr(poem, 'content', '') or '',
            'tags': getattr(poem, 'tags', []) or []
        })
    
    return jsonify({
        'success': True,
        'dynasty': dynasty,
        'poems': result,
        'page': page,
        'pages': (total + per_page - 1) // per_page if per_page > 0 else 0,
        'total': total
    })


@library_bp.route('/poems/by-author/<author_name>', methods=['GET'])
def get_poems_by_author(author_name):
    """按作者获取诗词"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    query = Session.query(Poem).filter(Poem.author.like(f'%{author_name}%'))
    
    poems, total = paginate_query(query.order_by(Poem.id.desc()), page, per_page)
    
    result = []
    for poem in poems:
        result.append({
            'id': poem.id,
            'title': poem.title,
            'author': poem.author,
            'dynasty': poem.dynasty,
            'content': getattr(poem, 'content', '') or '',
            'tags': getattr(poem, 'tags', []) or []
        })
    
    return jsonify({
        'success': True,
        'author': author_name,
        'poems': result,
        'page': page,
        'pages': (total + per_page - 1) // per_page if per_page > 0 else 0,
        'total': total
    })


@library_bp.route('/authors', methods=['GET'])
def get_authors():
    """获取诗人列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    dynasty = request.args.get('dynasty')
    
    # 使用 Session 执行查询
    query = Session.query(AuthorProfile).filter(AuthorProfile.active == True)
    
    if dynasty:
        query = query.filter(AuthorProfile.dynasty == dynasty)
    
    # 计算总数
    total = query.count()
    
    # 分页
    authors = query.order_by(AuthorProfile.poem_count.desc())\
        .offset((page - 1) * per_page).limit(per_page).all()
    
    result = []
    for author in authors:
        result.append({
            'id': author.id,
            'name': author.name,
            'alias': author.alias,
            'dynasty': author.dynasty,
            'bio': author.bio[:100] + '...' if author.bio and len(author.bio) > 100 else author.bio,
            'avatar_url': author.avatar_url,
            'poem_count': author.poem_count,
            'tags': author.tags or []
        })
    
    return jsonify({
        'success': True,
        'authors': result,
        'page': page,
        'pages': (total + per_page - 1) // per_page if per_page > 0 else 0,
        'total': total
    })


@library_bp.route('/dynasties', methods=['GET'])
def get_dynasties():
    """获取朝代统计"""
    # 统计各朝代诗词数量
    stats = Session.query(
        Poem.dynasty,
        func.count(Poem.id).label('count')
    ).group_by(Poem.dynasty).all()
    
    dynasty_map = {
        '唐': {'icon': '📜', 'order': 1},
        '宋': {'icon': '📖', 'order': 2},
        '元': {'icon': '🎭', 'order': 3},
        '明': {'icon': '🏯', 'order': 4},
        '清': {'icon': '🎋', 'order': 5},
        '汉': {'icon': '⚔️', 'order': 6},
        '魏晋': {'icon': '🍃', 'order': 7},
        '秦': {'icon': '🐴', 'order': 8},
        '隋': {'icon': '🌸', 'order': 9},
        '先秦': {'icon': '🏺', 'order': 0},
    }
    
    result = []
    for dynasty, count in stats:
        info = dynasty_map.get(dynasty, {'icon': '📚', 'order': 99})
        result.append({
            'name': dynasty,
            'icon': info['icon'],
            'count': count,
            'order': info['order']
        })
    
    # 按顺序排序
    result.sort(key=lambda x: x['order'])
    
    return jsonify({
        'success': True,
        'dynasties': result,
        'total_poems': sum(d['count'] for d in result)
    })


# ═══════════════════════════════════════════════════════════════════
# 阅读历史
# ═══════════════════════════════════════════════════════════════════

@library_bp.route('/reading-history', methods=['GET'])
def get_reading_history():
    """获取阅读历史"""
    user_id = get_user_id()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    query = Session.query(ReadingHistory).filter_by(user_id=user_id)\
        .order_by(ReadingHistory.read_at.desc())
    history, total = paginate_query(query, page, per_page)
    
    result = []
    for h in history:
        result.append({
            'id': h.id,
            'item_type': h.item_type,
            'item_id': h.item_id,
            'title': h.title,
            'author': h.author,
            'duration': h.duration,
            'finished': h.finished,
            'read_at': h.read_at.isoformat() if h.read_at else None
        })
    
    return jsonify({
        'success': True,
        'history': result,
        'page': page,
        'pages': (total + per_page - 1) // per_page if per_page > 0 else 0,
        'total': total
    })


@library_bp.route('/reading-history', methods=['POST'])
def add_reading_history():
    """添加阅读记录"""
    user_id = get_user_id()
    data = request.get_json()
    
    item_type = data.get('item_type')
    item_id = data.get('item_id')
    
    if not item_type or not item_id:
        return jsonify({'success': False, 'error': '缺少必要参数'}), 400
    
    # 检查是否已有记录，有则更新
    existing = q(ReadingHistory).filter_by(
        user_id=user_id,
        item_type=item_type,
        item_id=item_id
    ).first()
    
    if existing:
        existing.duration = data.get('duration', existing.duration + 10)
        existing.finished = data.get('finished', existing.finished)
        existing.read_at = func.now()
    else:
        history = ReadingHistory(
            user_id=user_id,
            item_type=item_type,
            item_id=item_id,
            title=data.get('title'),
            author=data.get('author'),
            duration=data.get('duration', 0),
            finished=data.get('finished', False)
        )
        Session().add(history)
    
    Session().commit()
    
    return jsonify({'success': True})


# ═══════════════════════════════════════════════════════════════════
# 搜索
# ═══════════════════════════════════════════════════════════════════

@library_bp.route('/search', methods=['GET'])
def search_library():
    """搜索藏书阁"""
    user_id = get_user_id()
    keyword = request.args.get('q', '').strip()
    
    if not keyword:
        return jsonify({'success': True, 'results': {
            'poems': [],
            'golden_quotes': [],
            'authors': []
        }})
    
    results = {
        'poems': [],
        'golden_quotes': [],
        'authors': []
    }
    
    # 搜索诗词
    poems = q(Poem).filter(
        or_(
            Poem.title.like(f'%{keyword}%'),
            Poem.author.like(f'%{keyword}%'),
            Poem.content.like(f'%{keyword}%')
        )
    ).limit(10).all()
    
    for poem in poems:
        results['poems'].append({
            'id': poem.id,
            'title': poem.title,
            'author': poem.author,
            'dynasty': poem.dynasty,
            'excerpt': poem.content[:50] + '...' if poem.content and len(poem.content) > 50 else poem.content
        })
    
    # 搜索金句卡片
    quotes = q(GoldenQuote).filter_by(user_id=user_id).filter(
        or_(
            GoldenQuote.content.like(f'%{keyword}%'),
            GoldenQuote.title.like(f'%{keyword}%'),
            GoldenQuote.note.like(f'%{keyword}%')
        )
    ).limit(10).all()
    
    for quote in quotes:
        results['golden_quotes'].append({
            'id': quote.id,
            'content': quote.content,
            'poem_title': quote.poem_title,
            'author': quote.author,
            'image_url': quote.image_url
        })
    
    # 搜索诗人
    authors = q(AuthorProfile).filter(
        or_(
            AuthorProfile.name.like(f'%{keyword}%'),
            AuthorProfile.alias.like(f'%{keyword}%')
        )
    ).limit(10).all()
    
    for author in authors:
        results['authors'].append({
            'id': author.id,
            'name': author.name,
            'alias': author.alias,
            'dynasty': author.dynasty,
            'poem_count': author.poem_count
        })
    
    return jsonify({
        'success': True,
        'keyword': keyword,
        'results': results
    })


# ═══════════════════════════════════════════════════════════════════
# 统计
# ═══════════════════════════════════════════════════════════════════

@library_bp.route('/stats', methods=['GET'])
def get_library_stats():
    """获取藏书阁统计"""
    user_id = get_user_id()
    
    # 书架数
    shelf_count = q(Bookshelf).filter_by(user_id=user_id).count()
    
    # 金句卡片数
    quote_count = q(GoldenQuote).filter_by(user_id=user_id).count()
    
    # 总收藏数
    collection_count = q(BookshelfItem).join(Bookshelf).filter(
        Bookshelf.user_id == user_id
    ).count()
    
    # 阅读时长（分钟）
    total_duration = Session.query(func.sum(ReadingHistory.duration))\
        .filter_by(user_id=user_id).scalar() or 0
    
    return jsonify({
        'success': True,
        'stats': {
            'shelf_count': shelf_count,
            'quote_count': quote_count,
            'collection_count': collection_count,
            'total_reading_minutes': round(total_duration / 60, 1)
        }
    })
