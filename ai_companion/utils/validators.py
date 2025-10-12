"""
验证器
包含各种数据验证函数
"""

import re
from typing import Optional

def validate_email(email: str) -> bool:
    """验证邮箱地址"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_url(url: str) -> bool:
    """验证URL"""
    pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return bool(pattern.match(url))

def validate_phone_number(phone: str) -> bool:
    """验证手机号（中国）"""
    pattern = r'^1[3-9]\d{9}$'
    return bool(re.match(pattern, phone))

def validate_username(username: str, min_length: int = 3, max_length: int = 20) -> bool:
    """验证用户名"""
    if not min_length <= len(username) <= max_length:
        return False

    # 只允许字母、数字、下划线
    pattern = r'^[a-zA-Z0-9_]+$'
    return bool(re.match(pattern, username))

def validate_password(password: str, min_length: int = 8) -> bool:
    """验证密码强度"""
    if len(password) < min_length:
        return False

    # 至少包含字母和数字
    has_letter = bool(re.search(r'[a-zA-Z]', password))
    has_digit = bool(re.search(r'\d', password))

    return has_letter and has_digit

def validate_ip_address(ip: str) -> bool:
    """验证IP地址"""
    pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    if not re.match(pattern, ip):
        return False

    # 检查每个数字是否在0-255范围内
    parts = ip.split('.')
    for part in parts:
        try:
            num = int(part)
            if not 0 <= num <= 255:
                return False
        except ValueError:
            return False

    return True

def validate_port(port: int) -> bool:
    """验证端口号"""
    return 1 <= port <= 65535

def validate_api_key(api_key: str) -> bool:
    """验证API密钥格式"""
    if len(api_key) < 10:
        return False

    # 检查是否包含有效字符
    pattern = r'^[a-zA-Z0-9._-]+$'
    return bool(re.match(pattern, api_key))

def validate_json_path(path: str) -> bool:
    """验证JSON路径格式（如：config.llm.api_key）"""
    pattern = r'^[a-zA-Z_][a-zA-Z0-9_]*(\.[a-zA-Z_][a-zA-Z0-9_]*)*$'
    return bool(re.match(pattern, path))

def validate_temperature(temp: float) -> bool:
    """验证LLM温度参数"""
    return 0.0 <= temp <= 2.0

def validate_max_tokens(tokens: int) -> bool:
    """验证最大token数"""
    return 1 <= tokens <= 100000

def validate_yandere_level(level: int) -> bool:
    """验证病娇等级"""
    return 0 <= level <= 4

def validate_persona_state(state: str) -> bool:
    """验证人格状态"""
    valid_states = {"private", "public", "yandere", "tsundere", "deredere"}
    return state in valid_states

def validate_message_content(content: str, max_length: int = 10000) -> bool:
    """验证消息内容"""
    if not content or len(content) > max_length:
        return False

    # 检查是否包含过多空白字符
    if content.strip().count('\n') > 100:  # 超过100行换行
        return False

    return True

def validate_filename(filename: str) -> bool:
    """验证文件名"""
    if not filename:
        return False

    # 检查非法字符
    illegal_chars = r'[<>:"/\\|?*]'
    if re.search(illegal_chars, filename):
        return False

    # 检查长度
    if len(filename) > 255:
        return False

    return True

def validate_color_code(color: str) -> bool:
    """验证颜色代码（十六进制）"""
    pattern = r'^#[0-9A-Fa-f]{6}$'
    return bool(re.match(pattern, color))

def validate_version(version: str) -> bool:
    """验证版本号格式"""
    pattern = r'^\d+\.\d+\.\d+$'
    return bool(re.match(pattern, version))

def validate_domain(domain: str) -> bool:
    """验证域名"""
    pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$'
    return bool(re.match(pattern, domain))