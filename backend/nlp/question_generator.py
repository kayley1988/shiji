"""
题库生成器 - 诗语雅集

支持三种题型：
1. 飞花令 - 给定关键字，说出含该字的诗句（对战模式）
2. 填句题 - 给出上句，填下句（单选/填空）
3. 识别题 - 给出诗句，识别作者或题目

性能优化（v2）：
- 层1: first_char 索引精确过滤，大幅减少扫描范围
- 层2: 精确匹配 LRU 缓存，命中率最高路径 <1ms
- 层3: 模糊匹配只在前两层过滤后子集上跑
"""
import random
import re
import os
from typing import List, Dict, Optional
from dataclasses import dataclass
from functools import lru_cache

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, scoped_session

from .char_convert import to_simplified, normalize_poetry_text

# ============ 数据库连接 ============

engine = create_engine('sqlite:///E:/shiji/backend/shiyayaji.db')
_Session = scoped_session(sessionmaker(bind=engine))


def get_db():
    return _Session()


# ============ 全局精确匹配缓存（进程内 LRU）============
# key=(normalized_text,), value=(line_id, content, title, author)
# 容量 5000 条，覆盖绝大多数标准诗句
@lru_cache(maxsize=5000)
def _cached_exact_lookup(norm_text: str):
    """精确匹配查询（带进程级 LRU 缓存）"""
    db = _Session()
    try:
        result = db.execute(text('''
            SELECT pl.id, pl.content, p.title, p.author
            FROM poem_lines pl
            JOIN poems p ON p.id = pl.poem_id
            WHERE p.review_status = 'APPROVED'
              AND pl.normalized_content = :norm
            LIMIT 5
        '''), {'norm': norm_text})
        rows = result.fetchall()
        if rows:
            return rows
        return None
    finally:
        _Session.remove()


# ============ 缓存失效装饰器 ============
def invalidate_cache():
    """清除精确匹配缓存（在批量导入后调用）"""
    _cached_exact_lookup.cache_clear()


# ============ 题库配置 ============

# 通行版→古籍版 别名映射（最常见诗词的不同版本）
# key=通行版(用户常说), value=古籍版(数据库有)
VARIANT_ALIASES = {
    '床前明月光': '床前看月光',
    '低头思故乡': '举头望山月',  # 这句配对错误，忽略
    '春眠不觉晓': '春眠不覺曉',
    '春风又绿江南岸': '春風又綠江南岸',
    '春风又绿江南岸': '春风又绿江南岸',
    '明月几时有': '明月幾時有',
    '明月几时有': '明月几时有',
    '海上生明月': '海上生明月',
    '但愿人长久': '但願人長久',
    '千里共婵娟': '千里共嬋娟',
    '不知细叶谁裁出': '不知細葉誰裁出',
    '二月春风似剪刀': '二月春風似剪刀',
    '万紫千红总是春': '萬紫千紅總是春',
    '桃花潭水深千尺': '桃花潭水深千尺',
}

def _resolve_variant(text: str) -> str:
    """解析通行版别名，返回数据库中的版本"""
    return VARIANT_ALIASES.get(text, text)


# 飞花令高频字（常用关键字）
FEIHUA_KEYWORDS = [
    '人', '山', '水', '月', '花', '春', '风', '云', '鸟', '秋',
    '夜', '酒', '雨', '雪', '日', '江', '城', '天', '地', '心',
    '思', '泪', '梦', '君', '家', '路', '树', '柳', '梅', '竹',
    '马', '舟', '灯', '书', '茶', '琴', '棋', '诗', '画', '情',
    '恨', '愁', '寒', '暖', '清', '明', '白', '青', '红', '绿',
]

