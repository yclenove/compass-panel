# coding:utf-8

# ---------------------------------------------------------------------------------
# MW-Linux面板
# ---------------------------------------------------------------------------------
# copyright (c) 2018-∞(https://github.com/midoks/mdserver-web) All rights reserved.
# ---------------------------------------------------------------------------------
# Author: midoks <midoks@163.com>
# ---------------------------------------------------------------------------------

"""
安全工具模块
提供输入验证、路径安全检查、CSRF 保护等功能
"""

import os
import re
import secrets
import time
from functools import wraps


# 敏感目录列表 - 不允许文件操作
SENSITIVE_DIRS = [
    "/", "/root", "/boot", "/bin", "/etc", "/home",
    "/dev", "/sbin", "/var", "/usr", "/tmp", "/sys",
    "/proc", "/media", "/mnt", "/opt", "/lib", "/srv",
    "/selinux", "/www/server",
]

# 危险文件扩展名
DANGEROUS_EXTENSIONS = [
    '.exe', '.bat', '.cmd', '.com', '.msi', '.scr',
    '.pif', '.vbs', '.vbe', '.js', '.jse', '.ws',
    '.wsf', '.wsc', '.wsh', '.ps1', '.psm1', '.psd1',
]

# 文件名非法字符
INVALID_FILENAME_CHARS = [';', '&', '|', '*', '<', '>', '`', '$', '(', ')', '{', '}']


def validate_filename(filename):
    """验证文件名是否安全

    Args:
        filename: 文件名

    Returns:
        (bool, str) - (是否合法, 错误信息)
    """
    if not filename:
        return False, "文件名不能为空"

    # 检查长度
    if len(filename) > 255:
        return False, "文件名长度不能超过255个字符"

    # 检查非法字符
    for char in INVALID_FILENAME_CHARS:
        if char in filename:
            return False, f"文件名不能包含字符: {char}"

    # 检查路径遍历
    if '..' in filename or filename.startswith('/'):
        return False, "文件名包含非法路径"

    # 检查空格和点结尾（Windows 兼容）
    if filename.endswith(' ') or filename.endswith('.'):
        return False, "文件名不能以空格或点结尾"

    return True, ""


def validate_path(path, allow_root=False):
    """验证路径是否安全

    Args:
        path: 文件路径
        allow_root: 是否允许根目录操作

    Returns:
        (bool, str) - (是否合法, 错误信息)
    """
    if not path:
        return False, "路径不能为空"

    # 检查原始路径中的路径遍历
    if '..' in path:
        return False, "路径包含非法遍历"

    # 规范化路径
    normalized = os.path.normpath(path)
    # 统一使用正斜杠进行比较
    normalized = normalized.replace('\\', '/')

    # 检查敏感目录
    if not allow_root:
        for sensitive in SENSITIVE_DIRS:
            if normalized == sensitive or normalized.startswith(sensitive + '/'):
                return False, f"不允许操作敏感目录: {sensitive}"

    return True, ""


def validate_input(value, input_type="string", max_length=1000, allow_empty=False):
    """通用输入验证

    Args:
        value: 输入值
        input_type: 输入类型 (string, integer, float, email, ip, port)
        max_length: 最大长度
        allow_empty: 是否允许空值

    Returns:
        (bool, str) - (是否合法, 错误信息)
    """
    if value is None or value == "":
        if allow_empty:
            return True, ""
        return False, "输入不能为空"

    value_str = str(value)

    # 检查长度
    if len(value_str) > max_length:
        return False, f"输入长度不能超过{max_length}个字符"

    # SQL 注入检查
    sql_patterns = [
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|UNION|ALTER)\b)",
        r"(--|;|/\*|\*/)",
        r"(\b(OR|AND)\b\s+\d+\s*=\s*\d+)",
    ]
    for pattern in sql_patterns:
        if re.search(pattern, value_str, re.IGNORECASE):
            return False, "输入包含非法字符"

    # XSS 检查
    xss_patterns = [
        r"<script[^>]*>",
        r"javascript:",
        r"on\w+\s*=",
        r"<iframe",
        r"<object",
        r"<embed",
    ]
    for pattern in xss_patterns:
        if re.search(pattern, value_str, re.IGNORECASE):
            return False, "输入包含非法字符"

    # 类型特定验证
    if input_type == "integer":
        try:
            int(value)
        except (ValueError, TypeError):
            return False, "输入必须是整数"

    elif input_type == "float":
        try:
            float(value)
        except (ValueError, TypeError):
            return False, "输入必须是数字"

    elif input_type == "email":
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, value_str):
            return False, "邮箱格式不正确"

    elif input_type == "ip":
        ip_pattern = (
            r'^((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}'
            r'(25[0-5]|2[0-4]\d|[01]?\d\d?)$'
        )
        if not re.match(ip_pattern, value_str):
            return False, "IP地址格式不正确"

    elif input_type == "port":
        try:
            port_num = int(value)
            if port_num < 1 or port_num > 65535:
                return False, "端口范围必须在1-65535之间"
        except (ValueError, TypeError):
            return False, "端口必须是整数"

    return True, ""


