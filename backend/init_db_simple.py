"""
简化的数据库初始化脚本
不依赖 Flask，直接用 sqlite3
"""
import sqlite3
import os
import re
import uuid
from datetime import datetime, timezone, timedelta

DB_PATH = 'shiyayaji.db'

# 如果数据库已存在，删除它
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# 创建表
print("创建数据库表...")

# 用户表
cursor.execute('''
CREATE TABLE users (
    id TEXT PRIMARY KEY,
    nickname TEXT,
    rank TEXT DEFAULT '萌新',
    exp INTEGER DEFAULT 0,
    total_games INTEGER DEFAULT 0,
    total_wins INTEGER DEFAULT 0,
    total_correct INTEGER DEFAULT 0,
    avatar_url TEXT,
    device_id TEXT,
    created_at TEXT,
    updated_at TEXT
)
''')

# 会话表
cursor.execute('''
CREATE TABLE user_sessions (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    refresh_token_hash TEXT,
    expires_at TEXT NOT NULL,
    revoked_at TEXT,
    created_at TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
)
''')

# 诗词表
cursor.execute('''
CREATE TABLE poems (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    dynasty TEXT,
    source_name TEXT,
    source_url TEXT,
    license_name TEXT,
    license_url TEXT,
    distribution_allowed INTEGER DEFAULT 0,
    review_status TEXT DEFAULT 'PENDING',
    created_at TEXT
)
''')

# 诗句表
cursor.execute('''
CREATE TABLE poem_lines (
    id TEXT PRIMARY KEY,
    poem_id TEXT NOT NULL,
    line_no INTEGER NOT NULL,
    content TEXT NOT NULL,
    normalized_content TEXT NOT NULL,
    is_rare INTEGER DEFAULT 0,
    review_status TEXT DEFAULT 'PENDING',
    source_locator TEXT,
    created_at TEXT,
    FOREIGN KEY (poem_id) REFERENCES poems(id),
    UNIQUE(poem_id, line_no)
)
''')

# 标签表
cursor.execute('''
CREATE TABLE tags (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL,
    name TEXT NOT NULL,
    normalized_name TEXT NOT NULL,
    active INTEGER DEFAULT 1,
    created_at TEXT,
    UNIQUE(type, normalized_name)
)
''')

# 诗句-标签关联表
cursor.execute('''
CREATE TABLE poem_line_tags (
    poem_line_id TEXT NOT NULL,
    tag_id TEXT NOT NULL,
    confidence INTEGER DEFAULT 100,
    reviewed_by TEXT,
    created_at TEXT,
    PRIMARY KEY (poem_line_id, tag_id),
    FOREIGN KEY (poem_line_id) REFERENCES poem_lines(id),
    FOREIGN KEY (tag_id) REFERENCES tags(id)
)
''')

# 诗句别名表
cursor.execute('''
CREATE TABLE poem_line_aliases (
    id TEXT PRIMARY KEY,
    poem_line_id TEXT NOT NULL,
    normalized_alias TEXT NOT NULL,
    review_status TEXT DEFAULT 'PENDING',
    created_at TEXT,
    FOREIGN KEY (poem_line_id) REFERENCES poem_lines(id)
)
''')

# 节气表
cursor.execute('''
CREATE TABLE solar_terms (
    id TEXT PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL,
    season TEXT NOT NULL,
    primary_element TEXT NOT NULL,
    description TEXT,
    config_version TEXT NOT NULL,
    active INTEGER DEFAULT 1,
    created_at TEXT
)
''')

# 节气关键词表
cursor.execute('''
CREATE TABLE solar_term_keywords (
    id TEXT PRIMARY KEY,
    solar_term_id TEXT NOT NULL,
    keyword TEXT NOT NULL,
    imagery TEXT,
    sort_order INTEGER DEFAULT 0,
    enabled INTEGER DEFAULT 1,
    FOREIGN KEY (solar_term_id) REFERENCES solar_terms(id),
    UNIQUE(solar_term_id, keyword)
)
''')

