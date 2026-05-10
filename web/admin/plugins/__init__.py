# coding:utf-8

# ---------------------------------------------------------------------------------
# Compass Panel
# ---------------------------------------------------------------------------------
# Copyright (C) 2024-2026 Compass Panel. All rights reserved.
# ---------------------------------------------------------------------------------
# Author: Compass Panel Team
# ---------------------------------------------------------------------------------

import os
import json

from flask import Blueprint, render_template
from flask import request

from utils.plugin import plugin as MwPlugin
from admin.user_login_check import panel_login_required


import core.mw as mw
import utils.config as utils_config
import thisdb


blueprint = Blueprint(
    "plugins", __name__, url_prefix="/plugins", template_folder="../../templates"
)


@blueprint.route("/index", endpoint="index")
@panel_login_required
def index():
    name = thisdb.getOption("template", default="default")
    return render_template("%s/plugins.html" % name)


# 初始化检查,首页提示选择安装
@blueprint.route("/init", endpoint="init", methods=["POST"])
@panel_login_required
def init():
    return MwPlugin.instance().init()


# 初始化安装
@blueprint.route("/init_install", endpoint="init_install", methods=["POST"])
@panel_login_required
def init_install():
    plugin_list = request.form.get("list", "")
    return MwPlugin.instance().initInstall(plugin_list)


# 首页软件展示
@blueprint.route("/index_list", endpoint="index_list", methods=["GET", "POST"])
@panel_login_required
def index_list():
    pg = MwPlugin.instance()
    return pg.getIndexList()


# 插件列表
@blueprint.route("/list", endpoint="list", methods=["GET"])
@panel_login_required
def list():
    plugins_type = request.args.get("type", "0")
    page = request.args.get("p", "1")
    search = request.args.get("search", "").lower()

    if not mw.isNumber(plugins_type):
        plugins_type = 1

    if not mw.isNumber(page):
        page = 0

    pg = MwPlugin.instance()
    return pg.getList(plugins_type, search, int(page))


# 插件设置是否在首页展示
@blueprint.route("/set_index", endpoint="set_index", methods=["POST"])
@panel_login_required
def set_index():
    name = request.form.get("name", "")
    status = request.form.get("status", "0")
    version = request.form.get("version", "")

    pg = MwPlugin.instance()
    if status == "1":
        return pg.addIndex(name, version)
    return pg.removeIndex(name, version)


# 插件安装
@blueprint.route("/install", endpoint="install", methods=["POST"])
@panel_login_required
def install():
    name = request.form.get("name", "")
    version = request.form.get("version", "")

    upgrade = None
    if hasattr(request.form, "upgrade"):
        upgrade = True

    pg = MwPlugin.instance()
    return pg.install(name, version, upgrade=upgrade)


# 插件卸载
@blueprint.route("/uninstall", endpoint="uninstall", methods=["POST"])
@panel_login_required
def uninstall():
    name = request.form.get("name", "")
    version = request.form.get("version", "")
    pg = MwPlugin.instance()
    return pg.uninstall(name, version)


# 文件读取
@blueprint.route("/menu", endpoint="menu", methods=["GET"])
@panel_login_required
def menu():
    data = utils_config.getGlobalVar()
    pg = MwPlugin.instance()
    tag = request.args.get("tag", "")

    hook_menu = thisdb.getOptionByJson("hook_menu", type="hook", default=[])
    content = ""
    for menu_data in hook_menu:
        if tag == menu_data["name"] and "path" in menu_data:
            t = pg.menuGetAbsPath(tag, menu_data["path"])
            content = mw.readFile(t)
    # ------------------------------------------------------------
    data["hook_tag"] = tag
    data["plugin_content"] = content
    return render_template("plugin_menu.html", data=data)


