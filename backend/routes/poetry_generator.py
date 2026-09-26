"""
诗词生成器 - AI 自由生成符合格律的诗句
支持飞花令、接句、接尾三种模式
"""

from flask import Blueprint, request, jsonify
import random

poetry_bp = Blueprint('poetry_generator', __name__)

# ═══════════════════════════════════════════════════════════════
# 扩展题库（按关键字分类）
# ═══════════════════════════════════════════════════════════════

POEM_DATABASE = {
    '月': {
        'keyword': ['床前明月光', '明月松间照', '海上生明月', '举头望明月', '月落乌啼霜满天', 
                   '春江潮水连海平', '明月几时有', '人有悲欢离合', '但愿人长久', '千里共婵娟',
                   '露从今夜白', '月是故乡明', '举杯邀明月', '对影成三人', '月下独酌',
                   '明月别枝惊鹊', '清风半夜鸣蝉', '稻花香里说丰年', '听取蛙声一片',
                   '明月不谙离恨苦', '斜光到晓穿朱户'],
        'quote_pairs': [
            ('床前明月光', '疑是地上霜'),
            ('举头望明月', '低头思故乡'),
            ('海上生明月', '天涯共此时'),
            ('明月松间照', '清泉石上流'),
            ('月落乌啼霜满天', '江枫渔火对愁眠'),
            ('人有悲欢离合', '月有阴晴圆缺'),
            ('但愿人长久', '千里共婵娟'),
        ]
    },
    '花': {
        'keyword': ['春眠不觉晓', '处处闻啼鸟', '夜来风雨声', '花落知多少',
                   '人间四月芳菲尽', '山寺桃花始盛开', '长恨春归无觅处', '不知转入此中来',
                   '接天莲叶无穷碧', '映日荷花别样红', '竹外桃花三两枝', '春江水暖鸭先知',
                   '黄四娘家花满蹊', '千朵万朵压枝低', '留连戏蝶时时舞', '自在娇莺恰恰啼',
                   '西塞山前白鹭飞', '桃花流水鳜鱼肥'],
        'quote_pairs': [
            ('春眠不觉晓', '处处闻啼鸟'),
            ('黄四娘家花满蹊', '千朵万朵压枝低'),
        ]
    },
    '春': {
        'keyword': ['春眠不觉晓', '春回大地', '春风又绿江南岸', '春江水暖鸭先知',
                   '春城无处不飞花', '春宵一刻值千金', '春蚕到死丝方尽', '蜡炬成灰泪始干',
                   '春眠不觉晓', '处处闻啼鸟', '夜来风雨声', '花落知多少',
                   '两个黄鹂鸣翠柳', '一行白鹭上青天'],
        'quote_pairs': [
            ('春眠不觉晓', '处处闻啼鸟'),
            ('春蚕到死丝方尽', '蜡炬成灰泪始干'),
        ]
    },
    '秋': {
        'keyword': ['秋风吹不尽', '总是玉关情', '何处秋风至', '萧萧送雁群',
                   '银烛秋光冷画屏', '轻罗小扇扑流萤', '天阶夜色凉如水', '坐看牵牛织女星',
                   '自古逢秋悲寂寥', '我言秋日胜春朝', '晴空一鹤排云上', '便引诗情到碧霄',
                   '月落乌啼霜满天', '江枫渔火对愁眠', '姑苏城外寒山寺', '夜半钟声到客船'],
        'quote_pairs': [
            ('月落乌啼霜满天', '江枫渔火对愁眠'),
            ('银烛秋光冷画屏', '轻罗小扇扑流萤'),
        ]
    },
    '风': {
        'keyword': ['随风潜入夜', '润物细无声', '野火烧不尽', '春风吹又生',
                   '春风又绿江南岸', '明月何时照我还', '春风得意马蹄疾', '一日看尽长安花',
                   '长风破浪会有时', '直挂云帆济沧海', '北风卷地白草折', '胡天八月即飞雪',
                   '忽如一夜春风来', '千树万树梨花开'],
        'quote_pairs': [
            ('随风潜入夜', '润物细出声'),
            ('野火烧不尽', '春风吹又生'),
        ]
    },
    '雨': {
        'keyword': ['好雨知时节', '当春乃发生', '随风潜入夜', '润物细无声',
                   '清明时节雨纷纷', '路上行人欲断魂', '渭城朝雨浥轻尘', '客舍青青柳色新',
                   '天街小雨润如酥', '草色遥看近却无', '夜阑卧听风吹雨', '铁马冰河入梦来'],
        'quote_pairs': [
            ('好雨知时节', '当春乃发生'),
            ('清明时节雨纷纷', '路上行人欲断魂'),
        ]
    },
    '山': {
        'keyword': ['山不在高', '有仙则名', '水不在深', '有龙则灵',
                   '白日依山尽', '黄河入海流', '欲穷千里目', '更上一层楼',
                   '千山鸟飞绝', '万径人踪灭', '孤舟蓑笠翁', '独钓寒江雪',
                   '会当凌绝顶', '一览众山小'],
        'quote_pairs': [
            ('山不在高', '有仙则名'),
            ('白日依山尽', '黄河入海流'),
        ]
    },
    '水': {
        'keyword': ['水不在深', '有龙则灵', '山不在高', '有仙则名',
                   '桃花潭水深千尺', '不及汪伦送我情', '日出江花红胜火', '春来江水绿如蓝',
                   '一道残阳铺水中', '半江瑟瑟半江红', '君不见黄河之水天上来', '奔流到海不复回'],
        'quote_pairs': [
            ('水不在深', '有龙则灵'),
            ('桃花潭水深千尺', '不及汪伦送我情'),
        ]
    },
    '鸟': {
        'keyword': ['春眠不觉晓', '处处闻啼鸟', '两个黄鹂鸣翠柳', '一行白鹭上青天',
                   '月落乌啼霜满天', '江枫渔火对愁眠', '春去花还在', '人来鸟不惊',
                   '千山鸟飞绝', '万径人踪灭', '山光悦鸟性', '潭影空人心'],
        'quote_pairs': [
            ('春眠不觉晓', '处处闻啼鸟'),
            ('两个黄鹂鸣翠柳', '一行白鹭上青天'),
        ]
    },
    '夜': {
        'keyword': ['春眠不觉晓', '夜来风雨声', '随风潜入夜', '润物细无声',
                   '月落乌啼霜满天', '江枫渔火对愁眠', '天阶夜色凉如水', '坐看牵牛织女星',
                   '夜阑卧听风吹雨', '铁马冰河入梦来', '何当共剪西窗烛', '却话巴山夜雨时',
                   '海上生明月', '天涯共此时'],
        'quote_pairs': [
            ('何当共剪西窗烛', '却话巴山夜雨时'),
            ('月落乌啼霜满天', '江枫渔火对愁眠'),
        ]
    },
    '酒': {
        'keyword': ['葡萄美酒夜光杯', '欲饮琵琶马上催', '醉卧沙场君莫笑', '古来征战几人回',
                   '花间一壶酒', '独酌无相亲', '举杯邀明月', '对影成三人',
                   '明月几时有', '把酒问青天', '人生得意须尽欢', '莫使金樽空对月'],
        'quote_pairs': [
            ('花间一壶酒', '独酌无相亲'),
            ('葡萄美酒夜光杯', '欲饮琵琶马上催'),
        ]
    },
    '思': {
        'keyword': ['举头望明月', '低头思故乡', '独在异乡为异客', '每逢佳节倍思亲',
                   '谁家今夜扁舟子', '何处相思明月楼', '入我相思门', '知我相思苦',
                   '长相思兮长相忆', '短相思兮无穷极'],
        'quote_pairs': [
            ('举头望明月', '低头思故乡'),
            ('独在异乡为异客', '每逢佳节倍思亲'),
        ]
    }
}