# 每日主题表
cursor.execute('''
CREATE TABLE daily_themes (
    date_cn TEXT PRIMARY KEY,
    solar_term_id TEXT NOT NULL,
    keywords TEXT NOT NULL,
    imagery TEXT,
    config_version TEXT NOT NULL,
    created_at TEXT,
    FOREIGN KEY (solar_term_id) REFERENCES solar_terms(id)
)
''')

# 房间表
cursor.execute('''
CREATE TABLE rooms (
    id TEXT PRIMARY KEY,
    code TEXT UNIQUE NOT NULL,
    host_user_id TEXT NOT NULL,
    mode TEXT DEFAULT 'SOLAR_TERM_ELEMENT',
    status TEXT DEFAULT 'WAITING',
    keywords TEXT,
    time_limit_sec INTEGER DEFAULT 15,
    max_players INTEGER DEFAULT 4,
    config_version TEXT,
    current_turn_no INTEGER DEFAULT 0,
    current_player_id TEXT,
    created_at TEXT,
    started_at TEXT,
    finished_at TEXT,
    FOREIGN KEY (host_user_id) REFERENCES users(id)
)
''')

# 房间成员表
cursor.execute('''
CREATE TABLE room_members (
    id TEXT PRIMARY KEY,
    room_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    seat_no INTEGER,
    role TEXT DEFAULT 'member',
    is_alive INTEGER DEFAULT 1,
    connection_state TEXT DEFAULT 'offline',
    joined_at TEXT,
    eliminated_at TEXT,
    eliminate_reason TEXT,
    FOREIGN KEY (room_id) REFERENCES rooms(id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    UNIQUE(room_id, user_id)
)
''')

# 游戏回合表
cursor.execute('''
CREATE TABLE game_turns (
    id TEXT PRIMARY KEY,
    room_id TEXT NOT NULL,
    turn_no INTEGER NOT NULL,
    player_id TEXT NOT NULL,
    deadline_at TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    submitted_at TEXT,
    FOREIGN KEY (room_id) REFERENCES rooms(id),
    UNIQUE(room_id, turn_no)
)
''')

# 答案提交表
cursor.execute('''
CREATE TABLE answer_submissions (
    id TEXT PRIMARY KEY,
    room_id TEXT NOT NULL,
    turn_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    client_request_id TEXT NOT NULL,
    raw_text TEXT NOT NULL,
    normalized_text TEXT NOT NULL,
    result TEXT NOT NULL,
    matched_line_id TEXT,
    reason TEXT,
    score_delta INTEGER DEFAULT 0,
    element_bonus INTEGER DEFAULT 0,
    created_at TEXT,
    FOREIGN KEY (room_id) REFERENCES rooms(id),
    FOREIGN KEY (turn_id) REFERENCES game_turns(id),
    UNIQUE(user_id, client_request_id)
)
''')

# 房间已用诗句表
cursor.execute('''
CREATE TABLE room_used_lines (
    room_id TEXT NOT NULL,
    poem_line_id TEXT NOT NULL,
    submission_id TEXT NOT NULL,
    PRIMARY KEY (room_id, poem_line_id),
    FOREIGN KEY (room_id) REFERENCES rooms(id),
    FOREIGN KEY (poem_line_id) REFERENCES poem_lines(id)
)
''')

# 游戏结果表
cursor.execute('''
CREATE TABLE game_results (
    id TEXT PRIMARY KEY,
    room_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    placement INTEGER NOT NULL,
    score INTEGER DEFAULT 0,
    correct_count INTEGER DEFAULT 0,
    element_bonus_count INTEGER DEFAULT 0,
    is_winner INTEGER DEFAULT 0,
    created_at TEXT,
    FOREIGN KEY (room_id) REFERENCES rooms(id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    UNIQUE(room_id, user_id)
)
''')

