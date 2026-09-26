"""
诗词标注器 - 基于词典 + BERT 的诗意象标签系统
"""
import re
from typing import List, Dict, Set, Optional
from dataclasses import dataclass

# ============ 意象词典 ============

# 季节映射
SEASONS = {
    '春': ['春', '春风', '春雨', '春花', '春草', '春色', '春光', '春日', '春晓', '春眠', '春来', '春去', '新春', '早春', '暮春', '残春', '仲春', '新春'],
    '夏': ['夏', '夏日', '夏风', '夏雨', '烈日', '炎夏', '酷暑', '盛夏', '仲夏', '消夏', '夏夜'],
    '秋': ['秋', '秋风', '秋雨', '秋花', '秋草', '秋色', '秋光', '秋日', '秋月', '秋夜', '深秋', '初秋', '晚秋', '金秋'],
    '冬': ['冬', '冬日', '冬风', '冬雨', '冬雪', '冬夜', '寒冬', '严冬', '隆冬', '仲冬', '残冬', '雪冬']
}

# 五行映射
ELEMENTS = {
    '木': ['木', '春', '青', '东', '风', '柳', '芽', '松', '柏', '竹', '梅', '兰', '菊', '草', '花', '树', '林', '森', '桐', '槐', '桑', '杨', '桃', '桂', '枫', '桂', '梧', '芭', '蕉'],
    '火': ['火', '夏', '赤', '南', '热', '日', '炎', '荷', '莲', '霞', '阳', '光', '明', '炎', '烈', '暑', '燎', '焚', '烽', '烛', '灯', '焰', '焚'],
    '金': ['金', '秋', '白', '西', '月', '霜', '菊', '枫', '银', '玉', '冰', '雪', '寒', '凉', '露', '雁', '砧', '刀', '剑', '弓', '甲', '钟', '镜'],
    '水': ['水', '冬', '黑', '北', '寒', '雪', '冰', '夜', '江', '河', '湖', '海', '泉', '溪', '潭', '波', '浪', '潮', '涛', '泪', '雨', '露', '霜', '雾', '云'],
    '土': ['土', '地', '山', '石', '沙', '尘', '泥', '田', '土', '城', '墙', '屋', '宅', '宫', '殿', '台', '阁', '楼', '廊', '亭', '寺', '观', '墓']
}

# 自然意象
NATURAL_IMAGERY = {
    '天体': ['日', '月', '星', '云', '风', '雨', '雪', '霜', '露', '雾', '雷', '电', '虹'],
    '地理': ['山', '水', '江', '河', '湖', '海', '泉', '溪', '石', '沙', '尘', '泥', '土', '地'],
    '植物': ['花', '草', '木', '树', '竹', '松', '梅', '兰', '菊', '荷', '柳', '枫', '桃', '李', '桂', '梧', '桐', '桑', '杨', '芭', '蕉'],
    '动物': ['鸟', '雁', '鹤', '鹭', '鸦', '鹊', '蝶', '蜂', '蝉', '蛙', '鱼', '龙', '凤', '鹿', '马', '牛', '羊', '犬', '猪', '猿'],
    '建筑': ['楼', '台', '亭', '阁', '寺', '观', '宫', '殿', '城', '墙', '门', '窗', '桥', '舟', '船', '车'],
    '人物': ['人', '子', '君', '妾', '夫', '妻', '母', '父', '兄', '弟', '姐', '妹', '翁', '叟', '童', '叟']
}

# 情感意象
EMOTION_IMAGERY = {
    '思乡': ['乡', '故', '家', '归', '思', '念', '忆', '怀', '归', '客', '旅', '羁', '思乡', '乡愁', '故里', '故乡'],
    '离别': ['离', '别', '送', '行', '征', '辞', '怨', '恨', '思', '念', '忆', '分手', '离别', '离别', '相送'],
    '怀古': ['古', '昔', '旧', '往', '忆', '当年', '昔日', '古人', '古时', '遗迹', '旧迹', '前朝', '往昔'],
    '闺怨': ['闺', '楼', '窗', '帘', '妆', '思', '念', '泪', '肠', '心', '瘦', '独', '孤', '寂', '冷', '清'],
    '山水': ['山', '水', '云', '月', '松', '竹', '石', '泉', '溪', '瀑', '江', '湖', '海', '峰', '岭', '岩']
}

# 常见颜色
COLOR_IMAGERY = {
    '白': ['白', '雪', '霜', '云', '月', '银', '素', '皓', '皎', '白', '素白', '雪白', '银白'],
    '青': ['青', '绿', '翠', '碧', '苍', '青', '翠绿', '碧绿', '青翠', '苍翠', '青碧'],
    '红': ['红', '赤', '丹', '朱', '绯', '绛', '彤', '红', '赤红', '朱红', '丹红', '绯红'],
    '黄': ['黄', '金', '橙', '黄', '金黄', '橙黄', '枯黄', '蜡黄', '焦黄'],
    '黑': ['黑', '墨', '玄', '乌', '暗', '夜', '黑', '墨黑', '乌黑', '漆黑']
}

