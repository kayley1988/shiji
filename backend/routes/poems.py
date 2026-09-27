"""
诗词 API 路由
"""
import os
import random
from datetime import datetime
from flask import Blueprint, request, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker, scoped_session

from config import ART_PROMPTS
from models import Poem, PoemLine, Tag, PoemLineTag, ReviewStatus
from nlp.char_convert import to_simplified

poems_bp = Blueprint('poems', __name__, url_prefix='/v1/poems')

# ---------- 真实数据库读取（shiyayaji.db） ----------
_engine = create_engine('sqlite:///' + os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'shiyayaji.db'))
DBSession = scoped_session(sessionmaker(bind=_engine))


def _format_content(lines_text):
    """两句一组拼正文：A，B。C，D。"""
    parts = []
    for i in range(0, len(lines_text), 2):
        parts.append('，'.join(lines_text[i:i + 2]) + '。')
    return ''.join(parts)


def _poem_from_db(poem_id):
    """从真库读诗，返回与旧 mock 同构的 dict；查不到返回 None"""
    db = DBSession()
    try:
        p = db.query(Poem).filter(Poem.id == poem_id).first()
        if not p:
            return None
        lines = db.query(PoemLine).filter(PoemLine.poem_id == poem_id) \
            .order_by(PoemLine.line_no).all()
        lines_text = [to_simplified(l.content) for l in lines if l.content]
        if not lines_text:
            return None
        tag_names = [r[0] for r in db.query(Tag.name)
                     .join(PoemLineTag, PoemLineTag.tag_id == Tag.id)
                     .join(PoemLine, PoemLine.id == PoemLineTag.poem_line_id)
                     .filter(PoemLine.poem_id == poem_id).all()]
        seen, tags = set(), []
        for t in tag_names:
            if t not in seen:
                seen.add(t)
                tags.append(t)
        return {
            'id': p.id,
            'title': to_simplified(p.title or ''),
            'author': to_simplified(p.author or ''),
            'dynasty': p.dynasty or '',
            'content': _format_content(lines_text),
            'full_text': '\n'.join(lines_text),
            # 逐句原文（保留繁体，前端做繁/简双栏）
            'lines': [{'content': l.content, 'line_no': l.line_no}
                      for l in lines if l.content],
            'tags': tags,
            'imagery': tags[:6],
            'is_rare': any(bool(l.is_rare) for l in lines),
            'difficulty': 'medium',
        }
    except Exception:
        return None
    finally:
        db.close()

