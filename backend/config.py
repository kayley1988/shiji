"""诗语雅集 - 配置"""
import os
import logging
from typing import List

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 尝试加载 .env 文件
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv 未安装，忽略
    pass

class Config:
    """应用配置类"""
    
    # ═══════════════════════════════════════════════════════
    # 🔴 安全配置 - 支持环境变量和 .env 文件
    # ═══════════════════════════════════════════════════════
    
    # 生产环境必须设置 SECRET_KEY
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        # 开发环境使用默认值
        import secrets
        SECRET_KEY = f"dev-{secrets.token_hex(16)}"
        logging.warning("⚠️ 使用开发环境默认 SECRET_KEY，生产环境请设置 SECRET_KEY 环境变量")
    
    # 数据库：默认 SQLite，生产环境切换 MySQL
    _default_db = os.environ.get('DATABASE_URL', 'sqlite:///shiyayaji.db')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', _default_db)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = os.environ.get('SQLALCHEMY_ECHO', 'false').lower() == 'true'
    
    # CORS：严格限制来源，支持 .env 配置
    _cors_env = os.environ.get('CORS_ORIGINS', '')
    if _cors_env:
        CORS_ORIGINS = [origin.strip() for origin in _cors_env.split(',') if origin.strip()]
    else:
        # 默认允许的开发端口
        CORS_ORIGINS = [
            'http://localhost:5181',
            'http://localhost:3000',
            'http://localhost:5173',
            'http://127.0.0.1:5181',
            'http://127.0.0.1:3000',
        ]
        logging.warning("⚠️ CORS_ORIGINS 未设置，使用开发默认值")
    
    # Socket.IO
    SOCKETIO_MESSAGE_QUEUE = os.environ.get('REDIS_URL', None)
    
    # ═══════════════════════════════════════════════════════
    # 游戏配置
    # ═══════════════════════════════════════════════════════
    
    GAME_TIME_LIMIT_OPTIONS: List[int] = [10, 15, 20]
    GAME_MIN_PLAYERS = 2
    GAME_MAX_PLAYERS = 8
    GAME_DEFAULT_TIME_LIMIT = 15
    GAME_DEFAULT_MAX_PLAYERS = 4
    
    # 计分
    SCORE_VALID_ANSWER = 10
    SCORE_ELEMENT_BONUS_MULTIPLIER = 2  # 五行命中翻倍
    
    # 答案配置
    ANSWER_MAX_LENGTH = 80
    KEYWORD_MIN_LENGTH = 1
    KEYWORD_MAX_LENGTH = 6
    
    # 房间配置
    ROOM_WAIT_TIMEOUT = 15 * 60  # 15分钟无人开局解散
    ROOM_RECONNECT_GRACE_PERIOD = 30  # 30秒断线重连宽限

    # ═══════════════════════════════════════════════════════
    # 🔴 AI 服务 - 必须通过环境变量设置
    # ═══════════════════════════════════════════════════════
    
    DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY')
    if not DEEPSEEK_API_KEY:
        logging.warning("⚠️ DEEPSEEK_API_KEY 未设置，AI 对话功能将不可用")
    
    # 接尾飞花令专用配置
    TAIL_CONNECT_MIN_CHARS = 2      # 接尾最少字符数
    TAIL_CONNECT_TIME_LIMIT = 8     # 接尾模式更短时限（秒）
    TAIL_CONNECT_BONUS = 15         # 接尾正确基础分
    TAIL_CONNECT_BONUS_MULTIPLIER = 1.5  # 接尾加成系数


# ═══════════════════════════════════════════════════════
# 飞花令关键字池（单字令，精选高频诗词字）
# ═══════════════════════════════════════════════════════
FEIHUALING_KEYWORDS = [
    '月', '花', '春', '秋', '风', '雨', '雪', '云', '山', '水',
    '江', '河', '海', '湖', '天', '日', '夜', '星', '梦', '心',
    '情', '愁', '思', '酒', '醉', '歌', '人', '君', '客', '家',
    '乡', '归', '别', '望', '楼', '台', '门', '窗', '灯', '烟',
    '柳', '梅', '竹', '松', '桃', '荷', '菊', '兰', '草', '鸟',
    '马', '燕', '雁', '鹤', '龙', '红', '绿', '青', '白', '黄',
    '金', '玉', '钟', '琴', '书', '剑', '路', '舟', '船', '桥',
]


