"""
工具函数模块
"""
import re
from datetime import datetime, timedelta, timezone


def normalize_text(text: str) -> str:
    """规范化诗句文本"""
    text = text.strip()
    text = re.sub(r'[，。、？！；：""''【】《》『』「」『』]', '', text)
    text = re.sub(r'\s+', '', text)
    text = text.replace('　', '')  # 全角空格
    return text


def generate_room_code() -> str:
    """生成8位房间码"""
    import random
    import string
    chars = string.digits
    return ''.join(random.choices(chars, k=8))


def get_today_date_cn() -> str:
    """获取中国日期字符串 YYYY-MM-DD"""
    return datetime.now(timezone(timedelta(hours=8))).strftime('%Y-%m-%d')


def get_current_time_cn() -> datetime:
    """获取当前中国时间"""
    return datetime.now(timezone(timedelta(hours=8)))
