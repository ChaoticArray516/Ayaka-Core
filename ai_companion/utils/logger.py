"""
日志配置
设置统一的日志格式和处理器
"""

import logging
import os
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import Optional

def setup_logging(config: Optional[dict] = None) -> None:
    """设置日志配置"""
    # 默认配置
    default_config = {
        "level": "INFO",
        "file": "logs/ai_companion.log",
        "max_size": "10MB",
        "backup_count": 5,
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    }

    # 使用传入的配置或默认配置
    log_config = config or default_config

    # 创建日志目录
    log_file = Path(log_config["file"])
    log_file.parent.mkdir(parents=True, exist_ok=True)

    # 解析日志级别
    level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL
    }
    level = level_map.get(log_config["level"].upper(), logging.INFO)

    # 设置根日志级别
    logging.basicConfig(
        level=level,
        format=log_config["format"]
    )

    # 创建文件处理器
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=_parse_size(log_config["max_size"]),
        backupCount=log_config["backup_count"],
        encoding='utf-8'
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(logging.Formatter(log_config["format"]))

    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(logging.Formatter(log_config["format"]))

    # 获取根日志器
    root_logger = logging.getLogger()

    # 移除现有处理器
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # 添加处理器
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    # 设置第三方库日志级别
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("werkzeug").setLevel(logging.WARNING)
    logging.getLogger("engineio").setLevel(logging.WARNING)
    logging.getLogger("socketio").setLevel(logging.WARNING)

def _parse_size(size_str: str) -> int:
    """解析大小字符串"""
    size_str = size_str.upper()
    if size_str.endswith('KB'):
        return int(size_str[:-2]) * 1024
    elif size_str.endswith('MB'):
        return int(size_str[:-2]) * 1024 * 1024
    elif size_str.endswith('GB'):
        return int(size_str[:-2]) * 1024 * 1024 * 1024
    else:
        return int(size_str)