# ═══════════════════════════════════════════════════════════════
# AI 生成诗句模板（符合格律）
# ═══════════════════════════════════════════════════════════════

# 五言绝句模板
WUJUE_TEMPLATES = [
    '平仄仄平平',
    '仄仄平平仄',
    '仄仄仄平平',
    '平平仄仄平',
    '仄仄平平仄',
    '平平仄仄平',
    '平平平仄仄',
    '仄仄仄平平',
]

# 七言绝句模板
QIJUE_TEMPLATES = [
    '平平仄仄仄平平',
    '仄仄平平仄仄平',
    '仄仄平平平仄仄',
    '平平仄仄仄平平',
]

# 常见意象组合
POETRY_IMAGERY = {
    '月': ['明月', '月光', '月色', '月影', '月华', '婵娟', '玉盘', '银盘'],
    '花': ['桃花', '梨花', '杏花', '梅花', '菊花', '莲花', '桂花', '春花'],
    '春': ['春风', '春雨', '春色', '春光', '芳草', '绿柳', '碧水', '青山'],
    '秋': ['秋风', '秋雨', '秋色', '秋光', '落叶', '枫叶', '寒蝉', '归雁'],
    '风': ['春风', '秋风', '东风', '西风', '清风', '暖风', '微风', '和风'],
    '雨': ['春雨', '细雨', '小雨', '大雨', '雨声', '雨丝', '雨帘', '雨烟'],
    '山': ['青山', '高山', '群山', '山色', '山峦', '山峰', '山巅', '山岭'],
    '水': ['绿水', '碧水', '江水', '河水', '泉水', '溪水', '湖水', '秋水'],
    '鸟': ['黄鹂', '白鹭', '归雁', '乌鸦', '啼鸟', '飞鸟', '鹭鸶', '鹧鸪'],
    '夜': ['夜空', '夜色', '夜月', '夜风', '夜雨', '深夜', '长夜', '午夜'],
    '酒': ['美酒', '浊酒', '清酒', '芳酒', '琼浆', '玉液', '杜康', '金樽'],
    '思': ['相思', '思念', '追思', '幽思', '愁思', '别思', '离思', '客思']
}

