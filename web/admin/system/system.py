# coding:utf-8

# ---------------------------------------------------------------------------------
# Compass Panel
# ---------------------------------------------------------------------------------
# Copyright (C) 2024-2026 Compass Panel. All rights reserved.
# ---------------------------------------------------------------------------------
# Author: Compass Panel Team
# ---------------------------------------------------------------------------------


from flask import Blueprint
from flask import request

from admin.user_login_check import panel_login_required
from utils.system import monitor

import core.mw as mw
import utils.system as sys
import thisdb

blueprint = Blueprint(
    "system", __name__, url_prefix="/system", template_folder="../../templates"
)


# 获取系统的统计信息
@blueprint.route("/system_total", endpoint="system_total", methods=["GET", "POST"])
@panel_login_required
def system_total():
    try:
        import platform, psutil
        data = sys.getMemInfo()
        cpu = sys.getCpuInfo(interval=1)
        data["cpuNum"] = cpu[1]
        data["cpuRealUsed"] = cpu[0]
        data["time"] = sys.getBootTime()
        data["system"] = sys.getSystemVersion()
        data["hostname"] = platform.node()
        data["kernel"] = platform.release()
        data["arch"] = platform.machine()
        import config
        data["version"] = config.APP_VERSION

        # Process statistics
        try:
            proc_count = len(psutil.pids())
            running = sum(1 for p in psutil.process_iter(['status']) if p.info['status'] == 'running')
            sleeping = sum(1 for p in psutil.process_iter(['status']) if p.info['status'] == 'sleeping')
            data["process_total"] = proc_count
            data["process_running"] = running
            data["process_sleeping"] = sleeping
        except Exception:
            data["process_total"] = 0; data["process_running"] = 0; data["process_sleeping"] = 0

        # Network connections
        try:
            conns = psutil.net_connections()
            tcp_count = sum(1 for c in conns if c.type == 1)  # SOCK_STREAM
            data["tcp_count"] = tcp_count
            data["active_connections"] = len([c for c in conns if c.status == 'ESTABLISHED'])
        except Exception:
            data["tcp_count"] = 0; data["active_connections"] = 0

        return data
    except Exception as e:
        return mw.returnData(False, str(e))


# 获取环境信息
@blueprint.route("/get_env_info", endpoint="get_env_info", methods=["GET", "POST"])
@panel_login_required
def get_env_info():
    try:
        return sys.getEnvInfo()
    except Exception as e:
        return mw.returnData(False, str(e))


# 获取系统的网络流量信息
@blueprint.route("/network", endpoint="network")
@panel_login_required
def network():
    try:
        stat = {}
        stat["cpu"] = sys.getCpuInfo()
        stat["load"] = sys.getLoadAverage()
        stat["mem"] = sys.getMemInfo()
        stat["iostat"] = sys.stats().disk()
        stat["network"] = sys.stats().network()
        return stat
    except Exception as e:
        return mw.returnData(False, str(e))


# 获取系统的磁盘信息
@blueprint.route("/disk_info", endpoint="disk_info", methods=["GET", "POST"])
@panel_login_required
def disk_info():
    try:
        data = sys.getDiskInfo()
        return mw.returnData(True, "ok", data)
    except Exception as e:
        return mw.returnData(False, str(e))


# 获取系统的负载统计信息
@blueprint.route("/get_load_average", endpoint="get_load_average", methods=["GET"])
@panel_login_required
def get_load_average():
    try:
        start = request.args.get("start", "")
        end = request.args.get("end", "")
        data = sys.getLoadAverageByDB(start, end)
        return mw.returnData(True, "ok", data)
    except Exception as e:
        return mw.returnData(False, str(e))


# 获取系统的磁盘IO统计信息
@blueprint.route("/get_disk_io", endpoint="get_disk_io", methods=["GET"])
@panel_login_required
def get_disk_io():
    try:
        start = request.args.get("start", "")
        end = request.args.get("end", "")
        data = sys.getDiskIoByDB(start, end)
        return mw.returnData(True, "ok", data)
    except Exception as e:
        return mw.returnData(False, str(e))


# 获取系统的CPU/IO统计信息
@blueprint.route("/get_cpu_io", endpoint="get_cpu_io", methods=["GET"])
@panel_login_required
def get_cpu_io():
    try:
        start = request.args.get("start", "")
        end = request.args.get("end", "")
        data = sys.getCpuIoByDB(start, end)
        return mw.returnData(True, "ok", data)
    except Exception as e:
        return mw.returnData(False, str(e))