# 文件读取
@blueprint.route("/file", endpoint="file", methods=["GET"])
@panel_login_required
def file():
    name = request.args.get("name", "")
    if name.strip() == "":
        return ""

    f = request.args.get("f", "")
    if f.strip() == "":
        return ""

    file = mw.getPluginDir() + "/" + name + "/" + f
    if not os.path.exists(file):
        return ""

    suffix = mw.getPathSuffix(file)
    if suffix == ".css":
        content = mw.readFile(file)
        from flask import Response
        from flask import make_response

        v = Response(content, headers={"Content-Type": 'text/css; charset="utf-8"'})
        return make_response(v)
    content = open(file, "rb").read()
    return content


# 插件上传
@blueprint.route("/update_zip", endpoint="update_zip", methods=["POST"])
@panel_login_required
def update_zip():
    request_zip = request.files["plugin_zip"]
    return MwPlugin.instance().updateZip(request_zip)


@blueprint.route("/input_zip", endpoint="input_zip", methods=["POST"])
@panel_login_required
def input_zip():
    plugin_name = request.form.get("plugin_name", "")
    tmp_path = request.form.get("tmp_path", "")
    return MwPlugin.instance().inputZipApi(plugin_name, tmp_path)


# 插件设置页
@blueprint.route("/setting", endpoint="setting", methods=["GET"])
@panel_login_required
def setting():
    name = request.args.get("name", "")
    html = mw.getPluginDir() + "/" + name + "/index.html"
    return mw.readFile(html)


# 插件统一回调入口API
@blueprint.route("/run", endpoint="run", methods=["GET", "POST"])
@panel_login_required
def run():
    name = request.form.get("name", "")
    func = request.form.get("func", "")
    version = request.form.get("version", "")
    args = request.form.get("args", "")
    script = request.form.get("script", "index")

    pg = MwPlugin.instance()
    data = pg.run(name, func, version, args, script)
    if data[1] == "":
        r = mw.returnData(True, "OK", data[0].strip())
    else:
        r = mw.returnData(False, data[1].strip())
    return r


# 插件安装进度查询
@blueprint.route("/install_progress", endpoint="install_progress", methods=["POST"])
@panel_login_required
def install_progress():
    """Query installation task progress"""
    task_id = request.form.get("task_id", "").strip()
    if not task_id or not task_id.isdigit():
        return mw.returnData(False, "无效的任务ID")

    task = thisdb.getTaskById(int(task_id))
    if not task:
        return mw.returnData(False, "任务不存在")

    status_map = {
        0: "pending",
        1: "completed",
        -1: "running",
    }
    status_str = status_map.get(task.get("status"), "unknown")

    # Calc progress: pending=10%, running=50%, completed=100%
    progress = {"pending": 10, "running": 50, "completed": 100}.get(status_str, 0)

    # Try to get more granular progress from task log
    try:
        log_file = mw.getPanelTaskExecLog()
        if os.path.exists(log_file):
            log_content = mw.readFile(log_file)
            if log_content and status_str == "running":
                # Check for download progress JSON
                try:
                    speed_data = json.loads(log_content.strip())
                    if isinstance(speed_data, dict) and "pre" in speed_data:
                        progress = speed_data["pre"]
                except (json.JSONDecodeError, ValueError):
                    progress = 50
            message = log_content[:500] if log_content else "任务执行中..."
        else:
            message = "等待执行..." if status_str == "pending" else "任务执行中..."
    except Exception:
        message = f"任务状态: {status_str}"

    return mw.returnData(True, {
        "task_id": task_id,
        "status": status_str,
        "progress": progress,
        "message": message,
        "task_name": task.get("name", ""),
    })


# 插件统一回调入口API
@blueprint.route("/callback", endpoint="callback", methods=["GET", "POST"])
@panel_login_required
def callback():
    name = request.form.get("name", "")
    func = request.form.get("func", "")
    args = request.form.get("args", "")
    script = request.form.get("script", "index")

    pg = MwPlugin.instance()
    data = pg.callback(name, func, args=args, script=script)
    if data[0]:
        return mw.returnData(True, "OK", data[1])
    return mw.returnData(False, data[1])
