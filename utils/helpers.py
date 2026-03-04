# utils/helpers.py
"""
通用工具函数模块
提供时间格式化、文件名处理、文本截断等辅助功能
"""

from datetime import datetime
import re


def format_timestamp(timestamp: datetime = None, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    格式化时间戳为字符串
    
    参数:
        timestamp: datetime对象，默认为当前时间
        format_str: 格式化字符串，默认为 "%Y-%m-%d %H:%M:%S"
    
    返回:
        格式化后的时间字符串
    """
    if timestamp is None:
        timestamp = datetime.now()
    return timestamp.strftime(format_str)


def sanitize_filename(filename: str, replacement: str = "_") -> str:
    """
    清理文件名，移除非法字符
    
    参数:
        filename: 原始文件名
        replacement: 替换非法字符的字符串，默认为下划线
    
    返回:
        清理后的安全文件名
    """
    # Windows 非法字符: < > : " / \ | ? *
    illegal_chars = r'[<>:"/\\|?*]'
    sanitized = re.sub(illegal_chars, replacement, filename)
    # 移除首尾空格和点
    sanitized = sanitized.strip('. ')
    # 限制长度
    if len(sanitized) > 200:
        sanitized = sanitized[:200]
    return sanitized


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    截断文本到指定长度
    
    参数:
        text: 原始文本
        max_length: 最大长度，默认为100
        suffix: 截断后添加的后缀，默认为"..."
    
    返回:
        截断后的文本
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def get_warning_color(level: str) -> str:
    """
    根据警告级别返回对应的颜色代码
    
    参数:
        level: 警告级别，如"高危"、"中危"
    
    返回:
        CSS颜色代码
    """
    level = level.strip().lower()
    if "高" in level or "danger" in level:
        return "#dc3545"  # 红色
    elif "中" in level or "warning" in level:
        return "#ffc107"  # 黄色
    else:
        return "#17a2b8"  # 蓝色