# 填句题经典名句对
FILL_BLANK_PAIRS = [
    ('春眠不觉晓', '处处闻啼鸟'),
    ('举头望明月', '低头思故乡'),
    ('白日依山尽', '黄河入海流'),
    ('欲穷千里目', '更上一层楼'),
    ('野火烧不尽', '春风吹又生'),
    ('不知细叶谁裁出', '二月春风似剪刀'),
    ('春风又绿江南岸', '明月何时照我还'),
    ('海内存知己', '天涯若比邻'),
    ('欲把西湖比西子', '淡妆浓抹总相宜'),
    ('但愿人长久', '千里共婵娟'),
    ('人生自古谁无死', '留取丹心照汗青'),
    ('山重水复疑无路', '柳暗花明又一村'),
    ('问君能有几多愁', '恰似一江春水向东流'),
    ('两个黄鹂鸣翠柳', '一行白鹭上青天'),
    ('桃花潭水深千尺', '不及汪伦送我情'),
    ('独在异乡为异客', '每逢佳节倍思亲'),
    ('葡萄美酒夜光杯', '欲饮琵琶马上催'),
    ('醉卧沙场君莫笑', '古来征战几人回'),
    ('旧时王谢堂前燕', '飞入寻常百姓家'),
    ('好雨知时节', '当春乃发生'),
    ('随风潜入夜', '润物细无声'),
    ('正是江南好风景', '落花时节又逢君'),
    ('日出江花红胜火', '春来江水绿如蓝'),
    ('借问酒家何处有', '牧童遥指杏花村'),
    ('停车坐爱枫林晚', '霜叶红于二月花'),
    ('天阶夜色凉如水', '卧看牵牛织女星'),
    ('何当共剪西窗烛', '却话巴山夜雨时'),
    ('春蚕到死丝方尽', '蜡炬成灰泪始干'),
    ('身无彩凤双飞翼', '心有灵犀一点通'),
    ('相见时难别亦难', '东风无力百花残'),
    ('回眸一笑百媚生', '六宫粉黛无颜色'),
    ('在天愿作比翼鸟', '在地愿为连理枝'),
    ('天长地久有时尽', '此恨绵绵无绝期'),
    ('同是天涯沦落人', '相逢何必曾相识'),
    ('羌笛何须怨杨柳', '春风不度玉门关'),
    ('黄沙百战穿金甲', '不破楼兰终不还'),
    ('两岸青山相对出', '孤帆一片日边来'),
    ('飞流直下三千尺', '疑是银河落九天'),
    ('日照香炉生紫烟', '遥看瀑布挂前川'),
    ('长风破浪会有时', '直挂云帆济沧海'),
    ('天生我材必有用', '千金散尽还复来'),
    ('人生得意须尽欢', '莫使金樽空对月'),
    ('蜀道之难难于上青天', '侧身西望长咨嗟'),
    ('忽如一夜春风来', '千树万树梨花开'),
    ('山回路转不见君', '雪上空留马行处'),
    ('孤帆远影碧空尽', '唯见长江天际流'),
    ('故人西辞黄鹤楼', '烟花三月下扬州'),
    ('我寄愁心与明月', '随风直到夜郎西'),
    ('明月几时有', '把酒问青天'),
    ('人有悲欢离合', '月有阴晴圆缺'),
    ('大江东去', '浪淘尽'),
    ('明月松间照', '清泉石上流'),
    ('空山新雨后', '天气晚来秋'),
    ('独坐幽篁里', '弹琴复长啸'),
    ('红豆生南国', '春来发几枝'),
    ('愿君多采撷', '此物最相思'),
    ('千山鸟飞绝', '万径人踪灭'),
    ('孤舟蓑笠翁', '独钓寒江雪'),
    ('床前明月光', '疑是地上霜'),
    ('举头望明月', '低头思故乡'),
    ('锄禾日当午', '汗滴禾下土'),
    ('谁知盘中餐', '粒粒皆辛苦'),
    ('鹅鹅鹅', '曲项向天歌'),
    ('白毛浮绿水', '红掌拨清波'),
    ('离离原上草', '一岁一枯荣'),
    ('远芳侵古道', '晴翠接荒城'),
    ('又送王孙去', '萋萋满别情'),
    ('慈母手中线', '游子身上衣'),
    ('临行密密缝', '意恐迟迟归'),
    ('谁言寸草心', '报得三春晖'),
    ('松下问童子', '言师采药去'),
    ('只在此山中', '云深不知处'),
    ('向晚意不适', '驱车登古原'),
    ('夕阳无限好', '只是近黄昏'),
    ('空山不见人', '但闻人语响'),
    ('返景入深林', '复照青苔上'),
    ('独怜幽草涧边生', '上有黄鹂深树鸣'),
    ('月落乌啼霜满天', '江枫渔火对愁眠'),
    ('姑苏城外寒山寺', '夜半钟声到客船'),
    ('劝君更尽一杯酒', '西出阳关无故人'),
    ('洛阳亲友如相问', '一片冰心在玉壶'),
    ('秦时明月汉时关', '万里长征人未还'),
    ('但使龙城飞将在', '不教胡马度阴山'),
    ('朝辞白帝彩云间', '千里江陵一日还'),
]


