# coding:utf-8

# ---------------------------------------------------------------------------------
# Compass Panel
# ---------------------------------------------------------------------------------
# Copyright (C) 2024-2026 Compass Panel. All rights reserved.
# ---------------------------------------------------------------------------------
# Author: Compass Panel Team
# ---------------------------------------------------------------------------------


import os
import re
import json
import time
import threading
from flask import Blueprint, redirect, request

from admin.user_login_check import panel_login_required

import thisdb
import core.mw as mw


def _safe_plugin_name(name):
    """Validate plugin name - alphanumeric, hyphens, underscores only"""
    if not name or not re.match(r'^[\w\-]+$', name):
        return None
    # Prevent path traversal
    if '..' in name or '/' in name or '\\' in name:
        return None
    return name

blueprint = Blueprint(
    "soft", __name__, url_prefix="/soft", template_folder="../../templates"
)

# Install progress tracking
_install_progress = {}
_progress_lock = threading.Lock()


@blueprint.route("/index", endpoint="index")
@panel_login_required
def index():
    return redirect("/" + thisdb.getOption("admin_path", default="") + "/vue/soft")


def _scan_plugins_for_soft():
    """从 plugins 目录扫描已安装的软件"""
    plugins_dir = mw.getPanelDir() + "/plugins"
    if not os.path.exists(plugins_dir):
        return []

    soft_list = []
    plugin_categories = {
        "nginx": "Web服务器", "openresty": "Web服务器", "apache": "Web服务器", "caddy": "Web服务器",
        "php": "PHP环境", "php-apt": "PHP环境", "php-yum": "PHP环境",
        "mysql": "数据库", "mariadb": "数据库", "postgresql": "数据库",
        "mongodb": "数据库", "redis": "数据库", "sqlite": "数据库",
        "memcached": "数据库", "valkey": "数据库",
        "docker": "容器管理",
        "pureftp": "FTP工具",
        "phpmyadmin": "数据库工具", "pgadmin": "数据库工具",
        "fail2ban": "安全工具", "op_waf": "安全工具", "system_safe": "安全工具",
        "webssh": "远程工具", "supervisor": "进程管理",
        "rsyncd": "备份工具",
        "gitea": "开发工具", "gogs": "开发工具",
        "grafana": "监控工具", "prometheus": "监控工具", "loki": "监控工具",
        "zabbix": "监控工具", "zabbix_agent": "监控工具", "nezha": "监控工具",
        "webstats": "统计工具",
        "webhook": "自动化",
        "alist": "文件管理", "cloudreve": "文件管理",
        "swap": "系统工具", "sys-opt": "系统工具", "simpleping": "系统工具",
    }

    for name in sorted(os.listdir(plugins_dir)):
        plugin_path = os.path.join(plugins_dir, name)
        if not os.path.isdir(plugin_path):
            continue

        # Read info.json
        info = {"title": name.replace("-", " ").replace("_", " ").title(), "version": "1.0"}
        for info_file in ["info.json", "Info.json"]:
            ipath = os.path.join(plugin_path, info_file)
            if os.path.exists(ipath):
                try:
                    data = json.loads(mw.readFile(ipath))
                    info.update(data)
                except Exception:
                    pass
                break

        # Check if installed
        installed = os.path.exists(os.path.join(plugin_path, "install.pl"))
        has_install = os.path.exists(os.path.join(plugin_path, "install.sh"))

        soft_list.append({
            "id": len(soft_list) + 1,
            "name": name,
            "title": info.get("title", name),
            "version": info.get("version", info.get("versions", "1.0")),
            "description": info.get("description", info.get("ps", "")),
            "category": plugin_categories.get(name, "其他工具"),
            "author": info.get("author", ""),
            "installed": installed,
            "has_install": has_install,
            "icon": info.get("icon", "Box"),
            "size": _get_dir_size(plugin_path),
        })

    return soft_list


def _get_dir_size(path):
    total = 0
    try:
        for root, dirs, files in os.walk(path, topdown=True):
            dirs[:] = [d for d in dirs if d not in ["__pycache__", ".git", "node_modules"]]
            for f in files:
                try:
                    total += os.path.getsize(os.path.join(root, f))
                except OSError:
                    pass
    except Exception:
        pass
    return total