# 获取系统网络IO统计信息
@blueprint.route("/get_network_io", endpoint="get_network_io", methods=["GET"])
@panel_login_required
def get_network_io():
    try:
        start = request.args.get("start", "")
        end = request.args.get("end", "")
        data = sys.getNetworkIoByDB(start, end)
        return mw.returnData(True, "ok", data)
    except Exception as e:
        return mw.returnData(False, str(e))


# 重启面板
@blueprint.route("/restart", endpoint="restart", methods=["POST"])
@panel_login_required
def restart():
    mw.restartMw()
    return mw.returnData(True, "面板已重启!")


# 重启面板
@blueprint.route("/restart_server", endpoint="restart_server", methods=["POST"])
@panel_login_required
def restart_server():
    if mw.isAppleSystem():
        return mw.returnData(False, "开发环境不可重起!")
    sys.restartServer()
    return mw.returnData(True, "正在重启服务器!")


# 设置
@blueprint.route("/set_control", endpoint="set_control", methods=["POST"])
@panel_login_required
def set_control():
    stype = request.form.get("type", "")
    day = request.form.get("day", "")

    if stype == "0":
        _day = int(day)
        if _day < 1:
            return mw.returnData(False, "保存天数异常!")
        thisdb.setOption("monitor_day", day, type="monitor")
        thisdb.setOption("monitor_status", "close", type="monitor")
        return mw.returnData(True, "关闭监控成功!")
    elif stype == "1":
        _day = int(day)
        if _day < 1:
            return mw.returnData(False, "保存天数异常!")

        thisdb.setOption("monitor_day", day, type="monitor")
        thisdb.setOption("monitor_status", "open", type="monitor")
        return mw.returnData(True, "开启监控成功!")
    elif stype == "2":
        thisdb.setOption("monitor_only_netio", "close", type="monitor")
        return mw.returnData(True, "关闭仅统计外网成功!")
    elif stype == "3":
        thisdb.setOption("monitor_only_netio", "open", type="monitor")
        return mw.returnData(True, "开启仅统计外网成功!")
    elif stype == "del":
        if not mw.isRestart():
            return mw.returnData(False, "请等待所有安装任务完成再执行")
        monitor.instance().clearDbFile()
        return mw.returnData(True, "清空监控记录成功!")
    else:
        monitor_status = thisdb.getOption(
            "monitor_status", default="open", type="monitor"
        )
        monitor_day = thisdb.getOption("monitor_day", default="30", type="monitor")
        monitor_only_netio = thisdb.getOption(
            "monitor_only_netio", default="open", type="monitor"
        )
        data = {}
        data["day"] = monitor_day
        if monitor_status == "open":
            data["status"] = True
        else:
            data["status"] = False
        if monitor_only_netio == "open":
            data["stat_all_status"] = True
        else:
            data["stat_all_status"] = False

        return data

    return mw.returnData(False, "异常!")


@blueprint.route("/health", endpoint="system_health", methods=["POST"])
@panel_login_required
def system_health():
    """系统健康检查"""
    import psutil, os, time
    health = {"score": 100, "status": "healthy", "checks": [], "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")}

    def check(name, ok, severity="warning"):
        penalty = {"critical": 20, "warning": 10, "info": 5}.get(severity, 10)
        if not ok:
            health["checks"].append({"name": name, "status": "fail", "severity": severity})
            health["score"] -= penalty
        else:
            health["checks"].append({"name": name, "status": "pass", "severity": severity})

    try:
        disk = psutil.disk_usage("/")
        check("磁盘空间 >5GB", disk.free > 5 * 1024**3, "critical")
        check("磁盘使用率 <90%", disk.percent < 90, "warning")
    except Exception:
        check("磁盘检查", False, "warning")

    try:
        mem = psutil.virtual_memory()
        check("可用内存 >256MB", mem.available > 256 * 1024**2, "critical")
    except Exception:
        check("内存检查", False, "critical")

    try:
        cpu = psutil.cpu_percent(interval=0.1)
        check("CPU <95%", cpu < 95, "warning")
    except Exception:
        check("CPU检查", False, "warning")

    check("面板数据库存在", os.path.exists(mw.getPanelDataDir() + "/panel.db"), "critical")

    if health["score"] >= 90:
        health["status"] = "healthy"
    elif health["score"] >= 60:
        health["status"] = "degraded"
    else:
        health["status"] = "unhealthy"
    return mw.returnData(True, health)


