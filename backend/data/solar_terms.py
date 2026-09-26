"""诗语雅集 - 24节气数据"""

SOLAR_TERMS = [
    # 春季
    {
        "name": "立春",
        "start_date": "02-03",
        "end_date": "02-18",
        "season": "春",
        "primary_element": "木",
        "description": "立春标志着春季的开始，万物复苏。",
        "keywords": ["春", "风", "柳", "芽", "绿", "暖", "新"],
        "imagery": "春风拂柳、万物复苏"
    },
    {
        "name": "雨水",
        "start_date": "02-19",
        "end_date": "03-05",
        "season": "春",
        "primary_element": "木",
        "description": "降雨开始，雨量渐增。",
        "keywords": ["雨", "水", "润", "湿", "桥", "舟"],
        "imagery": "春雨绵绵、润物无声"
    },
    {
        "name": "惊蛰",
        "start_date": "03-06",
        "end_date": "03-20",
        "season": "春",
        "primary_element": "木",
        "description": "春雷惊醒蛰伏的昆虫。",
        "keywords": ["雷", "虫", "鸣", "醒", "蝶", "鸟"],
        "imagery": "春雷惊梦、蛰虫始振"
    },
    {
        "name": "春分",
        "start_date": "03-21",
        "end_date": "04-04",
        "season": "春",
        "primary_element": "木",
        "description": "昼夜平分，春季过半。",
        "keywords": ["春", "燕", "花", "草", "蝶", "筝"],
        "imagery": "春光明媚、莺飞草长"
    },
    {
        "name": "清明",
        "start_date": "04-05",
        "end_date": "04-19",
        "season": "春",
        "primary_element": "木",
        "description": "春暖花开，慎终追远。",
        "keywords": ["雨", "花", "柳", "风", "酒", "魂"],
        "imagery": "清明时节、杏花春雨"
    },
    {
        "name": "谷雨",
        "start_date": "04-20",
        "end_date": "05-05",
        "season": "春",
        "primary_element": "木",
        "description": "雨生百谷，播种时节。",
        "keywords": ["雨", "谷", "茶", "萍", "桑", "蛙"],
        "imagery": "谷雨润物、浮萍初生"
    },
    # 夏季
    {
        "name": "立夏",
        "start_date": "05-06",
        "end_date": "05-20",
        "season": "夏",
        "primary_element": "火",
        "description": "夏季开始，万物繁茂。",
        "keywords": ["夏", "蛙", "蝉", "荷", "风", "凉"],
        "imagery": "初夏微热、蝉鸣渐起"
    },
    {
        "name": "小满",
        "start_date": "05-21",
        "end_date": "06-05",
        "season": "夏",
        "primary_element": "火",
        "description": "小麦籽粒渐满，夏收在望。",
        "keywords": ["麦", "蚕", "桑", "黄", "满", "熟"],
        "imagery": "小麦饱满、蚕事正忙"
    },
    {
        "name": "芒种",
        "start_date": "06-06",
        "end_date": "06-20",
        "season": "夏",
        "primary_element": "火",
        "description": "有芒的麦子快收，有芒的稻子可种。",
        "keywords": ["麦", "稻", "芒", "种", "梅", "雨"],
        "imagery": "芒种忙种、梅雨时节"
    },
    {
        "name": "夏至",
        "start_date": "06-21",
        "end_date": "07-06",
        "season": "夏",
        "primary_element": "火",
        "description": "白昼最长，阳气至极。",
        "keywords": ["日", "炎", "荷", "蝉", "热", "凉"],
        "imagery": "夏日炎炎、荷花映日"
    },
    {
        "name": "小暑",
        "start_date": "07-07",
        "end_date": "07-22",
        "season": "夏",
        "primary_element": "火",
        "description": "暑气渐盛，但未至极。",
        "keywords": ["风", "雨", "雷", "荷", "萤", "扇"],
        "imagery": "小暑温风、萤火虫舞"
    },
    {
        "name": "大暑",
        "start_date": "07-23",
        "end_date": "08-07",
        "season": "夏",
        "primary_element": "火",
        "description": "一年最热时节。",
        "keywords": ["热", "汗", "荷", "萤", "雷", "雨"],
        "imagery": "大暑酷热、荷叶田田"
    },
    # 秋季
    {
        "name": "立秋",
        "start_date": "08-08",
        "end_date": "08-22",
        "season": "秋",
        "primary_element": "金",
        "description": "秋季开始，暑去凉来。",
        "keywords": ["秋", "叶", "凉", "蝉", "露", "月"],
        "imagery": "一叶知秋、蝉声渐歇"
    },
    {
        "name": "处暑",
        "start_date": "08-23",
        "end_date": "09-07",
        "season": "秋",
        "primary_element": "金",
        "description": "暑气消退，秋意渐浓。",
        "keywords": ["暑", "凉", "露", "云", "雁", "雷"],
        "imagery": "处暑出伏、鹰乃祭鸟"
    },
    {
        "name": "白露",
        "start_date": "09-08",
        "end_date": "09-22",
        "season": "秋",
        "primary_element": "金",
        "description": "露凝而白，秋意渐深。",
        "keywords": ["露", "雁", "月", "桂", "萤", "寒"],
        "imagery": "白露为霜、蒹葭苍苍"
    },
    {
        "name": "秋分",
        "start_date": "09-23",
        "end_date": "10-07",
        "season": "秋",
        "primary_element": "金",
        "description": "昼夜平分，秋季过半。",
        "keywords": ["秋", "月", "桂", "菊", "枫", "雁"],
        "imagery": "秋高气爽、丹桂飘香"
    },
    {
        "name": "寒露",
        "start_date": "10-08",
        "end_date": "10-22",
        "season": "秋",
        "primary_element": "金",
        "description": "露气寒冷，秋意更深。",
        "keywords": ["露", "寒", "菊", "红", "霜", "雁"],
        "imagery": "寒露凝霜、层林尽染"
    },
    {
        "name": "霜降",
        "start_date": "10-23",
        "end_date": "11-06",
        "season": "秋",
        "primary_element": "金",
        "description": "天气渐冷，开始降霜。",
        "keywords": ["霜", "枫", "菊", "柿", "露", "寒"],
        "imagery": "霜降时节、枫红菊黄"
    },
    # 冬季
    {
        "name": "立冬",
        "start_date": "11-07",
        "end_date": "11-21",
        "season": "冬",
        "primary_element": "水",
        "description": "冬季开始，万物收藏。",
        "keywords": ["冬", "寒", "藏", "梅", "雪", "水"],
        "imagery": "立冬初寒、万物收藏"
    },
    {
        "name": "小雪",
        "start_date": "11-22",
        "end_date": "12-06",
        "season": "冬",
        "primary_element": "水",
        "description": "开始降雪，但雪量不大。",
        "keywords": ["雪", "雨", "冰", "寒", "梅", "松"],
        "imagery": "小雪初降、寒梅欲绽"
    },
    {
        "name": "大雪",
        "start_date": "12-07",
        "end_date": "12-21",
        "season": "冬",
        "primary_element": "水",
        "description": "雪量增大，银装素裹。",
        "keywords": ["雪", "寒", "冰", "松", "梅", "风"],
        "imagery": "大雪纷飞、红梅傲雪"
    },
    {
        "name": "冬至",
        "start_date": "12-22",
        "end_date": "01-05",
        "season": "冬",
        "primary_element": "水",
        "description": "白昼最短，阴极阳生。",
        "keywords": ["雪", "寒", "夜", "梅", "阳", "至"],
        "imagery": "冬至阳生、踏雪寻梅"
    },
    {
        "name": "小寒",
        "start_date": "01-06",
        "end_date": "01-19",
        "season": "冬",
        "primary_element": "水",
        "description": "寒气渐盛，但未至极冷。",
        "keywords": ["寒", "雪", "冰", "梅", "风", "年"],
        "imagery": "小寒料峭、腊梅飘香"
    },
    {
        "name": "大寒",
        "start_date": "01-20",
        "end_date": "02-02",
        "season": "冬",
        "primary_element": "水",
        "description": "一年最寒时节。",
        "keywords": ["寒", "雪", "冰", "风", "梅", "年"],
        "imagery": "大寒至极、寒气逼人"
    },
]


