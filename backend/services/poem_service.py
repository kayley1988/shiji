"""
诗词服务 - 诗句查询、AI生图提示词生成、拍立得卡片数据
"""
import random
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from config import ART_PROMPTS, POLAROID_STYLES


@dataclass
class PoemCard:
    """诗词卡片数据"""
    id: str
    title: str
    author: str
    dynasty: str
    content: str
    full_text: str
    tags: List[str]
    imagery: List[str]
    source: str
    license: str
    is_rare: bool
    difficulty: str  # easy, medium, hard
    explanation: Optional[str] = None
    background: Optional[str] = None


@dataclass
class PolaroidCard:
    """拍立得风格诗词卡片"""
    poem: PoemCard
    style: str
    frame_config: Dict
    generated_prompt: str
    template_type: str  # classic, vintage, ink, modern


class PoemService:
    """诗词服务"""
    
    # 诗词难度关键词映射
    DIFFICULTY_KEYWORDS = {
        'easy': ['春', '花', '月', '风', '雨', '鸟', '鱼', '云', '山', '水', '日', '夜'],
        'medium': ['思', '归', '愁', '梦', '情', '乡', '别', '望', '泪', '心', '意'],
        'hard': ['禅', '玄', '道', '虚', '空', '寂', '寥', '孤', '独', '魂', '魄']
    }
    
    # 意象分类
    IMAGERY_CATEGORIES = {
        '自然': ['月', '日', '星', '云', '风', '雨', '雪', '霜', '雾', '雷'],
        '山水': ['山', '水', '江', '河', '湖', '海', '泉', '瀑', '石', '松'],
        '植物': ['花', '柳', '梅', '竹', '松', '菊', '荷', '兰', '桃', '枫'],
        '动物': ['鸟', '鹤', '雁', '燕', '蝶', '蜂', '鱼', '蝉', '蛙'],
        '情感': ['思', '念', '愁', '恨', '爱', '怨', '悲', '欢', '喜', '忧'],
        '时间': ['春', '夏', '秋', '冬', '晨', '暮', '夜', '晓', '年', '日'],
        '建筑': ['楼', '台', '寺', '桥', '亭', '关', '城', '门', '窗', '庭'],
        '器物': ['酒', '杯', '灯', '琴', '书', '剑', '舟', '车', '钟', '笛'],
    }
    
    def __init__(self, db_session):
        self.db = db_session
    
    def search_poems(self, keyword: str = None, author: str = None, 
                    dynasty: str = None, tags: List[str] = None,
                    limit: int = 20, offset: int = 0) -> List[PoemCard]:
        """
        搜索诗句
        
        Args:
            keyword: 关键词（诗句中包含）
            author: 作者
            dynasty: 朝代
            tags: 标签列表
            limit: 返回数量限制
            offset: 偏移量
        """
        poems = []
        
        # 模拟数据（实际应从数据库查询）
        sample_poems = [
            {
                'id': 'p001',
                'title': '春晓',
                'author': '孟浩然',
                'dynasty': '唐',
                'lines': ['春眠不觉晓', '处处闻啼鸟', '夜来风雨声', '花落知多少'],
                'tags': ['春', '惜春', '梦境'],
                'imagery': ['春', '鸟', '雨', '花', '风'],
                'is_rare': False,
                'source': '唐诗三百首',
                'license': 'Public Domain'
            },
            {
                'id': 'p002',
                'title': '静夜思',
                'author': '李白',
                'dynasty': '唐',
                'lines': ['床前明月光', '疑是地上霜', '举头望明月', '低头思故乡'],
                'tags': ['思乡', '月夜', '静谧'],
                'imagery': ['月', '霜', '光', '乡'],
                'is_rare': False,
                'source': '唐诗三百首',
                'license': 'Public Domain'
            },
            {
                'id': 'p003',
                'title': '登鹳雀楼',
                'author': '王之涣',
                'dynasty': '唐',
                'lines': ['白日依山尽', '黄河入海流', '欲穷千里目', '更上一层楼'],
                'tags': ['登高', '望远', '哲理'],
                'imagery': ['日', '山', '河', '海', '楼'],
                'is_rare': False,
                'source': '唐诗三百首',
                'license': 'Public Domain'
            },
            {
                'id': 'p004',
                'title': '相思',
                'author': '王维',
                'dynasty': '唐',
                'lines': ['红豆生南国', '春来发几枝', '愿君多采撷', '此物最相思'],
                'tags': ['相思', '红豆', '爱情'],
                'imagery': ['红豆', '春', '南'],
                'is_rare': True,
                'source': '唐诗三百首',
                'license': 'Public Domain'
            },
            {
                'id': 'p005',
                'title': '黄鹤楼送孟浩然之广陵',
                'author': '李白',
                'dynasty': '唐',
                'lines': ['故人西辞黄鹤楼', '烟花三月下扬州', '孤帆远影碧空尽', '唯见长江天际流'],
                'tags': ['送别', '友情', '黄鹤楼'],
                'imagery': ['鹤', '楼', '帆', '江', '烟'],
                'is_rare': False,
                'source': '唐诗三百首',
                'license': 'Public Domain'
            },
            {
                'id': 'p006',
                'title': '枫桥夜泊',
                'author': '张继',
                'dynasty': '唐',
                'lines': ['月落乌啼霜满天', '江枫渔火对愁眠', '姑苏城外寒山寺', '夜半钟声到客船'],
                'tags': ['羁旅', '愁思', '夜景'],
                'imagery': ['月', '乌', '霜', '江', '枫', '钟', '船'],
                'is_rare': True,
                'source': '唐诗三百首',
                'license': 'Public Domain'
            },
            {
                'id': 'p007',
                'title': '出塞',
                'author': '王昌龄',
                'dynasty': '唐',
                'lines': ['秦时明月汉时关', '万里长征人未还', '但使龙城飞将在', '不教胡马度阴山'],
                'tags': ['边塞', '战争', '家国'],
                'imagery': ['月', '关', '龙', '胡', '山'],
                'is_rare': False,
                'source': '唐诗三百首',
                'license': 'Public Domain'
            },
            {
                'id': 'p008',
                'title': '江雪',
                'author': '柳宗元',
                'dynasty': '唐',
                'lines': ['千山鸟飞绝', '万径人踪灭', '孤舟蓑笠翁', '独钓寒江雪'],
                'tags': ['隐逸', '孤独', '冬景'],
                'imagery': ['山', '鸟', '雪', '江', '舟'],
                'is_rare': False,
                'source': '唐诗三百首',
                'license': 'Public Domain'
            },
            {
                'id': 'p009',
                'title': '游子吟',
                'author': '孟郊',
                'dynasty': '唐',
                'lines': ['慈母手中线', '游子身上衣', '临行密密缝', '意恐迟迟归', '谁言寸草心', '报得三春晖'],
                'tags': ['母爱', '亲情', '游子'],
                'imagery': ['母', '线', '衣', '草', '春'],
                'is_rare': True,
                'source': '唐诗三百首',
                'license': 'Public Domain'
            },
            {
                'id': 'p010',
                'title': '清明',
                'author': '杜牧',
                'dynasty': '唐',
                'lines': ['清明时节雨纷纷', '路上行人欲断魂', '借问酒家何处有', '牧童遥指杏花村'],
                'tags': ['清明', '雨景', '思乡'],
                'imagery': ['雨', '酒', '杏花', '村'],
                'is_rare': False,
                'source': '唐诗三百首',
                'license': 'Public Domain'
            }
        ]
        
        for p in sample_poems:
            # 过滤
            if keyword and keyword not in ''.join(p['lines']):
                continue
            if author and author not in p['author']:
                continue
            if dynasty and dynasty not in p['dynasty']:
                continue
            if tags and not any(t in p['tags'] for t in tags):
                continue
            
            poem = PoemCard(
                id=p['id'],
                title=p['title'],
                author=p['author'],
                dynasty=p['dynasty'],
                content='，'.join(p['lines'][:2]),
                full_text='\n'.join(p['lines']),
                tags=p['tags'],
                imagery=p['imagery'],
                source=p['source'],
                license=p['license'],
                is_rare=p['is_rare'],
                difficulty=self._estimate_difficulty(p)
            )
            poems.append(poem)
        
        return poems[offset:offset+limit]
    
    def _estimate_difficulty(self, poem: Dict) -> str:
        """估算诗句难度"""
        text = ''.join(poem['lines'])
        hard_count = sum(1 for k in self.DIFFICULTY_KEYWORDS['hard'] if k in text)
        medium_count = sum(1 for k in self.DIFFICULTY_KEYWORDS['medium'] if k in text)
        
        if hard_count > 0 or poem['is_rare']:
            return 'hard'
        elif medium_count > 0:
            return 'medium'
        return 'easy'
    
    def get_random_poem(self, keyword: str = None, difficulty: str = None) -> Optional[PoemCard]:
        """获取随机诗句"""
        poems = self.search_poems(keyword=keyword)
        
        if difficulty:
            poems = [p for p in poems if p.difficulty == difficulty]
        
        if not poems:
            return None
        
        return random.choice(poems)
    
    def get_poem_by_id(self, poem_id: str) -> Optional[PoemCard]:
        """根据ID获取诗句"""
        poems = self.search_poems()
        for p in poems:
            if p.id == poem_id:
                return p
        return None
    
    def generate_art_prompt(self, poem: PoemCard, style: str = 'default') -> str:
        """
        生成AI生图提示词
        
        Args:
            poem: 诗词卡片
            style: 风格 (default, gongbi, shuimo, dunhuang, modern)
        
        Returns:
            生成的英文提示词
        """
        # 获取风格模板
        template = ART_PROMPTS.get(style, ART_PROMPTS['default'])
        
        # 提取关键意象
        key_imagery = poem.imagery[:4] if poem.imagery else []
        
        # 构建上下文描述
        imagery_desc = '、'.join(key_imagery) if key_imagery else poem.tags[0] if poem.tags else '山水'
        
        # 朝代风格描述
        dynasty_styles = {
            '唐': 'Tang Dynasty style, classical elegance, refined brushwork',
            '宋': 'Song Dynasty style, literati painting, scholarly atmosphere',
            '元': 'Yuan Dynasty style, free brushwork, zen influence',
            '明': 'Ming Dynasty style, ornate yet elegant, decorative',
            '清': 'Qing Dynasty style, refined details, palace aesthetics'
        }
        
        dynasty_desc = dynasty_styles.get(poem.dynasty, 'classical Chinese painting')
        
        # 组装提示词
        prompt = template.format(
            poem_content=f"{poem.full_text}\n\n《{poem.title}》{poem.author}"
        )
        
        # 添加额外描述
        extra_desc = f"""
Traditional Chinese poetry illustration featuring {poem.title} by {poem.author}.
Scene elements: {imagery_desc}
Style: {dynasty_desc}
Atmosphere: {', '.join(poem.tags[:3]) if poem.tags else 'serene'}
"""
        
        return prompt.strip()
    
    def create_polaroid_card(self, poem: PoemCard, style: str = 'classic') -> PolaroidCard:
        """
        创建拍立得风格诗词卡片数据
        
        Args:
            poem: 诗词卡片
            style: 边框风格 (classic, vintage, ink, modern)
        
        Returns:
            拍立得卡片数据
        """
        frame_config = POLAROID_STYLES.get(style, POLAROID_STYLES['classic'])
        
        # 生成AI提示词
        art_prompt = self.generate_art_prompt(poem, style='shuimo')  # 默认用水墨风格
        
        return PolaroidCard(
            poem=poem,
            style=style,
            frame_config=frame_config,
            generated_prompt=art_prompt,
            template_type=style
        )
    
    def get_polaroid_templates(self) -> List[Dict]:
        """获取所有拍立得模板"""
        return [
            {
                'id': 'classic',
                'name': '经典拍立得',
                'description': '纯白边框，简约经典',
                'preview': '/assets/polaroid/classic.svg',
                'config': POLAROID_STYLES['classic']
            },
            {
                'id': 'vintage',
                'name': '复古胶片',
                'description': '米色做旧效果，时光感',
                'preview': '/assets/polaroid/vintage.svg',
                'config': POLAROID_STYLES['vintage']
            },
            {
                'id': 'ink',
                'name': '水墨古卷',
                'description': '宣纸质感，水墨边框',
                'preview': '/assets/polaroid/ink.svg',
                'config': POLAROID_STYLES['ink']
            },
            {
                'id': 'modern',
                'name': '现代简约',
                'description': '窄边框，时尚设计',
                'preview': '/assets/polaroid/modern.svg',
                'config': POLAROID_STYLES['modern']
            }
        ]
    
    def validate_poem_line(self, line: str, required_char: str = None) -> Tuple[bool, str]:
        """
        验证诗句是否有效
        
        Returns:
            (is_valid, message)
        """
        if not line or len(line.strip()) < 4:
            return False, '诗句太短'
        
        # 移除标点
        clean_line = re.sub(r'[，。！？；：""''【】（）、…—]', '', line.strip())
        
        # 检查是否包含必需字
        if required_char and required_char not in clean_line:
            return False, f'诗句需要包含「{required_char}」字'
        
        # 检查是否全为标点或空格
        if not re.search(r'[\u4e00-\u9fff]', clean_line):
            return False, '请输入中文诗句'
        
        # 检查长度限制
        if len(clean_line) > 30:
            return False, '诗句过长'
        
        return True, 'valid'
    
    def get_daily_recommendation(self) -> PoemCard:
        """获取每日推荐诗句"""
        # 基于日期选择，确保每天相同
        import datetime
        today = datetime.date.today()
        seed = today.year * 10000 + today.month * 100 + today.day
        random.seed(seed)
        
        poems = self.search_poems(limit=100)
        if not poems:
            # 返回默认
            return self.get_random_poem()
        
        poem = random.choice(poems)
        random.seed()  # 重置随机种子
        
        return poem
    
    def get_poem_explanation(self, poem: PoemCard) -> Dict:
        """
        获取诗句赏析（简化版）
        实际应从数据库或外部API获取
        """
        explanations = {
            '春晓': '诗人用浅显易懂的语言，描绘了春天早晨的景象，表达了对春光易逝的惋惜之情。',
            '静夜思': '望月思乡，是李白最著名的思乡诗之一，语言朴素而情感深挚。',
            '登鹳雀楼': '诗人登楼远眺，写出了壮阔的景象，并以「欲穷千里目，更上一层楼」表达积极进取的精神。',
            '相思': '借红豆寄托相思之情，是爱情诗中的经典。',
            '黄鹤楼送孟浩然之广陵': '送别诗的绝唱，将离别的情感融入壮美的江景之中。',
        }
        
        return {
            'title': f'《{poem.title}》赏析',
            'author_intro': f'{poem.author}（{poem.dynasty}），唐代著名诗人。',
            'explanation': explanations.get(poem.title, f'这首{poem.dynasty}诗表达了诗人独特的情感和意境。'),
            'keywords': poem.tags,
            'imagery': poem.imagery,
            'writing_skills': [
                '情景交融，借景抒情',
                '语言精炼，意境深远',
                '情感真挚，感人至深'
            ]
        }