# 地点/地域
REGION_IMAGERY = {
    '江南': ['江', '南', '江南', '吴', '越', '楚', '湘', '西湖', '钱塘', '潇湘', '洞庭', '江陵', '江浙', '扬州'],
    '塞北': ['塞', '北', '关', '塞北', '边', '漠', '羌', '胡', '胡天', '塞外', '边关', '玉门', '阳关', '燕然', '阴山'],
    '京城': ['京', '城', '长安', '洛阳', '京城', '帝都', '宫', '殿', '阙', '城', '上都', '都城'],
    '山水': ['山', '水', '江', '湖', '泉', '石', '云', '松', '竹', '庐山', '黄山', '泰山', '华山', '西湖', '洞庭']
}


@dataclass
class PoemLine:
    """诗句数据结构"""
    content: str
    normalized: str
    season: Optional[str] = None
    element: Optional[str] = None
    imagery: Set[str] = None
    emotion: Set[str] = None
    color: Optional[str] = None
    region: Optional[str] = None

    def __post_init__(self):
        if self.imagery is None:
            self.imagery = set()
        if self.emotion is None:
            self.emotion = set()

    def to_dict(self) -> dict:
        return {
            'content': self.content,
            'season': self.season,
            'element': self.element,
            'imagery': list(self.imagery),
            'emotion': list(self.emotion),
            'color': self.color,
            'region': self.region
        }


class PoetryTagger:
    """诗词标注器"""

    def __init__(self):
        # 合并所有词典
        self._all_keywords = set()
        for d in [SEASONS, ELEMENTS, NATURAL_IMAGERY, EMOTION_IMAGERY, 
                   COLOR_IMAGERY, REGION_IMAGERY]:
            for words in d.values():
                self._all_keywords.update(words)

    def normalize(self, text: str) -> str:
        """规范化诗句文本"""
        # 去标点
        text = re.sub(r'[，。！？；：、''""（）【】《》\-—…·]', '', text)
        # 去空格
        text = re.sub(r'\s+', '', text)
        return text

    def tag(self, line: str) -> PoemLine:
        """对诗句进行标注"""
        normalized = self.normalize(line)
        
        result = PoemLine(content=line, normalized=normalized)
        
        # 标注季节
        result.season = self._match_category(normalized, SEASONS)
        
        # 标注五行
        result.element = self._match_category(normalized, ELEMENTS)
        
        # 标注自然意象
        for category, keywords in NATURAL_IMAGERY.items():
            for kw in keywords:
                if kw in normalized:
                    result.imagery.add(category)
        
        # 标注情感
        for category, keywords in EMOTION_IMAGERY.items():
            for kw in keywords:
                if kw in normalized:
                    result.emotion.add(category)
        
        # 标注颜色
        for color, keywords in COLOR_IMAGERY.items():
            if any(kw in normalized for kw in keywords):
                result.color = color
                result.imagery.add('颜色')
                break
        
        # 标注地域
        for region, keywords in REGION_IMAGERY.items():
            for kw in keywords:
                if kw in normalized:
                    result.region = region
                    break
            if result.region:
                break
        
        return result

    def tag_batch(self, lines: List[str]) -> List[PoemLine]:
        """批量标注"""
        return [self.tag(line) for line in lines]

    def _match_category(self, text: str, categories: Dict[str, List[str]]) -> Optional[str]:
        """匹配类别"""
        matched = []
        for category, keywords in categories.items():
            for kw in keywords:
                if kw in text:
                    matched.append(category)
                    break
        # 返回匹配最多的类别
        if matched:
            return max(set(matched), key=matched.count)
        return None

    def get_keywords(self, text: str) -> Dict[str, List[str]]:
        """获取文本中包含的关键词"""
        normalized = self.normalize(text)
        result = {}
        
        for name, categories in [
            ('季节', SEASONS),
            ('五行', ELEMENTS),
            ('自然意象', NATURAL_IMAGERY),
            ('情感', EMOTION_IMAGERY),
            ('颜色', COLOR_IMAGERY),
            ('地域', REGION_IMAGERY)
        ]:
            matched = []
            for category, keywords in categories.items():
                for kw in keywords:
                    if kw in normalized:
                        matched.append(f"{category}:{kw}")
            if matched:
                result[name] = matched
        
        return result


# 全局实例
_tagger = None

def get_tagger() -> PoetryTagger:
    global _tagger
    if _tagger is None:
        _tagger = PoetryTagger()
    return _tagger


if __name__ == '__main__':
    # 测试
    tagger = get_tagger()
    
    test_lines = [
        "床前明月光",
        "疑是地上霜",
        "春眠不觉晓",
        "处处闻啼鸟",
        "两个黄鹂鸣翠柳",
        "一行白鹭上青天",
        "千山鸟飞绝",
        "万径人踪灭",
        "明月松间照",
        "清泉石上流",
        "大漠沙如雪",
        "燕山月似钩"
    ]
    
    print("=" * 60)
    print("诗词标注测试")
    print("=" * 60)
    
    for line in test_lines:
        result = tagger.tag(line)
        print(f"\n诗句: {line}")
        print(f"  季节: {result.season or '无'}")
        print(f"  五行: {result.element or '无'}")
        print(f"  意象: {', '.join(result.imagery) if result.imagery else '无'}")
        print(f"  情感: {', '.join(result.emotion) if result.emotion else '无'}")
        print(f"  颜色: {result.color or '无'}")
        print(f"  地域: {result.region or '无'}")
        
        # 详细关键词
        keywords = tagger.get_keywords(line)
        if keywords:
            print(f"  关键词: {keywords}")