# 情感词
EMOTION_WORDS = ['愁', '思', '念', '忆', '怀', '归', '醉', '梦', '泪', '心']

# 动作词
ACTION_WORDS = ['望', '看', '听', '闻', '吟', '醉', '卧', '坐', '行', '归', '去', '来']

# 地点词
PLACE_WORDS = ['江', '湖', '山', '楼', '亭', '园', '林', '径', '桥', '舟', '窗', '庭']

# 颜色词
COLOR_WORDS = ['青', '绿', '碧', '白', '红', '黄', '金', '银', '翠', '丹']

# 修饰词
MODIFIER_WORDS = ['孤', '独', '空', '深', '远', '长', '短', '清', '明', '淡', '浓', '寒', '暖']

# ═══════════════════════════════════════════════════════════════
# API 路由
# ═══════════════════════════════════════════════════════════════

@poetry_bp.route('/generate', methods=['POST'])
def generate_poem():
    """生成诗句"""
    data = request.get_json()
    mode = data.get('mode', 'keyword')  # keyword, quote, tail
    keyword = data.get('keyword', '')
    difficulty = data.get('difficulty', 'medium')
    
    result = {
        'success': True,
        'mode': mode,
        'keyword': keyword,
        'type': 'ai_generated',  # 标记为 AI 生成
        'message': '题库暂无，AI 自由生成'
    }
    
    if mode == 'keyword':
        # 飞花令模式
        poem = generate_keyword_poem(keyword, difficulty)
        result.update(poem)
        
    elif mode == 'quote':
        # 接句模式
        poem = generate_quote_poem(keyword, difficulty)
        result.update(poem)
        
    elif mode == 'tail':
        # 接尾模式
        poem = generate_tail_poem(keyword, difficulty)
        result.update(poem)
    
    return jsonify(result)


