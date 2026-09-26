"""诗语雅集 - 初始诗词数据

数据来源：chinese-poetry 项目（MIT License）
https://github.com/chinese-poetry/chinese-poetry

仅包含审核通过、允许分发的内容
"""

INITIAL_POEMS = [
    # 唐诗经典
    {
        "title": "静夜思",
        "author": "李白",
        "dynasty": "唐",
        "lines": [
            {"content": "床前明月光", "tags": ["月", "光", "夜", "思", "乡"], "is_rare": False},
            {"content": "疑是地上霜", "tags": ["霜", "月", "夜", "秋"], "is_rare": False},
            {"content": "举头望明月", "tags": ["月", "望", "夜", "思"], "is_rare": False},
            {"content": "低头思故乡", "tags": ["思", "乡", "月", "情"], "is_rare": False},
        ],
        "source": "chinese-poetry/全唐诗",
        "license": "MIT"
    },
    {
        "title": "春晓",
        "author": "孟浩然",
        "dynasty": "唐",
        "lines": [
            {"content": "春眠不觉晓", "tags": ["春", "眠", "晓", "睡"], "is_rare": False},
            {"content": "处处闻啼鸟", "tags": ["鸟", "春", "声", "鸣"], "is_rare": False},
            {"content": "夜来风雨声", "tags": ["雨", "风", "夜", "声"], "is_rare": False},
            {"content": "花落知多少", "tags": ["花", "落", "春", "雨"], "is_rare": False},
        ],
        "source": "chinese-poetry/全唐诗",
        "license": "MIT"
    },
    {
        "title": "登鹳雀楼",
        "author": "王之涣",
        "dynasty": "唐",
        "lines": [
            {"content": "白日依山尽", "tags": ["日", "山", "暮", "白"], "is_rare": False},
            {"content": "黄河入海流", "tags": ["河", "海", "黄", "流"], "is_rare": False},
            {"content": "欲穷千里目", "tags": ["目", "千", "远", "望"], "is_rare": False},
            {"content": "更上一层楼", "tags": ["楼", "上", "高", "望"], "is_rare": False},
        ],
        "source": "chinese-poetry/全唐诗",
        "license": "MIT"
    },
    {
        "title": "相思",
        "author": "王维",
        "dynasty": "唐",
        "lines": [
            {"content": "红豆生南国", "tags": ["红豆", "南", "春", "物"], "is_rare": False},
            {"content": "春来发几枝", "tags": ["春", "发", "生", "时"], "is_rare": False},
            {"content": "愿君多采撷", "tags": ["君", "采", "愿", "思"], "is_rare": False},
            {"content": "此物最相思", "tags": ["相思", "情", "物", "心"], "is_rare": False},
        ],
        "source": "chinese-poetry/全唐诗",
        "license": "MIT"
    },
    {
        "title": "鹿柴",
        "author": "王维",
        "dynasty": "唐",
        "lines": [
            {"content": "空山不见人", "tags": ["山", "空", "静", "人"], "is_rare": False},
            {"content": "但闻人语响", "tags": ["人", "声", "闻", "语"], "is_rare": False},
            {"content": "返景入深林", "tags": ["林", "深", "光", "日"], "is_rare": False},
            {"content": "复照青苔上", "tags": ["苔", "光", "林", "照"], "is_rare": False},
        ],
        "source": "chinese-poetry/全唐诗",
        "license": "MIT"
    },
    {
        "title": "悯农（其二）",
        "author": "李绅",
        "dynasty": "唐",
        "lines": [
            {"content": "锄禾日当午", "tags": ["锄", "禾", "日", "午", "农"], "is_rare": False},
            {"content": "汗滴禾下土", "tags": ["汗", "土", "禾", "劳"], "is_rare": False},
            {"content": "谁知盘中餐", "tags": ["餐", "食", "米", "盘中"], "is_rare": False},
            {"content": "粒粒皆辛苦", "tags": ["粒", "辛", "苦", "粮"], "is_rare": False},
        ],
        "source": "chinese-poetry/全唐诗",
        "license": "MIT"
    },
    {
        "title": "咏鹅",
        "author": "骆宾王",
        "dynasty": "唐",
        "lines": [
            {"content": "鹅鹅鹅", "tags": ["鹅", "鸟", "鸣"], "is_rare": False},
            {"content": "曲项向天歌", "tags": ["鹅", "天", "歌", "项"], "is_rare": False},
            {"content": "白毛浮绿水", "tags": ["白", "毛", "水", "浮", "绿"], "is_rare": False},
            {"content": "红掌拨清波", "tags": ["红", "波", "水", "清"], "is_rare": False},
        ],
        "source": "chinese-poetry/全唐诗",
        "license": "MIT"
    },
    {
        "title": "望庐山瀑布",
        "author": "李白",
        "dynasty": "唐",
        "lines": [
            {"content": "日照香炉生紫烟", "tags": ["日", "烟", "山", "紫"], "is_rare": False},
            {"content": "遥看瀑布挂前川", "tags": ["瀑", "川", "挂", "看"], "is_rare": False},
            {"content": "飞流直下三千尺", "tags": ["飞", "流", "水", "高"], "is_rare": False},
            {"content": "疑是银河落九天", "tags": ["河", "天", "落", "九"], "is_rare": False},
        ],
        "source": "chinese-poetry/全唐诗",
        "license": "MIT"
    },
    {
        "title": "绝句",
        "author": "杜甫",
        "dynasty": "唐",
        "lines": [
            {"content": "两个黄鹂鸣翠柳", "tags": ["黄", "鹂", "柳", "春", "鸣"], "is_rare": False},
            {"content": "一行白鹭上青天", "tags": ["白", "鹭", "天", "飞", "上"], "is_rare": False},
            {"content": "窗含西岭千秋雪", "tags": ["雪", "窗", "山", "千"], "is_rare": False},
            {"content": "门泊东吴万里船", "tags": ["船", "门", "水", "泊", "万"], "is_rare": False},
        ],
        "source": "chinese-poetry/全唐诗",
        "license": "MIT"
    },
    {
        "title": "江雪",
        "author": "柳宗元",
        "dynasty": "唐",
        "lines": [
            {"content": "千山鸟飞绝", "tags": ["山", "鸟", "飞", "雪", "千"], "is_rare": False},
            {"content": "万径人踪灭", "tags": ["人", "径", "灭", "雪", "万"], "is_rare": False},
            {"content": "孤舟蓑笠翁", "tags": ["舟", "翁", "孤", "雨"], "is_rare": False},
            {"content": "独钓寒江雪", "tags": ["雪", "江", "寒", "钓", "独"], "is_rare": False},
        ],
        "source": "chinese-poetry/全唐诗",
        "license": "MIT"
    },
    {
        "title": "枫桥夜泊",
        "author": "张继",
        "dynasty": "唐",
        "lines": [
            {"content": "月落乌啼霜满天", "tags": ["月", "乌", "霜", "夜", "啼"], "is_rare": False},
            {"content": "江枫渔火对愁眠", "tags": ["江", "枫", "火", "愁", "眠"], "is_rare": False},
            {"content": "姑苏城外寒山寺", "tags": ["城", "寺", "山", "寒"], "is_rare": False},
            {"content": "夜半钟声到客船", "tags": ["钟", "声", "夜", "船", "客"], "is_rare": False},
        ],
        "source": "chinese-poetry/全唐诗",
        "license": "MIT"
    },
    {
        "title": "出塞",
        "author": "王昌龄",
        "dynasty": "唐",
        "lines": [
            {"content": "秦时明月汉时关", "tags": ["月", "关", "秦", "汉", "明"], "is_rare": False},
            {"content": "万里长征人未还", "tags": ["万", "里", "人", "征", "远"], "is_rare": False},
            {"content": "但使龙城飞将在", "tags": ["将", "城", "龙", "飞"], "is_rare": False},
            {"content": "不教胡马度阴山", "tags": ["马", "山", "阴", "度"], "is_rare": False},
        ],
        "source": "chinese-poetry/全唐诗",
        "license": "MIT"
    },
    {
        "title": "凉州词",
        "author": "王翰",
        "dynasty": "唐",
        "lines": [
            {"content": "葡萄美酒夜光杯", "tags": ["酒", "杯", "夜", "光"], "is_rare": False},
            {"content": "欲饮琵琶马上催", "tags": ["酒", "马", "催", "弹"], "is_rare": False},
            {"content": "醉卧沙场君莫笑", "tags": ["沙", "场", "醉", "卧"], "is_rare": False},
            {"content": "古来征战几人回", "tags": ["战", "征", "回", "古"], "is_rare": False},
        ],
        "source": "chinese-poetry/全唐诗",
        "license": "MIT"
    },
    {
        "title": "黄鹤楼送孟浩然之广陵",
        "author": "李白",
        "dynasty": "唐",
        "lines": [
            {"content": "故人西辞黄鹤楼", "tags": ["楼", "鹤", "人", "辞", "西"], "is_rare": False},
            {"content": "烟花三月下扬州", "tags": ["花", "月", "春", "下", "扬"], "is_rare": False},
            {"content": "孤帆远影碧空尽", "tags": ["帆", "空", "远", "孤", "尽"], "is_rare": False},
            {"content": "唯见长江天际流", "tags": ["江", "长", "水", "流", "天"], "is_rare": False},
        ],
        "source": "chinese-poetry/全唐诗",
        "license": "MIT"
    },
    {
        "title": "回乡偶书",
        "author": "贺知章",
        "dynasty": "唐",
        "lines": [
            {"content": "少小离家老大回", "tags": ["回", "家", "少", "老"], "is_rare": False},
            {"content": "乡音无改鬓毛衰", "tags": ["乡", "音", "鬓", "改"], "is_rare": False},
            {"content": "儿童相见不相识", "tags": ["童", "子", "见", "识"], "is_rare": False},
            {"content": "笑问客从何处来", "tags": ["笑", "问", "客", "来"], "is_rare": False},
        ],
        "source": "chinese-poetry/全唐诗",
        "license": "MIT"
    },
    {
        "title": "九月九日忆山东兄弟",
        "author": "王维",
        "dynasty": "唐",
        "lines": [
            {"content": "独在异乡为异客", "tags": ["乡", "客", "独", "异"], "is_rare": False},
            {"content": "每逢佳节倍思亲", "tags": ["节", "思", "亲", "倍"], "is_rare": False},
            {"content": "遥知兄弟登高处", "tags": ["高", "处", "登", "知"], "is_rare": False},
            {"content": "遍插茱萸少一人", "tags": ["茱", "萸", "少", "插"], "is_rare": True},
        ],
        "source": "chinese-poetry/全唐诗",
        "license": "MIT"
    },
    {
        "title": "赠汪伦",
        "author": "李白",
        "dynasty": "唐",
        "lines": [
            {"content": "李白乘舟将欲行", "tags": ["舟", "行", "李", "白", "乘"], "is_rare": False},
            {"content": "忽闻岸上踏歌声", "tags": ["声", "歌", "闻", "岸"], "is_rare": False},
            {"content": "桃花潭水深千尺", "tags": ["桃", "花", "水", "深", "千"], "is_rare": False},
            {"content": "不及汪伦送我情", "tags": ["情", "送", "及", "深"], "is_rare": False},
        ],
        "source": "chinese-poetry/全唐诗",
        "license": "MIT"
    },
    {
        "title": "早发白帝城",
        "author": "李白",
        "dynasty": "唐",
        "lines": [
            {"content": "朝辞白帝彩云间", "tags": ["云", "白", "帝", "辞", "朝"], "is_rare": False},
            {"content": "千里江陵一日还", "tags": ["江", "陵", "千", "里", "还"], "is_rare": False},
            {"content": "两岸猿声啼不住", "tags": ["猿", "声", "啼", "岸", "两"], "is_rare": False},
            {"content": "轻舟已过万重山", "tags": ["舟", "山", "轻", "万", "过"], "is_rare": False},
        ],
        "source": "chinese-poetry/全唐诗",
        "license": "MIT"
    },
    {
        "title": "望天门山",
        "author": "李白",
        "dynasty": "唐",
        "lines": [
            {"content": "天门中断楚江开", "tags": ["门", "江", "天", "开", "断"], "is_rare": False},
            {"content": "碧水东流至此回", "tags": ["水", "碧", "流", "东", "回"], "is_rare": False},
            {"content": "两岸青山相对出", "tags": ["山", "青", "出", "岸", "两"], "is_rare": False},
            {"content": "孤帆一片日边来", "tags": ["帆", "日", "孤", "来", "片"], "is_rare": False},
        ],
        "source": "chinese-poetry/全唐诗",
        "license": "MIT"
    },
    {
        "title": "山行",
        "author": "杜牧",
        "dynasty": "唐",
        "lines": [
            {"content": "远上寒山石径斜", "tags": ["山", "石", "寒", "斜", "远"], "is_rare": False},
            {"content": "白云生处有人家", "tags": ["云", "白", "生", "家", "有"], "is_rare": False},
            {"content": "停车坐爱枫林晚", "tags": ["车", "停", "爱", "枫", "晚"], "is_rare": False},
            {"content": "霜叶红于二月花", "tags": ["叶", "红", "霜", "花", "二"], "is_rare": False},
        ],
        "source": "chinese-poetry/全唐诗",
        "license": "MIT"
    },
    {
        "title": "清明",
        "author": "杜牧",
        "dynasty": "唐",
        "lines": [
            {"content": "清明时节雨纷纷", "tags": ["雨", "清", "时", "节", "纷"], "is_rare": False},
            {"content": "路上行人欲断魂", "tags": ["路", "人", "行", "魂", "断"], "is_rare": False},
            {"content": "借问酒家何处有", "tags": ["酒", "问", "家", "何", "处"], "is_rare": False},
            {"content": "牧童遥指杏花村", "tags": ["童", "花", "村", "指", "杏"], "is_rare": False},
        ],
        "source": "chinese-poetry/全唐诗",
        "license": "MIT"
    },
    {
        "title": "江南春",
        "author": "杜牧",
        "dynasty": "唐",
        "lines": [
            {"content": "千里莺啼绿映红", "tags": ["莺", "绿", "红", "千", "啼"], "is_rare": False},
            {"content": "水村山郭酒旗风", "tags": ["村", "山", "酒", "风", "郭"], "is_rare": False},
            {"content": "南朝四百八十寺", "tags": ["寺", "南", "朝", "四", "百"], "is_rare": True},
            {"content": "多少楼台烟雨中", "tags": ["楼", "台", "烟", "雨", "中"], "is_rare": False},
        ],
        "source": "chinese-poetry/全唐诗",
        "license": "MIT"
    },
    {
        "title": "泊秦淮",
        "author": "杜牧",
        "dynasty": "唐",
        "lines": [
            {"content": "烟笼寒水月笼沙", "tags": ["烟", "寒", "水", "月", "沙"], "is_rare": False},
            {"content": "夜泊秦淮近酒家", "tags": ["泊", "夜", "秦", "淮", "酒"], "is_rare": False},
            {"content": "商女不知亡国恨", "tags": ["女", "亡", "国", "恨", "知"], "is_rare": False},
            {"content": "隔江犹唱后庭花", "tags": ["江", "花", "后", "隔", "唱"], "is_rare": False},
        ],
        "source": "chinese-poetry/全唐诗",
        "license": "MIT"
    },
    {
        "title": "乐游原",
        "author": "李商隐",
        "dynasty": "唐",
        "lines": [
            {"content": "向晚意不适", "tags": ["晚", "意", "向", "适"], "is_rare": False},
            {"content": "驱车登古原", "tags": ["车", "古", "登", "原"], "is_rare": False},
            {"content": "夕阳无限好", "tags": ["夕", "阳", "好", "无", "限"], "is_rare": False},
            {"content": "只是近黄昏", "tags": ["黄", "昏", "近", "只"], "is_rare": False},
        ],
        "source": "chinese-poetry/全唐诗",
        "license": "MIT"
    },
    {
        "title": "咏柳",
        "author": "贺知章",
        "dynasty": "唐",
        "lines": [
            {"content": "碧玉妆成一树高", "tags": ["柳", "碧", "玉", "树", "高"], "is_rare": False},
            {"content": "万条垂下绿丝绦", "tags": ["绿", "丝", "垂", "万", "条"], "is_rare": False},
            {"content": "不知细叶谁裁出", "tags": ["叶", "细", "裁", "出", "知"], "is_rare": False},
            {"content": "二月春风似剪刀", "tags": ["春", "风", "月", "刀", "剪"], "is_rare": False},
        ],
        "source": "chinese-poetry/全唐诗",
        "license": "MIT"
    },
    {
        "title": "宿建德江",
        "author": "孟浩然",
        "dynasty": "唐",
        "lines": [
            {"content": "移舟泊烟渚", "tags": ["舟", "泊", "烟", "移"], "is_rare": False},
            {"content": "日暮客愁新", "tags": ["日", "暮", "客", "愁"], "is_rare": False},
            {"content": "野旷天低树", "tags": ["旷", "野", "天", "树", "低"], "is_rare": False},
            {"content": "江清月近人", "tags": ["江", "清", "月", "近"], "is_rare": False},
        ],
        "source": "chinese-poetry/全唐诗",
        "license": "MIT"
    },
    {
        "title": "竹里馆",
        "author": "王维",
        "dynasty": "唐",
        "lines": [
            {"content": "独坐幽篁里", "tags": ["竹", "幽", "独", "坐"], "is_rare": False},
            {"content": "弹琴复长啸", "tags": ["琴", "声", "长", "啸"], "is_rare": False},
            {"content": "深林人不知", "tags": ["林", "深", "人", "知"], "is_rare": False},
            {"content": "明月来相照", "tags": ["月", "明", "来", "照"], "is_rare": False},
        ],
        "source": "chinese-poetry/全唐诗",
        "license": "MIT"
    },
    {
        "title": "鸟鸣涧",
        "author": "王维",
        "dynasty": "唐",
        "lines": [
            {"content": "人闲桂花落", "tags": ["花", "桂", "闲", "落", "人"], "is_rare": False},
            {"content": "夜静春山空", "tags": ["夜", "静", "山", "春", "空"], "is_rare": False},
            {"content": "月出惊山鸟", "tags": ["月", "鸟", "出", "惊", "山"], "is_rare": False},
            {"content": "时鸣春涧中", "tags": ["鸟", "鸣", "春", "涧"], "is_rare": False},
        ],
        "source": "chinese-poetry/全唐诗",
        "license": "MIT"
    },
    {
        "title": "凉州词",
        "author": "王之涣",
        "dynasty": "唐",
        "lines": [
            {"content": "黄河远上白云间", "tags": ["河", "黄", "云", "白", "间"], "is_rare": False},
            {"content": "一片孤城万仞山", "tags": ["城", "孤", "万", "山", "片"], "is_rare": False},
            {"content": "羌笛何须怨杨柳", "tags": ["笛", "柳", "怨", "羌"], "is_rare": False},
            {"content": "春风不度玉门关", "tags": ["春", "风", "关", "门", "玉"], "is_rare": False},
        ],
        "source": "chinese-poetry/全唐诗",
        "license": "MIT"
    },
]


def get_all_keywords() -> set:
    """获取所有诗句中的关键词"""
    keywords = set()
    for poem in INITIAL_POEMS:
        for line in poem["lines"]:
            for tag in line["tags"]:
                keywords.add(tag)
    return keywords


if __name__ == '__main__':
    print(f"共有 {len(INITIAL_POEMS)} 首诗词")
    keywords = get_all_keywords()
    print(f"共有 {len(keywords)} 个关键词")