# ═══════════════════════════════════════════════════════
# 意象精选分组（诗词品鉴筛选）
# ═══════════════════════════════════════════════════════
IMAGERY_GROUPS = [
    {
        'name': '自然',
        'items': ['云', '天', '山', '水', '江', '河', '海', '川', '月', '日',
                  '风', '雨', '雪', '霜', '沙', '石', '瀑', '波', '烟', '光',
                  '空', '火', '帆', '流', '浮', '泊', '清', '深'],
    },
    {
        'name': '植物',
        'items': ['花', '柳', '枫', '杏', '苔', '林', '叶', '禾', '红豆',
                  '树', '条', '米', '粒', '粮'],
    },
    {
        'name': '动物',
        'items': ['鸟', '马', '鹤', '鹭', '鹂', '鹅', '龙', '鸣', '飞'],
    },
    {
        'name': '人物',
        'items': ['君', '客', '翁', '童', '女', '人', '农', '人物'],
    },
    {
        'name': '器物',
        'items': ['酒', '杯', '船', '舟', '车', '钟', '刀', '锄', '玉', '盘中'],
    },
    {
        'name': '建筑',
        'items': ['寺', '楼', '城', '门', '窗', '桥', '家', '村', '关',
                  '乡', '场', '径', '国', '土', '地理', '建筑'],
    },
    {
        'name': '情感',
        'items': ['情', '愁', '思', '恨', '爱', '怨', '悲', '欢', '喜',
                  '怜', '惆', '怅', '伤', '心', '意', '念'],
    },
    {
        'name': '动作',
        'items': ['望', '归', '行', '去', '来', '入', '出', '坐', '立',
                  '卧', '醉', '醒', '歌', '笑', '哭', '语', '言'],
    },
    {
        'name': '时间',
        'items': ['春', '夏', '秋', '冬', '年', '日', '夜', '朝', '暮',
                  '时', '光', '阴', '晴', '晓', '黄昏'],
    },
]


# ═══════════════════════════════════════════════════════
# 诗人卡片数据（模拟 AI 生成的对诗人描述）
# ═══════════════════════════════════════════════════════
POET_CARDS = {
    '李白': {
        'title': '诗仙',
        'desc': '豪放飘逸，浪漫主义的巅峰',
        'style': '豪迈、洒脱、充满想象力',
        'mood': '酒、月、剑、鹏',
    },
    '杜甫': {
        'title': '诗圣',
        'desc': '沉郁顿挫，现实主义的典范',
        'style': '忧国忧民，沉稳厚重',
        'mood': '家、国、民生、山河',
    },
    '白居易': {
        'title': '诗魔',
        'desc': '老妪能解，通俗易懂又意境深远',
        'style': '平易近人，浅显深刻',
        'mood': '人间、世俗、情感',
    },
    '苏轼': {
        'title': '诗神',
        'desc': '诗词书画全能，才华横溢',
        'style': '旷达、哲理、豪放与婉约兼具',
        'mood': '江月、人生、豁达',
    },
    '李清照': {
        'title': '词后',
        'desc': '婉约派的代表，女性词人的骄傲',
        'style': '细腻、婉约、情感真挚',
        'mood': '花、月、思、愁',
    },
    '王维': {
        'title': '诗佛',
        'desc': '诗中有画，画中有诗',
        'style': '禅意、静谧、意境空灵',
        'mood': '山水、禅意、空灵',
    },
    '辛弃疾': {
        'title': '词龙',
        'desc': '豪放派的代表，壮志难酬的英雄',
        'style': '豪壮、悲愤、报国之志',
        'mood': '金戈、铁马、江山',
    },
    '陶渊明': {
        'title': '诗魂',
        'desc': '田园诗的开创者，归隐山林的高士',
        'style': '淡泊、宁静、自然',
        'mood': '田园、菊、归隐',
    },
}