@blueprint.route("/info", endpoint="system_info", methods=["POST"])
@panel_login_required
def system_info():
    """系统详细信息"""
    import psutil, platform, time, config as cfg
    disk = psutil.disk_usage("/")
    info = {
        "hostname": platform.node(),
        "os": f"{platform.system()} {platform.release()}",
        "arch": platform.machine(),
        "panel_version": cfg.APP_VERSION,
        "cpu": {"model": platform.processor() or "Unknown", "cores": psutil.cpu_count(), "percent": psutil.cpu_percent(interval=0.1)},
        "memory": {"total": psutil.virtual_memory().total, "used": psutil.virtual_memory().used, "percent": psutil.virtual_memory().percent},
        "disk": {"total": disk.total, "free": disk.free, "percent": disk.percent},
        "uptime": int(time.time() - psutil.boot_time()),
        "panel": {"port": mw.getHostPort(), "admin_path": thisdb.getOption("admin_path") or "", "title": thisdb.getOption("title", default="Compass 指南面板")},
    }
    return mw.returnData(True, info)


@blueprint.route("/services", endpoint="system_services", methods=["POST"])
@panel_login_required
def system_services():
    """Get status of common system services"""
    services = [
        ("nginx", "Nginx"),
        ("mysql", "MySQL"),
        ("mariadb", "MariaDB"),
        ("redis", "Redis"),
        ("postgresql", "PostgreSQL"),
        ("mongod", "MongoDB"),
        ("docker", "Docker"),
        ("php-fpm", "PHP-FPM"),
        ("pure-ftpd", "FTP"),
        ("sshd", "SSH"),
        ("cron", "Cron"),
    ]
    result = []
    for svc_name, svc_label in services:
        status = mw.execShell(f"systemctl is-active {svc_name} 2>/dev/null || echo unknown", timeout=3)[0].strip()
        running = status == "active"
        version = ""
        if running:
            # Try to get version
            ver_cmds = {
                "nginx": "nginx -v 2>&1 | awk '{print $NF}'",
                "mysql": "mysql --version 2>/dev/null | awk '{print $3}'",
                "mariadb": "mariadb --version 2>/dev/null | awk '{print $4}'",
                "redis": "redis-cli --version 2>/dev/null | awk '{print $2}'",
                "postgresql": "psql --version 2>/dev/null | awk '{print $3}'",
                "mongod": "mongod --version 2>/dev/null | head -1 | awk '{print $3}'",
                "docker": "docker --version 2>/dev/null | awk '{print $3}' | tr -d ','",
                "php-fpm": "php -v 2>/dev/null | head -1 | awk '{print $2}'",
                "pure-ftpd": "pure-ftpd --version 2>/dev/null | head -1",
                "sshd": "sshd --version 2>&1 | head -1",
            }
            if svc_name in ver_cmds:
                version = mw.execShell(ver_cmds[svc_name], timeout=3)[0].strip()
        result.append({
            "name": svc_name,
            "label": svc_label,
            "running": running,
            "version": version[:32] if version else "",
        })
    return mw.returnData(True, {"services": result, "count": len(result)})


@blueprint.route("/service_control", endpoint="service_control", methods=["POST"])
@panel_login_required
def service_control():
    """Control a system service (start/stop/restart)"""
    service = request.form.get("service", "").strip()
    action = request.form.get("action", "restart").strip()
    if not service:
        return mw.returnData(False, "服务名不能为空")
    if action not in ("start", "stop", "restart"):
        return mw.returnData(False, "不支持的操作")

    result = mw.execShell(f"systemctl {action} {service} 2>&1", timeout=10)
    success = result[2] == 0
    mw.writeLog("系统服务", f"{action} {service}: {'成功' if success else result[1].strip()}")
    if success:
        return mw.returnData(True, f"服务[{service}] {action} 成功!")
    return mw.returnData(False, f"操作失败: {result[1].strip()[:100]}")


@blueprint.route("/get_server_ip", methods=["POST"])
@panel_login_required
def get_server_ip():
    """Auto-detect server IP address"""
    import socket
    import urllib.request

    # Method 1: Get IP from socket connection
    ip = None
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
    except Exception:
        pass

    # Method 2: Get from hostname
    if not ip or ip == '127.0.0.1':
        try:
            ip = socket.gethostbyname(socket.gethostname())
        except Exception:
            pass

    # Method 3: Get public IP from external service
    if not ip or ip.startswith('127.'):
        try:
            req = urllib.request.Request('https://api.ipify.org', headers={'User-Agent': 'CompassPanel/1.0'})
            with urllib.request.urlopen(req, timeout=5) as resp:
                ip = resp.read().decode('utf-8').strip()
        except Exception:
            pass

    return mw.returnData(True, {"ip": ip or ""})
