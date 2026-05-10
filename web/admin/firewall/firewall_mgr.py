# coding:utf-8
# Compass Panel - Firewall Management (pluggable backend)
# Auto-detects firewalld/ufw/iptables and provides unified interface

import os
import re
from flask import Blueprint, request

from admin.user_login_check import panel_login_required
import core.mw as mw
import thisdb

blueprint = Blueprint("firewall_mgr", __name__, url_prefix="/firewall/mgr")


def _detect_firewall():
    """Auto-detect the firewall backend"""
    if os.path.exists("/usr/sbin/firewalld") or os.path.exists("/etc/redhat-release"):
        return "firewalld"
    if os.path.exists("/usr/sbin/ufw") or os.path.exists("/usr/bin/apt-get"):
        return "ufw"
    return "iptables"


def _validate_port(port):
    """Validate port number"""
    if not port or not port.isdigit():
        return False
    return 1 <= int(port) <= 65535


def _validate_protocol(proto):
    """Validate protocol - only tcp/udp allowed"""
    return proto.lower() in ("tcp", "udp")


def _validate_ip(ip):
    """Validate IP address format"""
    return bool(re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(/\d{1,2})?$", ip))


def _run_fw_cmd(backend, action, *args):
    """Run a firewall command based on backend type"""
    if backend == "firewalld":
        if action == "status":
            return mw.execShell("systemctl is-active firewalld 2>/dev/null || echo inactive", timeout=5)
        elif action == "start":
            return mw.execShell("systemctl start firewalld 2>&1", timeout=10)
        elif action == "stop":
            return mw.execShell("systemctl stop firewalld 2>&1", timeout=10)
        elif action == "reload":
            return mw.execShell("firewall-cmd --reload 2>&1", timeout=5)
        elif action == "add_port":
            port, proto = args
            return mw.execShell(f"firewall-cmd --permanent --zone=public --add-port={port}/{proto} 2>&1 && firewall-cmd --reload", timeout=5)
        elif action == "del_port":
            port, proto = args
            return mw.execShell(f"firewall-cmd --permanent --zone=public --remove-port={port}/{proto} 2>&1 && firewall-cmd --reload", timeout=5)
        elif action == "add_ip":
            ip = args[0]
            return mw.execShell(f"firewall-cmd --permanent --add-rich-rule='rule family=ipv4 source address=\"{ip}\" drop' 2>&1 && firewall-cmd --reload", timeout=5)
        elif action == "del_ip":
            ip = args[0]
            return mw.execShell(f"firewall-cmd --permanent --remove-rich-rule='rule family=ipv4 source address=\"{ip}\" drop' 2>&1 && firewall-cmd --reload", timeout=5)

    elif backend == "ufw":
        if action == "status":
            return mw.execShell("ufw status 2>/dev/null | head -1", timeout=5)
        elif action == "start":
            return mw.execShell("echo y | ufw enable 2>&1", timeout=10)
        elif action == "stop":
            return mw.execShell("ufw disable 2>&1", timeout=10)
        elif action == "reload":
            return mw.execShell("ufw reload 2>&1", timeout=5)
        elif action == "add_port":
            port, proto = args
            return mw.execShell(f"ufw allow {port}/{proto} 2>&1", timeout=5)
        elif action == "del_port":
            port, proto = args
            return mw.execShell(f"ufw delete allow {port}/{proto} 2>&1", timeout=5)
        elif action == "add_ip":
            ip = args[0]
            return mw.execShell(f"ufw insert 1 deny from {ip} to any 2>&1", timeout=5)
        elif action == "del_ip":
            ip = args[0]
            return mw.execShell(f"ufw delete deny from {ip} to any 2>&1", timeout=5)

    elif backend == "iptables":
        if action == "status":
            return mw.execShell("iptables -L INPUT -n --line-numbers 2>/dev/null | head -5", timeout=5)
        elif action == "start":
            return mw.execShell("echo 'iptables started'", timeout=1)
        elif action == "stop":
            return mw.execShell("iptables -P INPUT ACCEPT; iptables -F 2>&1", timeout=5)
        elif action == "reload":
            return mw.execShell("iptables-restore < /etc/iptables/rules.v4 2>/dev/null || echo 'no saved rules'", timeout=5)
        elif action == "add_port":
            port, proto = args
            return mw.execShell(f"iptables -I INPUT -p {proto} --dport {port} -j ACCEPT 2>&1", timeout=5)
        elif action == "del_port":
            port, proto = args
            return mw.execShell(f"iptables -D INPUT -p {proto} --dport {port} -j ACCEPT 2>&1", timeout=5)
        elif action == "add_ip":
            ip = args[0]
            return mw.execShell(f"iptables -I INPUT -s {ip} -j DROP 2>&1", timeout=5)
        elif action == "del_ip":
            ip = args[0]
            return mw.execShell(f"iptables -D INPUT -s {ip} -j DROP 2>&1", timeout=5)

    return "", "unsupported backend"


# ======== API Endpoints ========

@blueprint.route("/status", methods=["POST"])
@panel_login_required
def firewall_status():
    """Get firewall status"""
    backend = _detect_firewall()
    result = _run_fw_cmd(backend, "status")
    running = "active" in result[0] or "Status: active" in result[0] or "Chain INPUT" in result[0]

    # Get saved rules from database
    rules_db = thisdb.getFirewallList(page=1, size=100) or []
    port_count = len([r for r in rules_db if r.get("port")])

    return mw.returnData(True, {
        "backend": backend,
        "running": running,
        "port_rules": port_count,
    })


@blueprint.route("/toggle", methods=["POST"])
@panel_login_required
def firewall_toggle():
    """Enable/disable firewall"""
    action = request.form.get("action", "status").strip()
    backend = _detect_firewall()

    if action == "start":
        result = _run_fw_cmd(backend, "start")
    elif action == "stop":
        result = _run_fw_cmd(backend, "stop")
    elif action == "restart":
        _run_fw_cmd(backend, "stop")
        result = _run_fw_cmd(backend, "start")
    else:
        result = _run_fw_cmd(backend, "status")

    mw.writeLog("防火墙", f"操作: {action}")
    return mw.returnData(True, f"{backend}: {result[0].strip()[:100]}")


@blueprint.route("/port_rules", methods=["POST"])
@panel_login_required
def list_port_rules():
    """List port rules from database"""
    page = int(request.form.get("page", "1"))
    limit = int(request.form.get("limit", "50"))
    rules = thisdb.getFirewallList(page=page, size=limit)
    return mw.returnData(True, {"rules": rules if rules else []})


@blueprint.route("/add_port", methods=["POST"])
@panel_login_required
def add_port():
    """Add a port rule"""
    port = request.form.get("port", "").strip()
    protocol = request.form.get("protocol", "tcp").strip().lower()
    ps = request.form.get("ps", "").strip()

    if not _validate_port(port):
        return mw.returnData(False, "端口号无效(1-65535)")
    if not _validate_protocol(protocol):
        return mw.returnData(False, "协议无效(仅支持tcp/udp)")

    backend = _detect_firewall()
    result = _run_fw_cmd(backend, "add_port", port, protocol)

    if result[2] == 0:
        thisdb.addFirewall(port, protocol, ps)
        mw.writeLog("防火墙", f"放行端口: {port}/{protocol}")
        return mw.returnData(True, f"端口{port}/{protocol}已放行!")

    return mw.returnData(False, f"操作失败: {result[1]}")


@blueprint.route("/delete_port", methods=["POST"])
@panel_login_required
def delete_port():
    """Delete a port rule"""
    port = request.form.get("port", "").strip()
    protocol = request.form.get("protocol", "tcp").strip().lower()

    if not _validate_port(port):
        return mw.returnData(False, "端口号无效(1-65535)")
    if not _validate_protocol(protocol):
        return mw.returnData(False, "协议无效(仅支持tcp/udp)")

    backend = _detect_firewall()
    result = _run_fw_cmd(backend, "del_port", port, protocol)

    # Delete from DB
    thisdb.deleteFirewallByPort(port)

    mw.writeLog("防火墙", f"删除端口规则: {port}/{protocol}")
    return mw.returnData(True, f"端口{port}/{protocol}已删除!")


@blueprint.route("/ip_rules", methods=["POST"])
@panel_login_required
def list_ip_rules():
    """List IP rules"""
    page = int(request.form.get("page", "1"))
    limit = int(request.form.get("limit", "50"))
    rules = thisdb.getFirewallList(page=page, size=limit)
    ip_rules = [r for r in (rules or []) if not r.get("port")]
    return mw.returnData(True, {"rules": ip_rules})


@blueprint.route("/add_ip", methods=["POST"])
@panel_login_required
def add_ip_rule():
    """Block an IP address"""
    ip = request.form.get("ip", "").strip()

    if not ip:
        return mw.returnData(False, "IP地址不能为空")
    if not re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(/\d{1,2})?$", ip):
        return mw.returnData(False, "IP地址格式无效")

    backend = _detect_firewall()
    result = _run_fw_cmd(backend, "add_ip", ip)

    if result[2] == 0:
        thisdb.addFirewall(ip, "ip", "IP黑名单")
        mw.writeLog("防火墙", f"封锁IP: {ip}")
        return mw.returnData(True, f"IP {ip} 已封锁!")

    return mw.returnData(False, f"操作失败: {result[1]}")


@blueprint.route("/delete_ip", methods=["POST"])
@panel_login_required
def delete_ip_rule():
    """Unblock an IP address"""
    ip = request.form.get("ip", "").strip()
    if not ip or not _validate_ip(ip):
        return mw.returnData(False, "IP地址格式无效")

    backend = _detect_firewall()
    _run_fw_cmd(backend, "del_ip", ip)
    thisdb.deleteFirewallByPort(ip)

    mw.writeLog("防火墙", f"解封IP: {ip}")
    return mw.returnData(True, f"IP {ip} 已解封!")


@blueprint.route("/ssh_port", methods=["POST"])
@panel_login_required
def ssh_port_management():
    """Get/set SSH port"""
    action = request.form.get("action", "get").strip()

    if action == "get":
        result = mw.execShell("grep -E '^#*Port ' /etc/ssh/sshd_config 2>/dev/null | awk '{print $2}' | head -1")[0].strip()
        port = result or "22"
        return mw.returnData(True, {"port": port})

    elif action == "set":
        new_port = request.form.get("port", "").strip()
        if not new_port.isdigit() or int(new_port) < 22 or int(new_port) > 65535:
            return mw.returnData(False, "端口范围22-65535")

        # Don't allow common ports
        if new_port in ["80", "443", "8080", "888", "8888"]:
            return mw.returnData(False, "不能使用常用Web端口")

        # Update sshd_config
        mw.execShell(f"sed -i 's/^#*Port .*/Port {new_port}/' /etc/ssh/sshd_config")
        mw.execShell(f"sed -i 's/^#*Port .*/Port {new_port}/' /etc/ssh/sshd_config.d/*.conf 2>/dev/null")

        # Add firewall rule
        backend = _detect_firewall()
        _run_fw_cmd(backend, "add_port", new_port, "tcp")

        # Restart SSH
        mw.execShell("systemctl restart sshd 2>/dev/null || service ssh restart 2>/dev/null")

        mw.writeLog("防火墙", f"修改SSH端口为: {new_port}")
        return mw.returnData(True, f"SSH端口已改为{new_port}!")