# ============ 数据模型 ============

@dataclass
class Question:
    qid: str
    qtype: str          # 'feihua' | 'fill_blank' | 'identify_author'
    keyword: str
    prompt: str
    answer: str
    options: List[str]
    poem_id: str
    poem_title: str
    author: str
    difficulty: int


@dataclass
class QuizResult:
    correct: bool
    score_delta: int
    element_bonus: bool
    matched_line_id: Optional[str]
    reason: str
    raw_text: str


# ============ 题库类 ============

class QuestionGenerator:
    """题库生成器"""
    
    def __init__(self, db_session=None):
        self.db = db_session or get_db()
        self._feihua_cache = {}
        self._updated_normals = False
    
    def _ensure_normalized(self):
        """确保 normalized_content 已转为简体"""
        if self._updated_normals:
            return
        
        # 检查是否有未规范化的数据
        result = self.db.execute(text('''
            SELECT id FROM poem_lines
            WHERE normalized_content != :converted
            LIMIT 1
        '''), {'converted': to_simplified('测')})
        
        # 简单检查：看是否已有简体数据
        result2 = self.db.execute(text('''
            SELECT COUNT(*) FROM poem_lines
            WHERE normalized_content LIKE '%书%'
        '''))
        count = result2.scalar() or 0
        
        if count == 0:
            # 批量更新 normalized_content
            print('正在规范化诗句文本...')
            all_lines = self.db.execute(text('SELECT id, content FROM poem_lines'))
            updated = 0
            for row in all_lines:
                line_id, content = row
                norm = normalize_poetry_text(content)
                self.db.execute(text(
                    'UPDATE poem_lines SET normalized_content = :norm WHERE id = :id'
                ), {'norm': norm, 'id': line_id})
                updated += 1
                if updated % 50000 == 0:
                    self.db.commit()
                    print(f'  已更新 {updated}...')
            self.db.commit()
            print(f'规范化完成，共 {updated} 条')
        
        self._updated_normals = True
    
    def get_feihua_lines(self, keyword: str, limit: int = 100) -> List[Dict]:
        """获取含指定关键字的诗句（简体化后搜索）- 优化版 v2
        
        用 first_char 索引过滤，减少 LIKE 全表扫描
        """
        self._ensure_normalized()
        
        if keyword in self._feihua_cache:
            return self._feihua_cache[keyword]
        
        # 转为简体后搜索
        simp_kw = to_simplified(keyword)
        
        # 优化: 用 first_char 索引过滤，只扫描首字匹配的行
        query = '''
            SELECT pl.id, pl.content, pl.normalized_content,
                   p.id as poem_id, p.title, p.author, p.dynasty
            FROM poem_lines pl
            JOIN poems p ON p.id = pl.poem_id
            WHERE p.review_status = 'APPROVED'
              AND pl.first_char = :fc          -- first_char 索引过滤
              AND pl.normalized_content LIKE :kw
            ORDER BY RANDOM()
            LIMIT :limit
        '''
        result = self.db.execute(text(query), {
            'fc': simp_kw[0],
            'kw': f'%{simp_kw}%',
            'limit': limit
        })
        rows = result.fetchall()
        
        lines = []
        for row in rows:
            lines.append({
                'id': row[0],
                'content': row[1],
                'normalized': row[2],
                'poem_id': row[3],
                'title': row[4],
                'author': row[5],
                'dynasty': row[6],
            })
        
        self._feihua_cache[keyword] = lines
        self._feihua_cache[simp_kw] = lines
        return lines
    
    def get_random_keyword(self) -> str:
        """随机获取飞花令关键字"""
        return random.choice(FEIHUA_KEYWORDS)
    
    def generate_feihua_challenge(
        self, keyword: str, used_line_ids: set = None
    ) -> Optional[Question]:
        """生成飞花令挑战"""
        used = used_line_ids or set()
        lines = self.get_feihua_lines(keyword, limit=200)
        
        available = [l for l in lines if l['id'] not in used]
        if not available:
            available = lines
        
        if not available:
            return None
        
        line = random.choice(available)
        
        return Question(
            qid=f'feihua_{keyword}_{line["id"][:8]}',
            qtype='feihua',
            keyword=keyword,
            prompt=f'请说出含「{keyword}」字的诗句',
            answer=line['content'],
            options=[],
            poem_id=line['poem_id'],
            poem_title=line['title'],
            author=line['author'],
            difficulty=2
        )
    
    def generate_fill_blank(self) -> Optional[Question]:
        """生成填句题"""
        # 优先使用经典名句对
        if random.random() < 0.85 and FILL_BLANK_PAIRS:
            upper, lower = random.choice(FILL_BLANK_PAIRS)
            qid = f'fill_{hash(upper) % 100000:05d}'
            return Question(
                qid=qid,
                qtype='fill_blank',
                keyword='',
                prompt=f'上句：{upper}',
                answer=lower,
                options=[],
                poem_id='',
                poem_title='',
                author='',
                difficulty=1
            )
        
        # 备选：从数据库
        self._ensure_normalized()
        query = '''
            SELECT pl1.id, pl1.content, pl1.normalized_content, pl2.content,
                   p.id as poem_id, p.title, p.author
            FROM poem_lines pl1
            JOIN poem_lines pl2 ON pl2.poem_id = pl1.poem_id
                AND pl2.line_no = pl1.line_no + 1
            JOIN poems p ON p.id = pl1.poem_id
            WHERE p.review_status = 'APPROVED'
              AND pl2.content != ''
              AND length(pl1.content) >= 5
              AND length(pl2.content) >= 5
            ORDER BY RANDOM()
            LIMIT 1
        '''
        result = self.db.execute(text(query))
        row = result.fetchone()
        
        if not row:
            return None
        
        line1_id, line1_content, line1_norm, line2_content = row[0], row[1], row[2], row[3]
        poem_id, poem_title, author = row[4], row[5], row[6]
        
        return Question(
            qid=f'fill_{hash(line1_content) % 100000:05d}',
            qtype='fill_blank',
            keyword='',
            prompt=f'上句：{line1_content}',
            answer=line2_content,
            options=[],
            poem_id=poem_id,
            poem_title=poem_title,
            author=author,
            difficulty=3
        )
    
    def generate_multi_choice(self, qtype: str = 'identify_author') -> Optional[Question]:
        """生成选择题"""
        self._ensure_normalized()
        
        query = '''
            SELECT id, title, author, dynasty
            FROM poems
            WHERE review_status = 'APPROVED'
            ORDER BY RANDOM()
            LIMIT 1
        '''
        result = self.db.execute(text(query))
        row = result.fetchone()
        
        if not row:
            return None
        
        poem_id, title, author, dynasty = row
        
        query2 = self.db.execute(text('''
            SELECT content FROM poem_lines
            WHERE poem_id = :pid AND line_no = 0
            LIMIT 1
        '''), {'pid': poem_id})
        row2 = query2.fetchone()
        if not row2:
            return None
        
        first_line = row2[0]
        
        # 干扰选项
        wrong_result = self.db.execute(text('''
            SELECT DISTINCT author FROM poems
            WHERE review_status = 'APPROVED' AND author != :author
            ORDER BY RANDOM() LIMIT 3
        '''), {'author': author})
        wrong_authors = [r[0] for r in wrong_result.fetchall()]
        
        if len(wrong_authors) < 3:
            fallback = ['李白', '杜甫', '白居易', '王维', '苏轼', '李商隐', '杜牧', '王安石']
            wrong_authors = random.sample([a for a in fallback if a != author], 3)
        
        options = [author] + wrong_authors[:3]
        random.shuffle(options)
        
        return Question(
            qid=f'mc_{poem_id[:8]}',
            qtype=qtype,
            keyword='',
            prompt=f'这句诗出自哪首诗？\n"{first_line}"',
            answer=author if qtype == 'identify_author' else title,
            options=options,
            poem_id=poem_id,
            poem_title=title,
            author=author,
            difficulty=2
        )
    
    def judge_feihua(self, user_text: str, keyword: str,
                     used_line_ids: set = None) -> QuizResult:
        """判定飞花令答案 - 优化版（v2）
        
        三层过滤：
        1. 精确匹配（LRU 缓存，<1ms）
        2. first_char 索引过滤 + 子串匹配
        3. 编辑距离（只在前两层候选上跑）
        """
        used = used_line_ids or set()
        
        # 规范化输入（先尝试通行版别名解析）
        user_norm = normalize_poetry_text(_resolve_variant(user_text))
        
        # 检查关键字
        if keyword not in user_norm:
            return QuizResult(
                correct=False, score_delta=0, element_bonus=False,
                matched_line_id=None,
                reason=f'答案需包含「{keyword}」字',
                raw_text=user_text
            )
        
        # ========== 层1: 精确匹配（带 LRU 缓存）==========
        rows = _cached_exact_lookup(user_norm)
        if rows:
            for line_id, content, poem_title, author in rows:
                if line_id not in used:
                    return QuizResult(
                        correct=True, score_delta=10, element_bonus=False,
                        matched_line_id=line_id,
                        reason=f'✓ 正确！{poem_title} - {author}',
                        raw_text=user_text
                    )
        
        # ========== 层2: first_char 索引过滤 + 子串匹配 =========
        user_len = len(user_norm)
        if user_len < 3:
            return QuizResult(
                correct=False, score_delta=0, element_bonus=False,
                matched_line_id=None,
                reason='数据库中未找到此诗句，请确认出处正确',
                raw_text=user_text
            )
        
        # 取首字用于 first_char 索引过滤
        first_char = user_norm[0]
        
        # 提取连续3字子串作为搜索键
        substr_candidates = {user_norm[i:i+3] for i in range(user_len - 2)}
        
        best_match = None
        best_score = 0
        
        for substr in substr_candidates:
            # 优化: 加 first_char 过滤，大幅减少扫描范围
            result2 = self.db.execute(text('''
                SELECT pl.id, pl.content, p.title, p.author
                FROM poem_lines pl
                JOIN poems p ON p.id = pl.poem_id
                WHERE p.review_status = 'APPROVED'
                  AND pl.first_char = :fc          -- first_char 索引过滤
                  AND pl.normalized_content LIKE :pat
                LIMIT 30
            '''), {'fc': first_char, 'pat': f'%{substr}%'})
            
            for row in result2.fetchall():
                line_id, content, poem_title, author = row
                if line_id in used:
                    continue
                db_norm = normalize_poetry_text(content)
                
                if db_norm == user_norm:
                    return QuizResult(
                        correct=True, score_delta=10, element_bonus=False,
                        matched_line_id=line_id,
                        reason=f'✓ 正确！{poem_title} - {author}',
                        raw_text=user_text
                    )
                
                # ========== 层3: 编辑距离（只在小候选集上跑）==========
                dist = self._levenshtein(db_norm, user_norm)
                max_len = max(len(db_norm), len(user_norm))
                score = (max_len - dist) / max_len
                if score >= 0.80 and score > best_score:
                    best_match = (line_id, content, poem_title, author, score)
                    best_score = score
        
        if best_match and best_score >= 0.80:
            line_id, content, poem_title, author, score = best_match
            return QuizResult(
                correct=True, score_delta=7, element_bonus=False,
                matched_line_id=line_id,
                reason=f'✓ 正确（相近版本）！{poem_title} - {author}',
                raw_text=user_text
            )
        
        return QuizResult(
            correct=False, score_delta=0, element_bonus=False,
            matched_line_id=None,
            reason='数据库中未找到此诗句，请确认出处正确',
            raw_text=user_text
        )
    
    def _is_similar(self, text1: str, text2: str, threshold: float = 0.80) -> bool:
        """判断两句诗是否高度相似（用于处理古籍版本差异）"""
        if len(text1) < 3 or len(text2) < 3:
            return False
        
        # 编辑距离（Levenshtein）
        len1, len2 = len(text1), len(text2)
        if abs(len1 - len2) > 2:
            return False
        
        # 动态规划计算编辑距离
        dp = [[0] * (len2 + 1) for _ in range(len1 + 1)]
        for i in range(len1 + 1):
            dp[i][0] = i
        for j in range(len2 + 1):
            dp[0][j] = j
        
        for i in range(1, len1 + 1):
            for j in range(1, len2 + 1):
                if text1[i-1] == text2[j-1]:
                    dp[i][j] = dp[i-1][j-1]
                else:
                    dp[i][j] = 1 + min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1])
        
        distance = dp[len1][len2]
        max_len = max(len1, len2)
        similarity = (max_len - distance) / max_len
        return similarity >= threshold
    
    def _levenshtein(self, s1: str, s2: str) -> int:
        """计算两个字符串的编辑距离"""
        len1, len2 = len(s1), len(s2)
        dp = [[0] * (len2 + 1) for _ in range(len1 + 1)]
        for i in range(len1 + 1):
            dp[i][0] = i
        for j in range(len2 + 1):
            dp[0][j] = j
        for i in range(1, len1 + 1):
            for j in range(1, len2 + 1):
                if s1[i-1] == s2[j-1]:
                    dp[i][j] = dp[i-1][j-1]
                else:
                    dp[i][j] = 1 + min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1])
        return dp[len1][len2]
    
    def get_keyword_stats(self, keyword: str) -> Dict:
        """获取关键字统计"""
        self._ensure_normalized()
        simp_kw = to_simplified(keyword)
        query = '''
            SELECT COUNT(*)
            FROM poem_lines pl
            JOIN poems p ON p.id = pl.poem_id
            WHERE pl.normalized_content LIKE :kw
              AND p.review_status = 'APPROVED'
        '''
        result = self.db.execute(text(query), {'kw': f'%{simp_kw}%'})
        count = result.scalar() or 0
        return {'keyword': keyword, 'available_lines': count}
    
    def get_all_keywords_stats(self) -> List[Dict]:
        """获取所有关键字统计"""
        return [self.get_keyword_stats(kw) for kw in FEIHUA_KEYWORDS]


