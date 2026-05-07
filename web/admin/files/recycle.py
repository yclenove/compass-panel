# coding:utf-8

# ---------------------------------------------------------------------------------
# MW-Linux面板
# ---------------------------------------------------------------------------------
# copyright (c) 2018-∞(https://github.com/midoks/mdserver-web) All rights reserved.
# ---------------------------------------------------------------------------------
# Author: midoks <midoks@163.com>
# ---------------------------------------------------------------------------------


from flask import request

from admin.user_login_check import panel_login_required
import utils.file as file

from .files import blueprint


# 回收站文件列表
@blueprint.route("/get_recycle_bin", endpoint="get_recycle_bin", methods=["POST"])
@panel_login_required
def get_recycle_bin():
    return file.getRecycleBin()


# 回收站文件恢复
@blueprint.route("/re_recycle_bin", endpoint="re_recycle_bin", methods=["POST"])
@panel_login_required
def re_recycle_bin():
    path = request.form.get("path", "")
    return file.reRecycleBin(path)


@blueprint.route("/del_recycle_bin", endpoint="del_recycle_bin", methods=["POST"])
@panel_login_required
def del_recycle_bin():
    path = request.form.get("path", "")
    return file.delRecycleBin(path)


# 回收站文件
@blueprint.route("/recycle_bin", endpoint="recycle_bin", methods=["POST"])
@panel_login_required
def recycle_bin():
    return file.toggleRecycleBin()


# 回收站文件
@blueprint.route("/close_recycle_bin", endpoint="close_recycle_bin", methods=["POST"])
@panel_login_required
def close_recycle_bin():
    return file.closeRecycleBin()
