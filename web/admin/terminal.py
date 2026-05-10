# coding:utf-8
# Compass Panel - Enhanced Terminal Manager (SSH + Local PTY)
import os
import re
import json
import time
import threading
from flask import Blueprint, request

from admin.user_login_check import panel_login_required
import core.mw as mw
import thisdb

blueprint = Blueprint("terminal", __name__, url_prefix="/terminal")

TERMINAL_SESSIONS = {}
SESSION_LOCK = threading.Lock()

# Built-in quick commands organized by category
QUICK_COMMANDS = {
    "系统信息": [
        {"label": "系统信息", "cmd": "uname -a"},
        {"label": "系统版本", "cmd": "cat /etc/os-release | head -5"},
        {"label": "运行时间", "cmd": "uptime"},
        {"label": "内核版本", "cmd": "uname -r"},
    ],
    "资源监控": [
        {"label": "磁盘使用", "cmd": "df -h"},
        {"label": "内存使用", "cmd": "free -h"},
        {"label": "CPU信息", "cmd": "lscpu | head -10"},
        {"label": "进程列表", "cmd": "ps aux --sort=-%cpu | head -20"},
        {"label": "网络连接", "cmd": "ss -tlnp"},
        {"label": "IO状态", "cmd": "iostat -x 1 3 2>/dev/null || echo iostat not installed"},
    ],
    "Nginx/OpenResty": [
        {"label": "启动", "cmd": "systemctl start openresty"},
        {"label": "停止", "cmd": "systemctl stop openresty"},
        {"label": "重启", "cmd": "systemctl restart openresty"},
        {"label": "状态", "cmd": "systemctl status openresty"},
        {"label": "测试配置", "cmd": "openresty -t"},
        {"label": "查看日志", "cmd": "tail -50 /www/server/openresty/nginx/logs/error.log"},
    ],
    "MySQL": [
        {"label": "启动", "cmd": "systemctl start mysql"},
        {"label": "停止", "cmd": "systemctl stop mysql"},
        {"label": "重启", "cmd": "systemctl restart mysql"},
        {"label": "状态", "cmd": "systemctl status mysql"},
        {"label": "进入CLI", "cmd": "mysql -u root -p"},
        {"label": "进程列表", "cmd": "mysqladmin processlist"},
    ],
    "PHP": [
        {"label": "PHP版本", "cmd": "php -v"},
        {"label": "已安装模块", "cmd": "php -m | sort"},
        {"label": "PHP-FPM状态", "cmd": "systemctl status php*-fpm 2>/dev/null || echo not found"},
        {"label": "PHP配置", "cmd": "php --ini"},
    ],
    "Docker": [
        {"label": "容器列表", "cmd": "docker ps -a"},
        {"label": "镜像列表", "cmd": "docker images"},
        {"label": "资源使用", "cmd": "docker stats --no-stream"},
        {"label": "系统信息", "cmd": "docker info | head -20"},
    ],
    "日志查看": [
        {"label": "面板日志", "cmd": "tail -100 /www/server/compass-panel/logs/panel_error.log"},
        {"label": "系统日志", "cmd": "journalctl -n 50 --no-pager"},
        {"label": "认证日志", "cmd": "tail -50 /var/log/auth.log 2>/dev/null || echo not found"},
        {"label": "消息日志", "cmd": "tail -50 /var/log/messages 2>/dev/null || tail -50 /var/log/syslog"},
    ],
    "文件操作": [
        {"label": "网站目录", "cmd": "ls -la /www/wwwroot/"},
        {"label": "备份目录", "cmd": "ls -la /www/backup/"},
        {"label": "磁盘空间", "cmd": "df -h"},
        {"label": "大文件查找", "cmd": "find /www -type f -size +100M 2>/dev/null | head -20"},
    ],
}