@blueprint.route("/get_list", endpoint="get_list", methods=["POST"])
@panel_login_required
def get_list():
    """返回软件列表 - 从插件目录扫描"""
    soft_list = _scan_plugins_for_soft()
    return mw.returnData(True, "ok", soft_list)


@blueprint.route("/install", methods=["POST"])
@panel_login_required
def install_soft():
    """安装软件 - 执行插件的 install.sh，支持进度跟踪"""
    name = request.form.get("name", "").strip()
    safe_name = _safe_plugin_name(name)
    if not safe_name:
        return mw.returnData(False, "软件名无效")
    name = safe_name

    plugin_path = os.path.join(mw.getPanelDir(), "plugins", name)
    install_sh = os.path.join(plugin_path, "install.sh")
    if not os.path.exists(install_sh):
        return mw.returnData(False, f"软件[{name}]没有安装脚本")

    # Set initial progress
    task_id = f"install_{name}_{int(time.time())}"
    with _progress_lock:
        _install_progress[task_id] = {
            "name": name,
            "status": "running",
            "progress": 5,
            "message": "开始安装...",
            "start_time": time.strftime("%Y-%m-%d %H:%M:%S"),
        }

    def _install_task():
        try:
            with _progress_lock:
                _install_progress[task_id]["progress"] = 10
                _install_progress[task_id]["message"] = "正在设置执行权限..."

            mw.execShell(f"chmod +x '{install_sh}' 2>/dev/null")

            with _progress_lock:
                _install_progress[task_id]["progress"] = 20
                _install_progress[task_id]["message"] = "正在执行安装脚本..."

            result = mw.execShell(f"cd '{plugin_path}' && bash '{install_sh}' 2>&1", timeout=600)

            if result[2] == 0:
                mw.execShell(f"touch '{plugin_path}/install.pl'")
                with _progress_lock:
                    _install_progress[task_id] = {
                        "name": name,
                        "status": "completed",
                        "progress": 100,
                        "message": f"软件[{name}]安装成功!",
                        "end_time": time.strftime("%Y-%m-%d %H:%M:%S"),
                    }
                mw.writeLog("软件管理", f"安装: {name}")
            else:
                with _progress_lock:
                    _install_progress[task_id]["status"] = "failed"
                    _install_progress[task_id]["progress"] = -1
                    _install_progress[task_id]["message"] = f"安装失败: {result[1][:200]}"
        except Exception as e:
            with _progress_lock:
                _install_progress[task_id]["status"] = "failed"
                _install_progress[task_id]["progress"] = -1
                _install_progress[task_id]["message"] = f"安装异常: {str(e)}"

    # Run install in background thread
    thread = threading.Thread(target=_install_task, daemon=True)
    thread.start()

    return mw.returnData(True, {"task_id": task_id})


@blueprint.route("/install_progress", methods=["POST"])
@panel_login_required
def install_progress():
    """查询安装进度"""
    task_id = request.form.get("task_id", "").strip()
    if not task_id:
        return mw.returnData(False, "task_id不能为空")

    with _progress_lock:
        progress = _install_progress.get(task_id)

    if progress is None:
        return mw.returnData(False, "任务不存在")

    return mw.returnData(True, progress)


@blueprint.route("/uninstall", methods=["POST"])
@panel_login_required
def uninstall_soft():
    """卸载软件"""
    name = request.form.get("name", "").strip()
    safe_name = _safe_plugin_name(name)
    if not safe_name:
        return mw.returnData(False, "软件名无效")
    name = safe_name

    plugin_path = os.path.join(mw.getPanelDir(), "plugins", name)
    uninstall_sh = os.path.join(plugin_path, "uninstall.sh")
    if os.path.exists(uninstall_sh):
        mw.execShell(f"chmod +x '{uninstall_sh}' 2>/dev/null")
        mw.execShell(f"cd '{plugin_path}' && bash '{uninstall_sh}' 2>&1", timeout=300)

    install_pl = os.path.join(plugin_path, "install.pl")
    if os.path.exists(install_pl):
        os.remove(install_pl)

    mw.writeLog("软件管理", f"卸载: {name}")
    return mw.returnData(True, f"软件[{name}]已卸载!")