# 用户收藏表
cursor.execute('''
CREATE TABLE user_favorites (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    target_type TEXT NOT NULL,
    target_id TEXT NOT NULL,
    created_at TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id),
    UNIQUE(user_id, target_type, target_id)
)
''')

# 用户解锁表
cursor.execute('''
CREATE TABLE user_poem_unlocks (
    user_id TEXT NOT NULL,
    poem_line_id TEXT NOT NULL,
    unlock_reason TEXT,
    unlocked_at TEXT,
    PRIMARY KEY (user_id, poem_line_id),
    FOREIGN KEY (user_id) REFERENCES users(id)
)
''')

# 审计表
cursor.execute('''
CREATE TABLE audit_events (
    id TEXT PRIMARY KEY,
    actor_type TEXT NOT NULL,
    actor_id TEXT,
    action TEXT NOT NULL,
    entity_type TEXT,
    entity_id TEXT,
    payload TEXT,
    created_at TEXT
)
''')

conn.commit()
print("数据库表创建完成！")


# 导入诗词数据
def normalize_text(text):
    text = re.sub(r'[，。！？；：、''""（）【】《》]', '', text)
    text = re.sub(r'\s+', '', text)
    return text


# 初始诗词数据
POEMS = [
    {"title": "静夜思", "author": "李白", "dynasty": "唐", "lines": [
        {"content": "床前明月光", "tags": ["月", "光", "夜", "思", "乡"], "is_rare": False},
        {"content": "疑是地上霜", "tags": ["霜", "月", "夜", "秋"], "is_rare": False},
        {"content": "举头望明月", "tags": ["月", "望", "夜", "思"], "is_rare": False},
        {"content": "低头思故乡", "tags": ["思", "乡", "月", "情"], "is_rare": False},
    ]},
    {"title": "春晓", "author": "孟浩然", "dynasty": "唐", "lines": [
        {"content": "春眠不觉晓", "tags": ["春", "眠", "晓", "睡"], "is_rare": False},
        {"content": "处处闻啼鸟", "tags": ["鸟", "春", "声", "鸣"], "is_rare": False},
        {"content": "夜来风雨声", "tags": ["雨", "风", "夜", "声"], "is_rare": False},
        {"content": "花落知多少", "tags": ["花", "落", "春", "雨"], "is_rare": False},
    ]},
    {"title": "登鹳雀楼", "author": "王之涣", "dynasty": "唐", "lines": [
        {"content": "白日依山尽", "tags": ["日", "山", "暮", "白"], "is_rare": False},
        {"content": "黄河入海流", "tags": ["河", "海", "黄", "流"], "is_rare": False},
        {"content": "欲穷千里目", "tags": ["目", "千", "远", "望"], "is_rare": False},
        {"content": "更上一层楼", "tags": ["楼", "上", "高", "望"], "is_rare": False},
    ]},
    {"title": "相思", "author": "王维", "dynasty": "唐", "lines": [
        {"content": "红豆生南国", "tags": ["红豆", "南", "春", "物"], "is_rare": False},
        {"content": "春来发几枝", "tags": ["春", "发", "生", "时"], "is_rare": False},
        {"content": "愿君多采撷", "tags": ["君", "采", "愿", "思"], "is_rare": False},
        {"content": "此物最相思", "tags": ["相思", "情", "物", "心"], "is_rare": False},
    ]},
    {"title": "鹿柴", "author": "王维", "dynasty": "唐", "lines": [
        {"content": "空山不见人", "tags": ["山", "空", "静", "人"], "is_rare": False},
        {"content": "但闻人语响", "tags": ["人", "声", "闻", "语"], "is_rare": False},
        {"content": "返景入深林", "tags": ["林", "深", "光", "日"], "is_rare": False},
        {"content": "复照青苔上", "tags": ["苔", "光", "林", "照"], "is_rare": False},
    ]},
    {"title": "悯农", "author": "李绅", "dynasty": "唐", "lines": [
        {"content": "锄禾日当午", "tags": ["锄", "禾", "日", "午", "农"], "is_rare": False},
        {"content": "汗滴禾下土", "tags": ["汗", "土", "禾", "劳"], "is_rare": False},
        {"content": "谁知盘中餐", "tags": ["餐", "食", "米", "盘中"], "is_rare": False},
        {"content": "粒粒皆辛苦", "tags": ["粒", "辛", "苦", "粮"], "is_rare": False},
    ]},
    {"title": "咏鹅", "author": "骆宾王", "dynasty": "唐", "lines": [
        {"content": "鹅鹅鹅", "tags": ["鹅", "鸟", "鸣"], "is_rare": False},
        {"content": "曲项向天歌", "tags": ["鹅", "天", "歌", "项"], "is_rare": False},
        {"content": "白毛浮绿水", "tags": ["白", "毛", "水", "浮", "绿"], "is_rare": False},
        {"content": "红掌拨清波", "tags": ["红", "波", "水", "清"], "is_rare": False},
    ]},
    {"title": "望庐山瀑布", "author": "李白", "dynasty": "唐", "lines": [
        {"content": "日照香炉生紫烟", "tags": ["日", "烟", "山", "紫"], "is_rare": False},
        {"content": "遥看瀑布挂前川", "tags": ["瀑", "川", "挂", "看"], "is_rare": False},
        {"content": "飞流直下三千尺", "tags": ["飞", "流", "水", "高"], "is_rare": False},
        {"content": "疑是银河落九天", "tags": ["河", "天", "落", "九"], "is_rare": False},
    ]},
    {"title": "绝句", "author": "杜甫", "dynasty": "唐", "lines": [
        {"content": "两个黄鹂鸣翠柳", "tags": ["黄", "鹂", "柳", "春", "鸣"], "is_rare": False},
        {"content": "一行白鹭上青天", "tags": ["白", "鹭", "天", "飞", "上"], "is_rare": False},
        {"content": "窗含西岭千秋雪", "tags": ["雪", "窗", "山", "千"], "is_rare": False},
        {"content": "门泊东吴万里船", "tags": ["船", "门", "水", "泊", "万"], "is_rare": False},
    ]},
    {"title": "江雪", "author": "柳宗元", "dynasty": "唐", "lines": [
        {"content": "千山鸟飞绝", "tags": ["山", "鸟", "飞", "雪", "千"], "is_rare": False},
        {"content": "万径人踪灭", "tags": ["人", "径", "灭", "雪", "万"], "is_rare": False},
        {"content": "孤舟蓑笠翁", "tags": ["舟", "翁", "孤", "雨"], "is_rare": False},
        {"content": "独钓寒江雪", "tags": ["雪", "江", "寒", "钓", "独"], "is_rare": False},
    ]},
    {"title": "枫桥夜泊", "author": "张继", "dynasty": "唐", "lines": [
        {"content": "月落乌啼霜满天", "tags": ["月", "乌", "霜", "夜", "啼"], "is_rare": False},
        {"content": "江枫渔火对愁眠", "tags": ["江", "枫", "火", "愁", "眠"], "is_rare": False},
        {"content": "姑苏城外寒山寺", "tags": ["城", "寺", "山", "寒"], "is_rare": False},
        {"content": "夜半钟声到客船", "tags": ["钟", "声", "夜", "船", "客"], "is_rare": False},
    ]},
    {"title": "出塞", "author": "王昌龄", "dynasty": "唐", "lines": [
        {"content": "秦时明月汉时关", "tags": ["月", "关", "秦", "汉", "明"], "is_rare": False},
        {"content": "万里长征人未还", "tags": ["万", "里", "人", "征", "远"], "is_rare": False},
        {"content": "但使龙城飞将在", "tags": ["将", "城", "龙", "飞"], "is_rare": False},
        {"content": "不教胡马度阴山", "tags": ["马", "山", "阴", "度"], "is_rare": False},
    ]},
    {"title": "凉州词", "author": "王翰", "dynasty": "唐", "lines": [
        {"content": "葡萄美酒夜光杯", "tags": ["酒", "杯", "夜", "光"], "is_rare": False},
        {"content": "欲饮琵琶马上催", "tags": ["酒", "马", "催", "弹"], "is_rare": False},
        {"content": "醉卧沙场君莫笑", "tags": ["沙", "场", "醉", "卧"], "is_rare": False},
        {"content": "古来征战几人回", "tags": ["战", "征", "回", "古"], "is_rare": False},
    ]},
    {"title": "黄鹤楼送孟浩然之广陵", "author": "李白", "dynasty": "唐", "lines": [
        {"content": "故人西辞黄鹤楼", "tags": ["楼", "鹤", "人", "辞", "西"], "is_rare": False},
        {"content": "烟花三月下扬州", "tags": ["花", "月", "春", "下", "扬"], "is_rare": False},
        {"content": "孤帆远影碧空尽", "tags": ["帆", "空", "远", "孤", "尽"], "is_rare": False},
        {"content": "唯见长江天际流", "tags": ["江", "长", "水", "流", "天"], "is_rare": False},
    ]},
    {"title": "山行", "author": "杜牧", "dynasty": "唐", "lines": [
        {"content": "远上寒山石径斜", "tags": ["山", "石", "寒", "斜", "远"], "is_rare": False},
        {"content": "白云生处有人家", "tags": ["云", "白", "生", "家", "有"], "is_rare": False},
        {"content": "停车坐爱枫林晚", "tags": ["车", "停", "爱", "枫", "晚"], "is_rare": False},
        {"content": "霜叶红于二月花", "tags": ["叶", "红", "霜", "花", "二"], "is_rare": False},
    ]},
    {"title": "清明", "author": "杜牧", "dynasty": "唐", "lines": [
        {"content": "清明时节雨纷纷", "tags": ["雨", "清", "时", "节", "纷"], "is_rare": False},
        {"content": "路上行人欲断魂", "tags": ["路", "人", "行", "魂", "断"], "is_rare": False},
        {"content": "借问酒家何处有", "tags": ["酒", "问", "家", "何", "处"], "is_rare": False},
        {"content": "牧童遥指杏花村", "tags": ["童", "花", "村", "指", "杏"], "is_rare": False},
    ]},
    {"title": "泊秦淮", "author": "杜牧", "dynasty": "唐", "lines": [
        {"content": "烟笼寒水月笼沙", "tags": ["烟", "寒", "水", "月", "沙"], "is_rare": False},
        {"content": "夜泊秦淮近酒家", "tags": ["泊", "夜", "秦", "淮", "酒"], "is_rare": False},
        {"content": "商女不知亡国恨", "tags": ["女", "亡", "国", "恨", "知"], "is_rare": False},
        {"content": "隔江犹唱后庭花", "tags": ["江", "花", "后", "隔", "唱"], "is_rare": False},
    ]},
    {"title": "乐游原", "author": "李商隐", "dynasty": "唐", "lines": [
        {"content": "向晚意不适", "tags": ["晚", "意", "向", "适"], "is_rare": False},
        {"content": "驱车登古原", "tags": ["车", "古", "登", "原"], "is_rare": False},
        {"content": "夕阳无限好", "tags": ["夕", "阳", "好", "无", "限"], "is_rare": False},
        {"content": "只是近黄昏", "tags": ["黄", "昏", "近", "只"], "is_rare": False},
    ]},
    {"title": "咏柳", "author": "贺知章", "dynasty": "唐", "lines": [
        {"content": "碧玉妆成一树高", "tags": ["柳", "碧", "玉", "树", "高"], "is_rare": False},
        {"content": "万条垂下绿丝绦", "tags": ["绿", "丝", "垂", "万", "条"], "is_rare": False},
        {"content": "不知细叶谁裁出", "tags": ["叶", "细", "裁", "出", "知"], "is_rare": False},
        {"content": "二月春风似剪刀", "tags": ["春", "风", "月", "刀", "剪"], "is_rare": False},
    ]},
]