# Terminal themes
TERMINAL_THEMES = {
    "default": {"bg": "#1e1e1e", "fg": "#d4d4d4", "cursor": "#ffffff", "selection": "#264f78"},
    "dracula": {"bg": "#282a36", "fg": "#f8f8f2", "cursor": "#f8f8f2", "selection": "#44475a"},
    "monokai": {"bg": "#272822", "fg": "#f8f8f2", "cursor": "#f8f8f2", "selection": "#49483e"},
    "solarized_dark": {"bg": "#002b36", "fg": "#839496", "cursor": "#93a1a1", "selection": "#073642"},
    "nord": {"bg": "#2e3440", "fg": "#d8dee9", "cursor": "#d8dee9", "selection": "#3b4252"},
    "github_dark": {"bg": "#24292e", "fg": "#e1e4e8", "cursor": "#ffffff", "selection": "#444d56"},
    "tomorrow_night": {"bg": "#1d1f21", "fg": "#c5c8c6", "cursor": "#ffffff", "selection": "#373b41"},
    "one_dark": {"bg": "#282c34", "fg": "#abb2bf", "cursor": "#528bff", "selection": "#3e4451"},
}


@blueprint.route("/commands", methods=["POST"])
@panel_login_required
def get_commands():
    """Get all quick commands"""
    # Load custom commands from DB
    custom = thisdb.getOptionByJson("terminal_custom_cmds", default={})
    all_cmds = dict(QUICK_COMMANDS)
    if custom:
        all_cmds["自定义命令"] = custom
    return mw.returnData(True, {"categories": all_cmds})


@blueprint.route("/save_custom_command", methods=["POST"])
@panel_login_required
def save_custom_command():
    """Save a custom terminal command"""
    label = request.form.get("label", "").strip()
    cmd = request.form.get("cmd", "").strip()
    if not label or not cmd:
        return mw.returnData(False, "标签和命令不能为空")

    custom = thisdb.getOptionByJson("terminal_custom_cmds", default=[])
    custom.append({"label": label, "cmd": cmd})
    thisdb.setOption("terminal_custom_cmds", json.dumps(custom))
    return mw.returnData(True, "命令已保存!")


@blueprint.route("/delete_custom_command", methods=["POST"])
@panel_login_required
def delete_custom_command():
    """Delete a custom terminal command"""
    label = request.form.get("label", "").strip()
    custom = thisdb.getOptionByJson("terminal_custom_cmds", default=[])
    custom = [c for c in custom if c["label"] != label]
    thisdb.setOption("terminal_custom_cmds", json.dumps(custom))
    return mw.returnData(True, "命令已删除!")


@blueprint.route("/themes", methods=["POST"])
@panel_login_required
def get_themes():
    """Get terminal themes"""
    current = thisdb.getOption("terminal_theme", default="default")
    return mw.returnData(True, {"themes": TERMINAL_THEMES, "current": current})


@blueprint.route("/set_theme", methods=["POST"])
@panel_login_required
def set_theme():
    """Set terminal theme"""
    theme = request.form.get("theme", "default").strip()
    if theme in TERMINAL_THEMES:
        thisdb.setOption("terminal_theme", theme)
        return mw.returnData(True, f"主题已切换: {theme}")
    return mw.returnData(False, "不支持的主题")


@blueprint.route("/ssh_connections", methods=["POST"])
@panel_login_required
def list_ssh_connections():
    """List saved SSH connections"""
    conns = thisdb.getOptionByJson("ssh_connections", default=[])
    return mw.returnData(True, {"connections": conns})


@blueprint.route("/save_ssh_connection", methods=["POST"])
@panel_login_required
def save_ssh_connection():
    """Save an SSH connection"""
    name = request.form.get("name", "").strip()
    host = request.form.get("host", "").strip()
    port = request.form.get("port", "22").strip()
    username = request.form.get("username", "root").strip()
    password = request.form.get("password", "").strip()
    auth_method = request.form.get("auth_method", "password").strip()

    if not name or not host:
        return mw.returnData(False, "名称和主机不能为空")
    if not port.isdigit() or int(port) < 1 or int(port) > 65535:
        return mw.returnData(False, "端口无效(1-65535)")
    if not re.match(r'^[\w.\-]+$', host):
        return mw.returnData(False, "主机名无效")

    conns = thisdb.getOptionByJson("ssh_connections", default=[])
    conns.append({
        "id": str(int(time.time())),
        "name": name, "host": host, "port": port,
        "username": username, "password": mw.md5(password) if password else "",
        "auth_method": auth_method,
    })
    thisdb.setOption("ssh_connections", json.dumps(conns))
    return mw.returnData(True, f"SSH连接[{name}]已保存!")