def get_current_solar_term(date_str: str) -> dict:
    """根据日期字符串获取当前节气
    
    Args:
        date_str: MM-DD 格式的日期字符串
    
    Returns:
        节气信息字典
    """
    month, day = int(date_str[:2]), int(date_str[3:])
    
    # 冬至特殊处理（跨年）
    if month == 12:
        dongzhi = next(st for st in SOLAR_TERMS if st['name'] == '冬至')
        if (month > int(dongzhi['start_date'][:2]) or 
            (month == int(dongzhi['start_date'][:2]) and 
             day >= int(dongzhi['start_date'][3:]))):
            return dongzhi
    
    # 从后往前找第一个满足 start_date <= 当前日期的节气
    for st in reversed(SOLAR_TERMS):
        st_month = int(st['start_date'][:2])
        st_day = int(st['start_date'][3:])
        
        # 特殊处理冬至（12月22日开始）
        if st['name'] == '冬至':
            continue
            
        if month > st_month or (month == st_month and day >= st_day):
            return st
    
    # 默认返回立春（年份开始时）
    return next(st for st in SOLAR_TERMS if st['name'] == '立春')


def get_solar_term_by_name(name: str) -> dict:
    """根据节气名获取信息"""
    return next((st for st in SOLAR_TERMS if st['name'] == name), None)


if __name__ == '__main__':
    # 测试
    print(get_current_solar_term('02-15'))  # 立春附近
    print(get_current_solar_term('06-22'))  # 夏至附近
    print(get_current_solar_term('12-25'))  # 冬至附近
