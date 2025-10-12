"""
辅助函数
包含各种实用的工具函数
"""

import re
import uuid
import time
from datetime import datetime
from typing import Optional, Any
import hashlib

def format_time(timestamp: Optional[float] = None, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """格式化时间"""
    if timestamp is None:
        timestamp = time.time()
    return datetime.fromtimestamp(timestamp).strftime(format_str)

def sanitize_input(text: str, max_length: int = 1000) -> str:
    """清理用户输入"""
    if not text:
        return ""

    # 限制长度
    text = text[:max_length]

    # 移除控制字符
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)

    # 移除潜在的恶意代码
    text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r'<iframe[^>]*>.*?</iframe>', '', text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r'javascript:', '', text, flags=re.IGNORECASE)

    # 去除首尾空白
    text = text.strip()

    return text

def generate_session_id() -> str:
    """生成会话ID"""
    return str(uuid.uuid4())

def generate_hash(text: str) -> str:
    """生成文本哈希"""
    return hashlib.md5(text.encode('utf-8')).hexdigest()

def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """截断文本"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix

def extract_keywords(text: str, min_length: int = 2, max_keywords: int = 10) -> list:
    """提取关键词"""
    # 简单的关键词提取
    words = re.findall(r'[\u4e00-\u9fff\w]+', text.lower())
    words = [w for w in words if len(w) >= min_length]

    # 统计词频
    word_count = {}
    for word in words:
        word_count[word] = word_count.get(word, 0) + 1

    # 按频率排序并返回前N个
    keywords = sorted(word_count.items(), key=lambda x: x[1], reverse=True)
    return [word for word, count in keywords[:max_keywords]]

def format_file_size(size_bytes: int) -> str:
    """格式化文件大小"""
    if size_bytes == 0:
        return "0 B"

    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    size = float(size_bytes)

    while size >= 1024.0 and i < len(size_names) - 1:
        size /= 1024.0
        i += 1

    return f"{size:.1f} {size_names[i]}"

def is_valid_json(text: str) -> bool:
    """检查是否为有效的JSON"""
    try:
        import json
        json.loads(text)
        return True
    except (ValueError, TypeError):
        return False

def safe_get_nested(data: dict, path: str, default: Any = None) -> Any:
    """安全获取嵌套字典值"""
    keys = path.split('.')
    current = data

    try:
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default
        return current
    except (KeyError, TypeError):
        return default

def merge_dicts(dict1: dict, dict2: dict) -> dict:
    """合并字典"""
    result = dict1.copy()
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts(result[key], value)
        else:
            result[key] = value
    return result

def retry_function(func, max_retries: int = 3, delay: float = 1.0, exceptions: tuple = (Exception,)):
    """重试装饰器"""
    def wrapper(*args, **kwargs):
        last_exception = None

        for attempt in range(max_retries + 1):
            try:
                return func(*args, **kwargs)
            except exceptions as e:
                last_exception = e
                if attempt < max_retries:
                    time.sleep(delay * (2 ** attempt))  # 指数退避
                else:
                    raise last_exception

    return wrapper

def calculate_similarity(text1: str, text2: str) -> float:
    """计算文本相似度"""
    if not text1 or not text2:
        return 0.0

    # 简单的相似度计算（基于字符交集）
    set1 = set(text1.lower())
    set2 = set(text2.lower())
    intersection = set1.intersection(set2)
    union = set1.union(set2)

    if not union:
        return 0.0

    return len(intersection) / len(union)

def format_duration(seconds: float) -> str:
    """格式化持续时间"""
    if seconds < 60:
        return f"{seconds:.1f}秒"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}分钟"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}小时"

def escape_html(text: str) -> str:
    """HTML转义"""
    html_escape_table = {
        "&": "&amp;",
        '"': "&quot;",
        "'": "&#x27;",
        ">": "&gt;",
        "<": "&lt;",
    }
    return "".join(html_escape_table.get(c, c) for c in text)