@blueprint.route("/delete_ssh_connection", methods=["POST"])
@panel_login_required
def delete_ssh_connection():
    """Delete an SSH connection"""
    conn_id = request.form.get("id", "").strip()
    conns = thisdb.getOptionByJson("ssh_connections", default=[])
    conns = [c for c in conns if c["id"] != conn_id]
    thisdb.setOption("ssh_connections", json.dumps(conns))
    return mw.returnData(True, "连接已删除!")


@blueprint.route("/sessions", methods=["POST"])
@panel_login_required
def list_sessions():
    """List terminal session recordings"""
    record_dir = mw.getPanelDir() + "/data/terminal_recordings"
    sessions = []
    if os.path.exists(record_dir):
        for f in sorted(os.listdir(record_dir), reverse=True):
            fpath = os.path.join(record_dir, f)
            sessions.append({
                "name": f.replace(".log", ""),
                "path": fpath,
                "size": os.path.getsize(fpath),
                "time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(fpath))),
            })
    return mw.returnData(True, {"sessions": sessions, "count": len(sessions)})


@blueprint.route("/session_content", methods=["POST"])
@panel_login_required
def session_content():
    """Get recorded session content"""
    filepath = request.form.get("file", "").strip()
    if not filepath or not os.path.exists(filepath):
        return mw.returnData(False, "会话文件不存在")
    content = mw.readFile(filepath)
    return mw.returnData(True, {"content": content[-50000:] if len(content) > 50000 else content})


@blueprint.route("/execute", methods=["POST"])
@panel_login_required
def execute_command():
    """Execute a command and return output (for quick commands)"""
    cmd = request.form.get("cmd", "").strip()
    timeout = int(request.form.get("timeout", "30"))
    if not cmd:
        return mw.returnData(False, "命令不能为空")

    # Safety: block dangerous commands
    dangerous_patterns = [
        "rm -rf /", "rm -rf /*", "mkfs.", "dd if=", ":(){ :|:& };:",
        "> /dev/sd", "chmod 777 /", "chmod -r 777 /", "wget.*|.*sh",
        "curl.*|.*sh", "shutdown", "reboot", "halt", "init 0", "init 6",
    ]
    cmd_lower = cmd.lower().strip()
    for pattern in dangerous_patterns:
        if pattern in cmd_lower:
            return mw.returnData(False, f"命令包含危险操作: {pattern}")

    # Additional: block attempts to modify panel files
    panel_dir = mw.getPanelDir()
    if panel_dir and panel_dir.lower() in cmd_lower and any(kw in cmd_lower for kw in ['rm ', 'mv ', 'chmod ', 'chown ']):
        return mw.returnData(False, "禁止修改面板文件")

    # Default timeout to 30 seconds if not specified or unreasonable
    if not timeout or timeout <= 0:
        timeout = 30
    timeout = min(timeout, 60)  # Max 60 seconds for quick commands

    try:
        result = mw.execShell(cmd, timeout=timeout)
        output = (result[0] or "") + (("\n" + result[1]) if result[1] and result[1].strip() else "")
        mw.writeLog("终端", f"执行: {cmd[:100]}")
        return mw.returnData(True, {
            "output": output.strip() or "(无输出)",
            "stdout": result[0] or "",
            "stderr": result[1] or "",
            "exit_code": result[2],
        })
    except TimeoutError:
        return mw.returnData(False, f"命令执行超时({timeout}秒)")
    except Exception as e:
        if "Timeout" in str(e):
            return mw.returnData(False, f"命令执行超时({timeout}秒): {cmd[:50]}...")
        return mw.returnData(False, f"执行失败: {str(e)}")