# 导入诗词
print("\n导入诗词数据...")
for poem_data in POEMS:
    poem_id = str(uuid.uuid4())
    cursor.execute('''
        INSERT INTO poems (id, title, author, dynasty, source_name, license_name, distribution_allowed, review_status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, 1, 'APPROVED', ?)
    ''', (poem_id, poem_data['title'], poem_data['author'], poem_data.get('dynasty', '唐'),
          'chinese-poetry', 'MIT', datetime.now(timezone.utc).isoformat()))
    
    for i, line_data in enumerate(poem_data['lines'], 1):
        line_id = str(uuid.uuid4())
        cursor.execute('''
            INSERT INTO poem_lines (id, poem_id, line_no, content, normalized_content, is_rare, review_status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, 'APPROVED', ?)
        ''', (line_id, poem_id, i, line_data['content'], normalize_text(line_data['content']),
              1 if line_data.get('is_rare') else 0, datetime.now(timezone.utc).isoformat()))
        
        # 添加标签
        for tag_name in line_data.get('tags', []):
            cursor.execute(
                "SELECT id FROM tags WHERE type = 'scene' AND normalized_name = ?",
                (tag_name,)
            )
            row = cursor.fetchone()
            if row:
                tag_id = row[0]
            else:
                tag_id = str(uuid.uuid4())
                cursor.execute(
                    "INSERT INTO tags (id, type, name, normalized_name, active) VALUES (?, 'scene', ?, ?, 1)",
                    (tag_id, tag_name, tag_name)
                )
            
            cursor.execute(
                "INSERT OR IGNORE INTO poem_line_tags (poem_line_id, tag_id, confidence) VALUES (?, ?, 100)",
                (line_id, tag_id)
            )
    
    conn.commit()