# 模拟诗词数据库
POEMS_DB = [
    {
        'id': 'p001',
        'title': '春晓',
        'author': '孟浩然',
        'dynasty': '唐',
        'content': '春眠不觉晓，处处闻啼鸟。夜来风雨声，花落知多少。',
        'full_text': '春眠不觉晓，处处闻啼鸟。\n夜来风雨声，花落知多少。',
        'tags': ['春', '惜春', '梦境'],
        'imagery': ['春', '鸟', '雨', '花', '风'],
        'is_rare': False,
        'difficulty': 'easy'
    },
    {
        'id': 'p002',
        'title': '静夜思',
        'author': '李白',
        'dynasty': '唐',
        'content': '床前明月光，疑是地上霜。举头望明月，低头思故乡。',
        'full_text': '床前明月光，疑是地上霜。\n举头望明月，低头思故乡。',
        'tags': ['思乡', '月夜', '静谧'],
        'imagery': ['月', '霜', '光', '乡'],
        'is_rare': False,
        'difficulty': 'easy'
    },
    {
        'id': 'p003',
        'title': '登鹳雀楼',
        'author': '王之涣',
        'dynasty': '唐',
        'content': '白日依山尽，黄河入海流。欲穷千里目，更上一层楼。',
        'full_text': '白日依山尽，黄河入海流。\n欲穷千里目，更上一层楼。',
        'tags': ['登高', '望远', '哲理'],
        'imagery': ['日', '山', '河', '海', '楼'],
        'is_rare': False,
        'difficulty': 'easy'
    },
    {
        'id': 'p004',
        'title': '相思',
        'author': '王维',
        'dynasty': '唐',
        'content': '红豆生南国，春来发几枝。愿君多采撷，此物最相思。',
        'full_text': '红豆生南国，春来发几枝。\n愿君多采撷，此物最相思。',
        'tags': ['相思', '红豆', '爱情'],
        'imagery': ['红豆', '春', '南'],
        'is_rare': True,
        'difficulty': 'medium'
    },
    {
        'id': 'p005',
        'title': '黄鹤楼送孟浩然之广陵',
        'author': '李白',
        'dynasty': '唐',
        'content': '故人西辞黄鹤楼，烟花三月下扬州。孤帆远影碧空尽，唯见长江天际流。',
        'full_text': '故人西辞黄鹤楼，烟花三月下扬州。\n孤帆远影碧空尽，唯见长江天际流。',
        'tags': ['送别', '友情', '黄鹤楼'],
        'imagery': ['鹤', '楼', '帆', '江', '烟'],
        'is_rare': False,
        'difficulty': 'medium'
    },
    {
        'id': 'p006',
        'title': '枫桥夜泊',
        'author': '张继',
        'dynasty': '唐',
        'content': '月落乌啼霜满天，江枫渔火对愁眠。姑苏城外寒山寺，夜半钟声到客船。',
        'full_text': '月落乌啼霜满天，江枫渔火对愁眠。\n姑苏城外寒山寺，夜半钟声到客船。',
        'tags': ['羁旅', '愁思', '夜景'],
        'imagery': ['月', '乌', '霜', '江', '枫', '钟', '船'],
        'is_rare': True,
        'difficulty': 'hard'
    },
    {
        'id': 'p007',
        'title': '出塞',
        'author': '王昌龄',
        'dynasty': '唐',
        'content': '秦时明月汉时关，万里长征人未还。但使龙城飞将在，不教胡马度阴山。',
        'full_text': '秦时明月汉时关，万里长征人未还。\n但使龙城飞将在，不教胡马度阴山。',
        'tags': ['边塞', '战争', '家国'],
        'imagery': ['月', '关', '龙', '胡', '山'],
        'is_rare': False,
        'difficulty': 'medium'
    },
    {
        'id': 'p008',
        'title': '江雪',
        'author': '柳宗元',
        'dynasty': '唐',
        'content': '千山鸟飞绝，万径人踪灭。孤舟蓑笠翁，独钓寒江雪。',
        'full_text': '千山鸟飞绝，万径人踪灭。\n孤舟蓑笠翁，独钓寒江雪。',
        'tags': ['隐逸', '孤独', '冬景'],
        'imagery': ['山', '鸟', '雪', '江', '舟'],
        'is_rare': False,
        'difficulty': 'easy'
    },
    {
        'id': 'p009',
        'title': '游子吟',
        'author': '孟郊',
        'dynasty': '唐',
        'content': '慈母手中线，游子身上衣。临行密密缝，意恐迟迟归。谁言寸草心，报得三春晖。',
        'full_text': '慈母手中线，游子身上衣。\n临行密密缝，意恐迟迟归。\n谁言寸草心，报得三春晖。',
        'tags': ['母爱', '亲情', '游子'],
        'imagery': ['母', '线', '衣', '草', '春'],
        'is_rare': True,
        'difficulty': 'medium'
    },
    {
        'id': 'p010',
        'title': '清明',
        'author': '杜牧',
        'dynasty': '唐',
        'content': '清明时节雨纷纷，路上行人欲断魂。借问酒家何处有，牧童遥指杏花村。',
        'full_text': '清明时节雨纷纷，路上行人欲断魂。\n借问酒家何处有，牧童遥指杏花村。',
        'tags': ['清明', '雨景', '思乡'],
        'imagery': ['雨', '酒', '杏花', '村'],
        'is_rare': False,
        'difficulty': 'easy'
    }
]