@blueprint.route("/font_settings", methods=["POST"])
@panel_login_required
def font_settings():
    """Get/set terminal font settings"""
    action = request.form.get("action", "get").strip()
    if action == "get":
        settings = thisdb.getOptionByJson("terminal_font", default={
            "family": "JetBrains Mono, Menlo, Monaco, monospace",
            "size": "14",
            "lineHeight": "1.2",
        })
        return mw.returnData(True, settings)
    elif action == "set":
        family = request.form.get("family", "monospace").strip()
        size = request.form.get("size", "14").strip()
        thisdb.setOption("terminal_font", json.dumps({"family": family, "size": size, "lineHeight": "1.2"}))
        return mw.returnData(True, "字体设置已保存!")
    return mw.returnData(False, "未知操作")


# ==================== SSH Key Management ====================

@blueprint.route("/ssh_keys", methods=["POST"])
@panel_login_required
def list_ssh_keys():
    """List SSH key pairs"""
    ssh_dir = os.path.expanduser("~/.ssh")
    keys = []
    if os.path.exists(ssh_dir):
        for f in sorted(os.listdir(ssh_dir)):
            if f.endswith(".pub"):
                key_name = f.replace(".pub", "")
                priv = os.path.join(ssh_dir, key_name)
                pub = os.path.join(ssh_dir, f)
                keys.append({
                    "name": key_name,
                    "type": _detect_key_type(pub),
                    "size": os.path.getsize(pub),
                    "fingerprint": _key_fingerprint(pub),
                    "created": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(pub))),
                    "has_private": os.path.exists(priv),
                })
    return mw.returnData(True, {"keys": keys, "count": len(keys)})


@blueprint.route("/generate_ssh_key", methods=["POST"])
@panel_login_required
def generate_ssh_key():
    """Generate a new SSH key pair"""
    import re as _re
    key_type = request.form.get("type", "ed25519").strip()
    key_name = request.form.get("name", f"compass_{key_type}").strip()
    comment = request.form.get("comment", "compass-panel-key").strip()
    passphrase = request.form.get("passphrase", "").strip()

    # Validate key name - alphanumeric, hyphens, underscores only
    if not key_name or not _re.match(r'^[\w\-.]+$', key_name) or '..' in key_name or '/' in key_name:
        return mw.returnData(False, "密钥名无效")

    ssh_dir = os.path.expanduser("~/.ssh")
    os.makedirs(ssh_dir, exist_ok=True)

    key_file = os.path.join(ssh_dir, key_name)
    if os.path.exists(key_file):
        return mw.returnData(False, f"密钥[{key_name}]已存在")

    if key_type not in ["ed25519", "rsa", "ecdsa"]:
        return mw.returnData(False, "不支持的密钥类型")

    # Sanitize comment and passphrase for shell safety
    safe_comment = comment.replace("'", "").replace('"', '').replace('\\', '').replace('`', '').replace('$', '')[:64]
    safe_passphrase = passphrase.replace("'", "").replace('"', '').replace('\\', '').replace('`', '').replace('$', '')

    pass_arg = f"-N '{safe_passphrase}'" if safe_passphrase else "-N ''"
    result = mw.execShell(
        f"ssh-keygen -t {key_type} -f '{key_file}' {pass_arg} -C '{safe_comment}' 2>&1"
    )

    if result[2] == 0:
        mw.writeLog("终端管理", f"生成SSH密钥: {key_name}")
        pub_content = mw.readFile(f"{key_file}.pub") if os.path.exists(f"{key_file}.pub") else ""
        return mw.returnData(True, {
            "name": key_name,
            "public_key": pub_content,
            "fingerprint": _key_fingerprint(f"{key_file}.pub"),
        })
    return mw.returnData(False, f"生成失败: {result[1]}")


@blueprint.route("/delete_ssh_key", methods=["POST"])
@panel_login_required
def delete_ssh_key():
    """Delete an SSH key pair"""
    import re as _re
    key_name = request.form.get("name", "").strip()
    if not key_name or not _re.match(r'^[\w\-.]+$', key_name) or '..' in key_name or '/' in key_name:
        return mw.returnData(False, "密钥名无效")

    ssh_dir = os.path.expanduser("~/.ssh")
    priv = os.path.join(ssh_dir, key_name)
    pub = os.path.join(ssh_dir, f"{key_name}.pub")

    deleted = []
    for f in [priv, pub]:
        if os.path.exists(f):
            os.remove(f)
            deleted.append(os.path.basename(f))

    return mw.returnData(True, f"已删除: {', '.join(deleted)}")