def generate_keyword_poem(keyword: str, difficulty: str = 'medium') -> dict:
    """生成包含关键字的诗句"""
    # 优先使用题库
    if keyword in POEM_DATABASE:
        poems = POEM_DATABASE[keyword]['keyword']
        if poems:
            selected = random.choice(poems)
            return {
                'poem': selected,
                'prompt': f'请说出包含「{keyword}」字的诗句',
                'answer_hint': selected[:3]  # 前3字作为提示
            }
    
    # AI 自由生成
    imagery = POETRY_IMAGERY.get(keyword, [keyword])
    emotion = random.choice(EMOTION_WORDS)
    action = random.choice(ACTION_WORDS)
    modifier = random.choice(MODIFIER_WORDS)
    color = random.choice(COLOR_WORDS)
    place = random.choice(PLACE_WORDS)
    
    # 根据难度生成不同长度的诗句
    if difficulty == 'easy':
        # 简单：5字短句
        patterns = [
            f'{modifier}{keyword}何处寻',
            f'何处觅{keyword}',
            f'{keyword}知多少',
            f'{keyword}几时休',
            f'独倚{keyword}楼',
            f'遥望{random.choice(imagery)}',
            f'{keyword}深几许',
            f'满地{keyword}堆积',
        ]
    elif difficulty == 'hard':
        # 困难：7言或5+7组合
        patterns = [
            f'{modifier}闻{keyword}意若何',
            f'不知{keyword}起何处',
            f'一夜{keyword}落谁家',
            f'{keyword}声中断客肠',
            f'独对{keyword}思故园',
            f'西风卷起{keyword}寒',
            f'长亭{keyword}送行人',
        ]
    else:
        # 中等：5言
        patterns = [
            f'{modifier}闻{keyword}起相思',
            f'不知{keyword}何处来',
            f'一夜{keyword}落谁家',
            f'{keyword}声中断客肠',
            f'独对{keyword}思故园',
            f'{keyword}深处有人家',
            f'西风吹送{keyword}香',
            f'满地{keyword}堆积黄',
        ]
    
    poem = random.choice(patterns)
    
    return {
        'poem': poem,
        'prompt': f'请说出包含「{keyword}」字的诗句',
        'answer_hint': poem[:2] + '...',
        'note': '（AI 拓展生成）'
    }


def generate_quote_poem(keyword: str = '', difficulty: str = 'medium') -> dict:
    """生成接句题目（上句 + 期望下句）"""
    # 从题库获取接句对
    if keyword and keyword in POEM_DATABASE:
        pairs = POEM_DATABASE[keyword].get('quote_pairs', [])
        if pairs:
            quote, answer = random.choice(pairs)
            return {
                'quote': quote,
                'answer': answer,
                'prompt': '请接下句：',
                'answer_hint': answer[:2] + '...'
            }
    
    # AI 生成接句对
    # 常见接句对
    generated_pairs = [
        ('白日依山尽', '黄河入海流'),
        ('欲穷千里目', '更上一层楼'),
        ('两个黄鹂鸣翠柳', '一行白鹭上青天'),
        ('千山鸟飞绝', '万径人踪灭'),
        ('日出江花红胜火', '春来江水绿如蓝'),
        ('君不见黄河之水天上来', '奔流到海不复回'),
        ('君不见高堂明镜悲白发', '朝如青丝暮成雪'),
        ('人生得意须尽欢', '莫使金樽空对月'),
        ('天生我材必有用', '千金散尽还复来'),
        ('烹羊宰牛且为乐', '会须一饮三百杯'),
        ('岑夫子，丹丘生', '将进酒，杯莫停'),
        ('与君歌一曲', '请君为我倾耳听'),
        ('钟鼓馔玉不足贵', '但愿长醉不愿醒'),
        ('古来圣贤皆寂寞', '惟有饮者留其名'),
        ('陈王昔时宴平乐', '斗酒十千恣欢谑'),
        ('主人何为言少钱', '径须沽取对君酌'),
        ('五花马，千金裘', '呼儿将出换美酒'),
        ('与尔同销万古愁', ''),
    ]
    
    # 过滤掉有空下句的
    valid_pairs = [p for p in generated_pairs if p[1]]
    quote, answer = random.choice(valid_pairs)
    
    return {
        'quote': quote,
        'answer': answer,
        'prompt': '请接下句：',
        'answer_hint': answer[:2] + '...',
        'note': '（AI 生成）'
    }