def sanitize_html(text):
    """清理HTML内容，防止XSS

    Args:
        text: HTML文本

    Returns:
        清理后的文本
    """
    if not text:
        return ""

    # 移除危险标签及其内容
    remove_tags = ['script', 'iframe', 'object']
    for tag in remove_tags:
        text = re.sub(
            f'<{tag}[^>]*>.*?</{tag}>', '', text,
            flags=re.IGNORECASE | re.DOTALL,
        )
        text = re.sub(f'<{tag}[^>]*/>', '', text, flags=re.IGNORECASE)
        text = re.sub(f'<{tag}[^>]*>', '', text, flags=re.IGNORECASE)

    # 移除自闭合/空元素标签（如 embed）
    void_tags = ['embed']
    for tag in void_tags:
        text = re.sub(f'<{tag}[^>]*/?>', '', text, flags=re.IGNORECASE)

    # 剥离标签但保留内容（如 form）
    strip_tags = ['form']
    for tag in strip_tags:
        text = re.sub(f'<{tag}[^>]*>', '', text, flags=re.IGNORECASE)
        text = re.sub(f'</{tag}>', '', text, flags=re.IGNORECASE)

    # 移除事件属性
    text = re.sub(r'\s*on\w+\s*=\s*["\'][^"\']*["\']', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\s*on\w+\s*=\s*\S+', '', text, flags=re.IGNORECASE)

    # 移除 javascript: 协议
    text = re.sub(r'javascript\s*:', '', text, flags=re.IGNORECASE)

    return text


def generate_csrf_token():
    """生成CSRF令牌

    Returns:
        CSRF令牌字符串
    """
    return secrets.token_hex(32)


def verify_csrf_token(token, session_token):
    """验证CSRF令牌

    Args:
        token: 提交的令牌
        session_token: 会话中的令牌

    Returns:
        是否验证通过
    """
    if not token or not session_token:
        return False
    return secrets.compare_digest(token, session_token)


def rate_limit(max_requests=100, window=60):
    """速率限制装饰器

    用于限制 API 接口的请求频率，防止暴力攻击。

    Args:
        max_requests: 窗口期内最大请求数，默认 100
        window: 时间窗口（秒），默认 60 秒

    Returns:
        装饰器函数

    Example:
        @app.route('/api/login')
        @rate_limit(max_requests=5, window=60)
        def login():
            # 每分钟最多 5 次请求
            pass
    """
    requests = {}

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            from flask import request, jsonify

            # 获取客户端标识
            client_id = request.remote_addr
            current_time = time.time()

            # 清理过期记录
            if client_id in requests:
                requests[client_id] = [
                    t for t in requests[client_id]
                    if current_time - t < window
                ]
            else:
                requests[client_id] = []

            # 检查速率限制
            if len(requests[client_id]) >= max_requests:
                return jsonify({
                    'status': False,
                    'msg': '请求过于频繁，请稍后再试'
                }), 429

            # 记录请求
            requests[client_id].append(current_time)

            return func(*args, **kwargs)
        return wrapper
    return decorator


def check_password_strength(password):
    """检查密码强度

    Args:
        password: 密码

    Returns:
        (bool, str) - (是否符合要求, 错误信息)
    """
    if not password:
        return False, "密码不能为空"

    if len(password) < 8:
        return False, "密码长度不能少于8位"

    if len(password) > 128:
        return False, "密码长度不能超过128位"

    # 检查是否包含大小写字母和数字
    has_upper = bool(re.search(r'[A-Z]', password))
    has_lower = bool(re.search(r'[a-z]', password))
    has_digit = bool(re.search(r'\d', password))

    if not (has_upper and has_lower and has_digit):
        return False, "密码必须包含大小写字母和数字"

    return True, ""


def mask_sensitive_data(data, fields=None):
    """脱敏敏感数据

    Args:
        data: 数据字典
        fields: 需要脱敏的字段列表

    Returns:
        脱敏后的数据
    """
    if not isinstance(data, dict):
        return data

    if fields is None:
        fields = ['password', 'token', 'secret', 'key', 'api_key', 'access_token']

    masked_data = data.copy()
    for field in fields:
        if field in masked_data:
            value = str(masked_data[field])
            if len(value) > 4:
                masked_data[field] = value[:2] + '*' * (len(value) - 4) + value[-2:]
            else:
                masked_data[field] = '****'

    return masked_data