@blueprint.route("/read_ssh_key", methods=["POST"])
@panel_login_required
def read_ssh_key():
    """Read SSH public key content"""
    import re as _re
    key_name = request.form.get("name", "").strip()
    which = request.form.get("which", "pub").strip()

    if not key_name or not _re.match(r'^[\w\-.]+$', key_name) or '..' in key_name or '/' in key_name:
        return mw.returnData(False, "密钥名无效")

    ssh_dir = os.path.expanduser("~/.ssh")
    key_file = os.path.join(ssh_dir, f"{key_name}{'.pub' if which == 'pub' else ''}")

    if not os.path.exists(key_file):
        return mw.returnData(False, "密钥文件不存在")

    content = mw.readFile(key_file)
    return mw.returnData(True, {"name": os.path.basename(key_file), "content": content})


# ==================== Batch Execution ====================

@blueprint.route("/batch_execute", methods=["POST"])
@panel_login_required
def batch_execute():
    """Execute a command on multiple saved SSH connections"""
    cmd = request.form.get("cmd", "").strip()
    conn_ids = request.form.get("conn_ids", "").strip()
    timeout = int(request.form.get("timeout", "30"))

    if not cmd:
        return mw.returnData(False, "命令不能为空")
    if not conn_ids:
        return mw.returnData(False, "请选择目标服务器")

    conns = thisdb.getOptionByJson("ssh_connections", default=[])
    id_list = conn_ids.split(",")

    results = []
    for conn in conns:
        if conn["id"] not in id_list:
            continue

        # Validate connection fields
        if not conn.get("port", "").isdigit() or not conn.get("host") or not conn.get("username"):
            results.append({"name": conn.get("name", ""), "host": conn.get("host", ""), "success": False, "output": "连接参数无效"})
            continue

        # Use password file to avoid command line exposure
        import tempfile
        pwd_file = None
        try:
            pwd = conn.get("password", "")
            if pwd:
                pwd_file = tempfile.NamedTemporaryFile(mode='w', suffix='.pwd', delete=False)
                pwd_file.write(pwd)
                pwd_file.close()
                sshpass = f"sshpass -f '{pwd_file.name}'"
            else:
                sshpass = ""

            ssh_cmd = (f"{sshpass} ssh -o StrictHostKeyChecking=no "
                       f"-o ConnectTimeout=5 -p {conn['port']} "
                       f"{conn['username']}@{conn['host']} '{cmd}' 2>&1")

            result = mw.execShell(ssh_cmd, timeout=timeout)
            results.append({
                "name": conn["name"],
                "host": conn["host"],
                "success": result[2] == 0,
                "output": result[0][:1000],
            })
        except Exception as e:
            results.append({"name": conn["name"], "host": conn["host"], "success": False, "output": "执行异常"})
        finally:
            if pwd_file:
                try:
                    os.unlink(pwd_file.name)
                except OSError:
                    pass

    succ = sum(1 for r in results if r["success"])
    mw.writeLog("终端管理", f"批量执行: {cmd[:100]} → {succ}/{len(results)}成功")
    return mw.returnData(True, {"results": results, "total": len(results), "success": succ})


# ==================== Helpers ====================

def _detect_key_type(pub_file):
    if os.path.exists(pub_file):
        content = mw.readFile(pub_file)
        if "ssh-ed25519" in content:
            return "Ed25519"
        elif "ecdsa" in content:
            return "ECDSA"
        elif "ssh-rsa" in content:
            return "RSA"
    return "Unknown"


def _key_fingerprint(pub_file):
    if os.path.exists(pub_file):
        result = mw.execShell(f"ssh-keygen -lf '{pub_file}' 2>/dev/null | awk '{{print $2}}'")[0].strip()
        return result or "N/A"
    return "N/A"