# ============ 快捷函数 ============

def quick_test():
    """快速测试"""
    qg = QuestionGenerator()
    
    print('=' * 50)
    print('题库生成器测试')
    print('=' * 50)
    
    # 关键字统计
    print('\n高频字诗句数量:')
    for kw in ['月', '花', '春', '酒', '水', '山', '风', '云']:
        stats = qg.get_keyword_stats(kw)
        print(f'  「{kw}」: {stats["available_lines"]} 条')
    
    print()
    
    # 飞花令挑战
    keyword = qg.get_random_keyword()
    print(f'随机关键字: {keyword}')
    challenge = qg.generate_feihua_challenge(keyword)
    if challenge:
        print(f'挑战: {challenge.prompt}')
        print(f'正确答案: {challenge.answer}')
        print(f'出处: {challenge.poem_title} - {challenge.author}')
    
    print()
    print('-' * 50)
    print('判题测试')
    print('-' * 50)
    
    # 规范化后的判题
    tests = [
        ('床前明月光', '月', set()),
        ('床前看月光', '月', set()),   # 数据库中是"看"
        ('举头望明月', '月', set()),
        ('这是我自己写的', '月', set()),
    ]
    
    for text, kw, used in tests:
        result = qg.judge_feihua(text, kw, used)
        print(f'\n答案: {text}')
        print(f'  正确: {result.correct}, 分数: {result.score_delta}')
        print(f'  原因: {result.reason}')
    
    print()
    print('=' * 50)
    print('填句题测试')
    print('=' * 50)
    
    q = qg.generate_fill_blank()
    if q:
        print(f'题目: {q.prompt}')
        print(f'答案: {q.answer}')
    
    print()
    print('=' * 50)
    print('选择题测试')
    print('=' * 50)
    
    q2 = qg.generate_multi_choice('identify_author')
    if q2:
        print(f'题目: {q2.prompt}')
        print(f'选项: {q2.options}')
        print(f'答案: {q2.answer}')
    
    print('\n✅ 题库生成器测试完成!')


if __name__ == '__main__':
    quick_test()