print(f"已导入 {len(POEMS)} 首诗词")


# 导入节气数据
SOLAR_TERMS = [
    {"name": "立春", "start_date": "02-03", "end_date": "02-18", "season": "春", "primary_element": "木", "keywords": ["春", "风", "柳", "芽", "绿", "暖", "新"]},
    {"name": "雨水", "start_date": "02-19", "end_date": "03-05", "season": "春", "primary_element": "木", "keywords": ["雨", "水", "润", "湿", "桥", "舟"]},
    {"name": "惊蛰", "start_date": "03-06", "end_date": "03-20", "season": "春", "primary_element": "木", "keywords": ["雷", "虫", "鸣", "醒", "蝶", "鸟"]},
    {"name": "春分", "start_date": "03-21", "end_date": "04-04", "season": "春", "primary_element": "木", "keywords": ["春", "燕", "花", "草", "蝶", "筝"]},
    {"name": "清明", "start_date": "04-05", "end_date": "04-19", "season": "春", "primary_element": "木", "keywords": ["雨", "花", "柳", "风", "酒", "魂"]},
    {"name": "谷雨", "start_date": "04-20", "end_date": "05-05", "season": "春", "primary_element": "木", "keywords": ["雨", "谷", "茶", "萍", "桑", "蛙"]},
    {"name": "立夏", "start_date": "05-06", "end_date": "05-20", "season": "夏", "primary_element": "火", "keywords": ["夏", "蛙", "蝉", "荷", "风", "凉"]},
    {"name": "小满", "start_date": "05-21", "end_date": "06-05", "season": "夏", "primary_element": "火", "keywords": ["麦", "蚕", "桑", "黄", "满", "熟"]},
    {"name": "芒种", "start_date": "06-06", "end_date": "06-20", "season": "夏", "primary_element": "火", "keywords": ["麦", "稻", "芒", "种", "梅", "雨"]},
    {"name": "夏至", "start_date": "06-21", "end_date": "07-06", "season": "夏", "primary_element": "火", "keywords": ["日", "炎", "荷", "蝉", "热", "凉"]},
    {"name": "小暑", "start_date": "07-07", "end_date": "07-22", "season": "夏", "primary_element": "火", "keywords": ["风", "雨", "雷", "荷", "萤", "扇"]},
    {"name": "大暑", "start_date": "07-23", "end_date": "08-07", "season": "夏", "primary_element": "火", "keywords": ["热", "汗", "荷", "萤", "雷", "雨"]},
    {"name": "立秋", "start_date": "08-08", "end_date": "08-22", "season": "秋", "primary_element": "金", "keywords": ["秋", "叶", "凉", "蝉", "露", "月"]},
    {"name": "处暑", "start_date": "08-23", "end_date": "09-07", "season": "秋", "primary_element": "金", "keywords": ["暑", "凉", "露", "云", "雁", "雷"]},
    {"name": "白露", "start_date": "09-08", "end_date": "09-22", "season": "秋", "primary_element": "金", "keywords": ["露", "雁", "月", "桂", "萤", "寒"]},
    {"name": "秋分", "start_date": "09-23", "end_date": "10-07", "season": "秋", "primary_element": "金", "keywords": ["秋", "月", "桂", "菊", "枫", "雁"]},
    {"name": "寒露", "start_date": "10-08", "end_date": "10-22", "season": "秋", "primary_element": "金", "keywords": ["露", "寒", "菊", "红", "霜", "雁"]},
    {"name": "霜降", "start_date": "10-23", "end_date": "11-06", "season": "秋", "primary_element": "金", "keywords": ["霜", "枫", "菊", "柿", "露", "寒"]},
    {"name": "立冬", "start_date": "11-07", "end_date": "11-21", "season": "冬", "primary_element": "水", "keywords": ["冬", "寒", "藏", "梅", "雪", "水"]},
    {"name": "小雪", "start_date": "11-22", "end_date": "12-06", "season": "冬", "primary_element": "水", "keywords": ["雪", "雨", "冰", "寒", "梅", "松"]},
    {"name": "大雪", "start_date": "12-07", "end_date": "12-21", "season": "冬", "primary_element": "水", "keywords": ["雪", "寒", "冰", "松", "梅", "风"]},
    {"name": "冬至", "start_date": "12-22", "end_date": "01-05", "season": "冬", "primary_element": "水", "keywords": ["雪", "寒", "夜", "梅", "阳", "至"]},
    {"name": "小寒", "start_date": "01-06", "end_date": "01-19", "season": "冬", "primary_element": "水", "keywords": ["寒", "雪", "冰", "梅", "风", "年"]},
    {"name": "大寒", "start_date": "01-20", "end_date": "02-02", "season": "冬", "primary_element": "水", "keywords": ["寒", "雪", "冰", "风", "梅", "年"]},
]

print("\n导入节气数据...")
for term in SOLAR_TERMS:
    term_id = str(uuid.uuid4())
    cursor.execute('''
        INSERT INTO solar_terms (id, name, start_date, end_date, season, primary_element, config_version, active)
        VALUES (?, ?, ?, ?, ?, ?, 'v1', 1)
    ''', (term_id, term['name'], term['start_date'], term['end_date'], term['season'], term['primary_element']))
    
    for i, kw in enumerate(term['keywords']):
        cursor.execute('''
            INSERT INTO solar_term_keywords (id, solar_term_id, keyword, sort_order, enabled)
            VALUES (?, ?, ?, ?, 1)
        ''', (str(uuid.uuid4()), term_id, kw, i))
    
    conn.commit()

print(f"已导入 {len(SOLAR_TERMS)} 个节气")

conn.close()
print("\n" + "=" * 50)
print("数据库初始化完成！")
print(f"数据库文件: {os.path.abspath(DB_PATH)}")
print("=" * 50)