EXPLANATIONS = {
    'p001': '诗人用浅显易懂的语言，描绘了春天早晨的景象，表达了对春光易逝的惋惜之情。全诗平实自然，却意境深远。',
    'p002': '望月思乡，是李白最著名的思乡诗之一。语言朴素而情感深挚，千年来广为传诵。',
    'p003': '诗人登楼远眺，写出了壮阔的景象，并以「欲穷千里目，更上一层楼」表达积极进取的精神。',
    'p004': '借红豆寄托相思之情，是爱情诗中的经典。以物喻情，含蓄深永。',
    'p005': '送别诗的绝唱，将离别的情感融入壮美的江景之中，意境开阔而情深意长。',
}


@poems_bp.route('', methods=['GET'])
def list_poems():
    """获取诗句列表"""
    keyword = request.args.get('keyword')
    author = request.args.get('author')
    dynasty = request.args.get('dynasty')
    tags = request.args.getlist('tags')
    limit = request.args.get('limit', 20, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    poems = POEMS_DB
    
    # 过滤
    if keyword:
        poems = [p for p in poems if keyword in p['content'] or keyword in p['title']]
    if author:
        poems = [p for p in poems if author in p['author']]
    if dynasty:
        poems = [p for p in poems if dynasty in p['dynasty']]
    if tags:
        poems = [p for p in poems if any(t in p['tags'] for t in tags)]
    
    total = len(poems)
    poems = poems[offset:offset+limit]
    
    return jsonify({
        'data': {
            'poems': poems,
            'total': total,
            'limit': limit,
            'offset': offset
        }
    })


@poems_bp.route('/<poem_id>', methods=['GET'])
def get_poem(poem_id):
    """获取诗句详情（优先真实数据库，兼容旧 mock ID）"""
    poem = _poem_from_db(poem_id) or next((p for p in POEMS_DB if p['id'] == poem_id), None)

    if not poem:
        return jsonify({'error': 'POEM_NOT_FOUND'}), 404

    return jsonify({'data': poem})


@poems_bp.route('/<poem_id>/explanation', methods=['GET'])
def get_poem_explanation(poem_id):
    """获取诗句赏析"""
    poem = _poem_from_db(poem_id) or next((p for p in POEMS_DB if p['id'] == poem_id), None)

    if not poem:
        return jsonify({'error': 'POEM_NOT_FOUND'}), 404

    explanation = EXPLANATIONS.get(poem_id, f'这首{poem["dynasty"]}诗表达了诗人独特的情感和意境，值得细细品味。')

    return jsonify({
        'data': {
            'poem_id': poem_id,
            'title': poem['title'],
            'author': poem['author'],
            'author_intro': f'{poem["author"]}（{poem["dynasty"]}），一代著名诗人。' if poem['dynasty'] else f'{poem["author"]}，一代著名诗人。',
            'explanation': explanation,
            'keywords': poem['tags'],
            'imagery': poem['imagery'],
            'writing_skills': [
                '情景交融，借景抒情',
                '语言精炼，意境深远',
                '情感真挚，感人至深'
            ]
        }
    })


@poems_bp.route('/random', methods=['GET'])
def get_random_poem():
    """获取随机诗句（真实数据库）"""
    keyword = request.args.get('keyword')
    difficulty = request.args.get('difficulty')

    poem = None
    db = DBSession()
    try:
        q = db.query(Poem.id)
        if keyword:
            like = f'%{keyword.strip()}%'
            line_ids = [r[0] for r in db.query(PoemLine.poem_id)
                        .filter(PoemLine.normalized_content.like(like))
                        .limit(5000).all()]
            if line_ids:
                q = q.filter(Poem.id.in_(line_ids))
            else:
                q = None
        if q is not None:
            pid = q.order_by(func.random()).limit(1).first()
            if pid:
                poem = _poem_from_db(pid[0])
    except Exception:
        poem = None
    finally:
        db.close()

    if not poem:
        poems = [p for p in POEMS_DB if (not keyword or keyword in p['content'])]
        if difficulty:
            poems = [p for p in poems if p['difficulty'] == difficulty]
        poem = random.choice(poems or POEMS_DB)

    return jsonify({'data': poem})


@poems_bp.route('/daily', methods=['GET'])
def get_daily_poem():
    """获取每日推荐（真实数据库，按日期种子固定）"""
    today = datetime.now()
    seed = today.year * 10000 + today.month * 100 + today.day

    poem = None
    db = DBSession()
    try:
        total = db.query(func.count(Poem.id)).scalar() or 0
        if total:
            p = db.query(Poem).order_by(Poem.id).offset(seed % total).first()
            if p:
                poem = _poem_from_db(p.id)
    except Exception:
        poem = None
    finally:
        db.close()

    if not poem:
        random.seed(seed)
        poem = random.choice(POEMS_DB)
        random.seed()  # 重置随机种子

    return jsonify({
        'data': {
            **poem,
            'date': today.strftime('%Y-%m-%d'),
            'reason': f'今日精选 · {poem["tags"][0] if poem["tags"] else "经典"}'
        }
    })


@poems_bp.route('/generate-prompt', methods=['POST'])
def generate_prompt():
    """生成生图提示词"""
    data = request.get_json() or {}
    
    poem_id = data.get('poem_id')
    style = data.get('style', 'shuimo')
    
    poem = next((p for p in POEMS_DB if p['id'] == poem_id), None)
    
    if not poem:
        return jsonify({'error': 'POEM_NOT_FOUND'}), 404
    
    # 构建提示词
    style_prefixes = {
        'shuimo': 'Traditional Chinese ink wash painting (Shuimo), minimalist black ink on rice paper',
        'gongbi': 'Traditional Chinese Gongbi fine painting, delicate brushwork, vibrant colors',
        'dunhuang': 'Dunhuang cave fresco style, vibrant colors, Buddhist art influence',
        'modern': 'Modern Chinese art fusion, contemporary interpretation'
    }
    
    style_prefix = style_prefixes.get(style, style_prefixes['shuimo'])
    
    prompt = f"""
{style_prefix}.

Poetry: {poem['full_text'].replace(chr(10), '，')}

Title: {poem['title']}
Author: {poem['author']} ({poem['dynasty']} Dynasty)

Requirements:
- Traditional Chinese art style
- Serene, contemplative atmosphere
- High quality illustration
- No text in the image
- Inspired by classical Chinese aesthetics
""".strip()
    
    return jsonify({
        'data': {
            'poem_id': poem_id,
            'style': style,
            'prompt': prompt,
            'preview_url': None
        }
    })


@poems_bp.route('/polaroid-templates', methods=['GET'])
def get_polaroid_templates():
    """获取拍立得边框模板"""
    templates = [
        {
            'id': 'classic',
            'name': '经典拍立得',
            'description': '纯白边框，简约经典',
            'frame_color': '#f5f5f5',
            'border_width': 12,
            'shadow': True
        },
        {
            'id': 'vintage',
            'name': '复古胶片',
            'description': '米色做旧效果，时光感',
            'frame_color': '#e8dcc8',
            'border_width': 16,
            'shadow': True,
            'tilt': -2
        },
        {
            'id': 'ink',
            'name': '水墨古卷',
            'description': '宣纸质感，水墨边框',
            'frame_color': '#f8f4e8',
            'border_width': 20,
            'shadow': False
        },
        {
            'id': 'modern',
            'name': '现代简约',
            'description': '窄边框，时尚设计',
            'frame_color': '#ffffff',
            'border_width': 8,
            'shadow': True
        }
    ]
    
    return jsonify({'data': templates})