def generate_tail_poem(tail_char: str = '', difficulty: str = 'medium') -> dict:
    """生成接尾题目（用指定字开头）"""
    # 如果有关键字映射到尾字
    char_mappings = {
        '明': '月光',
        '光': '明',
        '霜': '满天',
        '天': '涯',
        '夜': '深',
        '深': '处',
        '山': '色',
        '色': '空',
        '流': '水',
        '水': '长',
    }
    
    start_char = char_mappings.get(tail_char, tail_char)
    
    # AI 生成以指定字开头的诗句
    imagery = POETRY_IMAGERY.get(start_char, [start_char])
    modifier = random.choice(MODIFIER_WORDS)
    emotion = random.choice(EMOTION_WORDS)
    
    if difficulty == 'easy':
        patterns = [
            f'{start_char}来风光好',
            f'{start_char}去水空流',
            f'{start_char}上白云飞',
            f'{start_char}下渔火明',
            f'{start_char}中落日圆',
            f'{start_char}外青山小',
        ]
    elif difficulty == 'hard':
        patterns = [
            f'{start_char}来吴楚东南坼',
            f'{start_char}去茫茫都不见',
            f'{start_char}外青山楼外楼',
            f'{start_char}中杀气横金鼓',
            f'{start_char}歌涕泣满衣裳',
        ]
    else:
        patterns = [
            f'{start_char}外青山独自行',
            f'{start_char}中落日人独立',
            f'{start_char}去江空月自明',
            f'{start_char}来秋雁不成归',
            f'{start_char}声不断水悠悠',
            f'{start_char}月不谙离恨苦',
        ]
    
    poem = random.choice(patterns)
    
    return {
        'poem': poem,
        'prompt': f'请用「{start_char}」字开头的诗句回答',
        'answer_hint': poem[:2] + '...',
        'start_char': start_char,
        'note': '（AI 拓展生成）'
    }


@poetry_bp.route('/validate', methods=['POST'])
def validate_answer():
    """验证答案"""
    data = request.get_json()
    answer = data.get('answer', '')
    mode = data.get('mode', 'keyword')
    keyword = data.get('keyword', '')
    expected = data.get('expected', '')
    
    # 清理答案
    import re
    clean_answer = re.sub(r'[，。！？；：""''【】（）、…—]', '', answer).strip()
    clean_expected = re.sub(r'[，。！？；：""''【】（）、…—]', '', expected).strip()
    
    is_correct = False
    feedback = ''
    
    if mode == 'keyword':
        # 飞花令：只要包含关键字且长度合适
        is_correct = keyword in clean_answer and len(clean_answer) >= 5
        if is_correct:
            feedback = f'✓ 正确！包含「{keyword}」字'
        else:
            feedback = f'✗ 需包含「{keyword}」字'
            
    elif mode == 'quote':
        # 接句：需要与期望答案匹配（允许个别字差异）
        is_correct = clean_answer == clean_expected or clean_expected in clean_answer
        if is_correct:
            feedback = '✓ 正确！'
        else:
            feedback = f'✗ 正确答案是：「{expected}」'
            
    elif mode == 'tail':
        # 接尾：以指定字开头
        start_char = keyword[0] if keyword else ''
        is_correct = clean_answer.startswith(start_char) and len(clean_answer) >= 5
        if is_correct:
            feedback = f'✓ 正确！以「{start_char}」开头'
        else:
            feedback = f'✗ 需以「{start_char}」字开头'
    
    return jsonify({
        'success': True,
        'is_correct': is_correct,
        'feedback': feedback,
        'your_answer': answer,
        'correct_answer': expected if is_correct else ''
    })


@poetry_bp.route('/keywords', methods=['GET'])
def get_keywords():
    """获取所有关键字"""
    keywords = list(POEM_DATABASE.keys())
    return jsonify({
        'success': True,
        'keywords': keywords,
        'total': len(keywords)
    })


@poetry_bp.route('/stats', methods=['GET'])
def get_poem_stats():
    """获取诗词统计"""
    stats = {}
    for kw, data in POEM_DATABASE.items():
        stats[kw] = {
            'keyword_count': len(data.get('keyword', [])),
            'quote_count': len(data.get('quote_pairs', []))
        }
    
    return jsonify({
        'success': True,
        'stats': stats,
        'total_keywords': len(POEM_DATABASE)
    })