# ═══════════════════════════════════════════════════════
# 接尾飞花令模式：接尾字符映射表
# 例如 "月" -> "月" 可以接的尾字
# ═══════════════════════════════════════════════════════
TAIL_CHAR_MAP = {
    # 常见字及其可接的尾字（简化版，实际应从数据库读取）
    '月': ['圆', '光', '亮', '色', '下', '上', '中', '明', '夜', '楼'],
    '花': ['开', '落', '香', '飞', '红', '白', '黄', '春', '秋'],
    '春': ['来', '去', '风', '雨', '色', '晓', '眠', '归'],
    '秋': ['风', '月', '色', '声', '意', '心', '思', '叶'],
    '风': ['吹', '起', '来', '去', '雨', '云', '声'],
    '雨': ['声', '落', '来', '去', '打', '滴', '晴'],
    '雪': ['落', '飘', '飞', '化', '白', '寒'],
    '云': ['飞', '飘', '去', '来', '卷', '舒'],
    '山': ['上', '下', '中', '高', '青', '绿'],
    '水': ['流', '深', '浅', '清', '浊', '长', '远'],
    '江': ['上', '水', '南', '北', '流', '天'],
    '河': ['水', '流', '北', '南'],
    '海': ['上', '水', '内', '外', '边'],
    '天': ['上', '下', '地', '空', '涯'],
    '日': ['出', '落', '光', '照', '斜', '暮'],
    '夜': ['色', '深', '静', '阑', '半', '长'],
    '星': ['光', '稀', '河', '空'],
    '梦': ['中', '里', '醒', '回', '难'],
    '心': ['中', '上', '里', '意', '情'],
    '情': ['深', '长', '意', '真', '浓'],
    '愁': ['思', '绪', '肠', '苦', '多'],
    '思': ['念', '故', '乡', '君', '人'],
    '酒': ['醉', '杯', '香', '浓', '醇'],
    '人': ['生', '间', '去', '来', '老'],
}


# ═══════════════════════════════════════════════════════
# AI 生图提示词模板
# ═══════════════════════════════════════════════════════
ART_PROMPTS = {
    'default': 'Traditional Chinese ink painting style, {poem_content}, serene mountain landscape, poetry illustration, minimalist, elegant brushstrokes, black and white with subtle red accents',
    'gongbi': 'Traditional Chinese Gongbi style fine painting, {poem_content}, delicate brushwork, vibrant colors, classical Chinese art, poetry illustration, intricate details',
    'shuimo': 'Chinese ink wash painting (Shuimo), {poem_content}, minimalist black ink, elegant composition, poetry scene, traditional Chinese art style',
    'dunhuang': 'Dunhuang cave fresco style, {poem_content}, vibrant colors, Buddhist art influence, traditional Chinese painting, poetry illustration',
    'modern': 'Modern Chinese art style fusion, {poem_content}, contemporary interpretation, poetry scene, elegant and stylish, minimal design',
}

# ═══════════════════════════════════════════════════════
# 拍立得边框样式配置
# ═══════════════════════════════════════════════════════
POLAROID_STYLES = {
    'classic': {
        'name': '经典拍立得',
        'frame_color': '#f5f5f5',
        'border_width': 12,
        'shadow': True,
        'tilt': 0,
    },
    'vintage': {
        'name': '复古胶片',
        'frame_color': '#e8dcc8',
        'border_width': 16,
        'shadow': True,
        'tilt': -2,
    },
    'ink': {
        'name': '水墨古卷',
        'frame_color': '#f8f4e8',
        'border_width': 20,
        'shadow': False,
        'tilt': 0,
        'pattern': 'bamboo',
    },
    'modern': {
        'name': '现代简约',
        'frame_color': '#ffffff',
        'border_width': 8,
        'shadow': True,
        'tilt': 0,
    },
}
