# coding:utf-8
# Compass Panel - Docker Management (S8)
import os
from flask import Blueprint, request

from admin.user_login_check import panel_login_required
import core.mw as mw
import thisdb

blueprint = Blueprint("docker_mgr", __name__, url_prefix="/docker")


def _docker(cmd):
    return mw.execShell(f"docker {cmd} 2>&1")[0]


@blueprint.route("/status", methods=["POST"])
@panel_login_required
def docker_status():
    result = mw.execShell("systemctl is-active docker 2>/dev/null || echo unknown")[0].strip()
    running = "active" in result
    info = {}
    if running:
        try:
            info["containers"] = _docker("ps -a --format '{{.ID}}' | wc -l").strip()
            info["images"] = _docker("images --format '{{.ID}}' | wc -l").strip()
            info["version"] = _docker("version --format '{{.Server.Version}}'").strip()
        except Exception:
            pass
    return mw.returnData(True, {"running": running, "info": info})


@blueprint.route("/install", methods=["POST"])
@panel_login_required
def docker_install():
    """Install Docker using the official install script"""
    # Check if already installed
    check = mw.execShell("which docker 2>/dev/null")[0].strip()
    if check:
        # Try starting if installed but not running
        mw.execShell("systemctl start docker 2>/dev/null")
        mw.execShell("systemctl enable docker 2>/dev/null")
        return mw.returnData(True, "Docker已安装，正在启动服务...")

    # Install using official script
    result = mw.execShell("curl -fsSL https://get.docker.com | bash 2>&1", timeout=300)
    if result[2] == 0:
        mw.execShell("systemctl start docker 2>/dev/null")
        mw.execShell("systemctl enable docker 2>/dev/null")
        mw.writeLog("Docker", "Docker安装完成")
        return mw.returnData(True, "Docker安装完成!")
    return mw.returnData(False, f"安装失败: {result[1][:200] if result[1] else '未知错误'}")


@blueprint.route("/containers", methods=["POST"])
@panel_login_required
def list_containers():
    all_flag = request.form.get("all", "1") == "1"
    fmt = "{{.ID}}\t{{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}"
    cmd = f"ps {'-a' if all_flag else ''} --format '{fmt}'"
    lines = [l.split("\t") for l in _docker(cmd).strip().split("\n") if l.strip()]
    containers = [{"id": l[0], "name": l[1], "image": l[2], "status": l[3], "ports": l[4] if len(l) > 4 else ""} for l in lines]
    return mw.returnData(True, {"containers": containers, "count": len(containers)})


@blueprint.route("/container_action", methods=["POST"])
@panel_login_required
def container_action():
    name = request.form.get("name", "").strip()
    action = request.form.get("action", "restart").strip()
    if not name:
        return mw.returnData(False, "容器名不能为空")
    valid_actions = ["start", "stop", "restart", "pause", "unpause", "rm"]
    if action not in valid_actions:
        return mw.returnData(False, "不支持的操作")

    result = _docker(f"{action} {name}")
    mw.writeLog("Docker", f"{action} 容器 {name}")
    return mw.returnData(True, f"执行完成: {result}")


@blueprint.route("/container_logs", methods=["POST"])
@panel_login_required
def container_logs():
    name = request.form.get("name", "").strip()
    tail = request.form.get("tail", "100").strip()
    if not name:
        return mw.returnData(False, "容器名不能为空")
    logs = _docker(f"logs --tail {tail} {name}")
    return mw.returnData(True, {"logs": logs})


@blueprint.route("/container_inspect", methods=["POST"])
@panel_login_required
def container_inspect():
    name = request.form.get("name", "").strip()
    if not name:
        return mw.returnData(False, "容器名不能为空")
    import json
    try:
        info = json.loads(_docker(f"inspect {name}"))
        return mw.returnData(True, info[0] if info else {})
    except json.JSONDecodeError:
        return mw.returnData(False, "获取失败")


@blueprint.route("/images", methods=["POST"])
@panel_login_required
def list_images():
    fmt = "{{.Repository}}:{{.Tag}}\t{{.ID}}\t{{.Size}}\t{{.CreatedSince}}"
    lines = [l.split("\t") for l in _docker(f"images --format '{fmt}'").strip().split("\n") if l.strip()]
    images = [{"name": l[0], "id": l[1], "size": l[2], "created": l[3] if len(l) > 3 else ""} for l in lines]
    return mw.returnData(True, {"images": images, "count": len(images)})


@blueprint.route("/pull_image", methods=["POST"])
@panel_login_required
def pull_image():
    image = request.form.get("image", "").strip()
    if not image:
        return mw.returnData(False, "镜像名不能为空")
    result = _docker(f"pull {image}")
    mw.writeLog("Docker", f"拉取镜像: {image}")
    return mw.returnData(True, result)


@blueprint.route("/remove_image", methods=["POST"])
@panel_login_required
def remove_image():
    image = request.form.get("image", "").strip()
    if not image:
        return mw.returnData(False, "镜像名不能为空")
    _docker(f"rmi {image}")
    return mw.returnData(True, f"镜像{image}已删除!")


@blueprint.route("/networks", methods=["POST"])
@panel_login_required
def list_networks():
    result = _docker("network ls --format '{{.Name}}\t{{.Driver}}\t{{.Scope}}'")
    lines = [l.split("\t") for l in result.strip().split("\n") if l.strip()]
    networks = [{"name": l[0], "driver": l[1], "scope": l[2] if len(l) > 2 else ""} for l in lines]
    return mw.returnData(True, {"networks": networks, "count": len(networks)})


@blueprint.route("/volumes", methods=["POST"])
@panel_login_required
def list_volumes():
    result = _docker("volume ls --format '{{.Name}}\t{{.Driver}}\t{{.Mountpoint}}'")
    lines = [l.split("\t") for l in result.strip().split("\n") if l.strip()]
    volumes = [{"name": l[0], "driver": l[1], "mountpoint": l[2] if len(l) > 2 else ""} for l in lines]
    return mw.returnData(True, {"volumes": volumes, "count": len(volumes)})


@blueprint.route("/prune", methods=["POST"])
@panel_login_required
def docker_prune():
    target = request.form.get("target", "all").strip()
    if target in ["all", "containers"]:
        _docker("container prune -f")
    if target in ["all", "images"]:
        _docker("image prune -f")
    if target in ["all", "volumes"]:
        _docker("volume prune -f")
    if target in ["all", "networks"]:
        _docker("network prune -f")
    return mw.returnData(True, f"已清理: {target}")


# ==================== Docker Compose ====================

def _compose(cmd, project_dir=None):
    """Execute docker-compose command"""
    dir_opt = f"-f '{project_dir}/docker-compose.yml'" if project_dir else ""
    return mw.execShell(f"docker-compose {dir_opt} {cmd} 2>&1")[0]


@blueprint.route("/compose/status", methods=["POST"])
@panel_login_required
def compose_status():
    """Check docker-compose availability"""
    result = mw.execShell("docker-compose version 2>/dev/null || docker compose version 2>/dev/null")[0]
    installed = "version" in result.lower()
    return mw.returnData(True, {"installed": installed, "version": result.strip()})


@blueprint.route("/compose/list", methods=["POST"])
@panel_login_required
def compose_list():
    """List docker-compose projects"""
    # Check common compose project directories
    compose_dirs = []
    search_paths = ["/opt", "/home", "/root", "/www/server"]

    for search_path in search_paths:
        if not os.path.exists(search_path):
            continue
        for root, dirs, files in os.walk(search_path):
            depth = root.replace(search_path, "").count(os.sep)
            if depth > 3:
                dirs[:] = []
                continue
            if "docker-compose.yml" in files or "docker-compose.yaml" in files:
                compose_file = os.path.join(root, "docker-compose.yml" if "docker-compose.yml" in files else "docker-compose.yaml")
                compose_dirs.append({
                    "path": root,
                    "name": os.path.basename(root),
                    "file": compose_file,
                })

    return mw.returnData(True, {"projects": compose_dirs, "count": len(compose_dirs)})


@blueprint.route("/compose/up", methods=["POST"])
@panel_login_required
def compose_up():
    """Start docker-compose project"""
    project_dir = request.form.get("path", "").strip()
    detach = request.form.get("detach", "1") == "1"
    if not project_dir:
        return mw.returnData(False, "项目路径不能为空")

    compose_file = os.path.join(project_dir, "docker-compose.yml")
    if not os.path.exists(compose_file):
        compose_file = os.path.join(project_dir, "docker-compose.yaml")
    if not os.path.exists(compose_file):
        return mw.returnData(False, "docker-compose.yml 不存在")

    detach_flag = "-d" if detach else ""
    result = mw.execShell(f"cd '{project_dir}' && docker-compose up {detach_flag} 2>&1")
    mw.writeLog("Docker", f"Compose启动: {project_dir}")
    return mw.returnData(True, {"output": result[0][:2000]})


@blueprint.route("/compose/down", methods=["POST"])
@panel_login_required
def compose_down():
    """Stop and remove docker-compose project"""
    project_dir = request.form.get("path", "").strip()
    if not project_dir:
        return mw.returnData(False, "项目路径不能为空")

    result = mw.execShell(f"cd '{project_dir}' && docker-compose down 2>&1")
    mw.writeLog("Docker", f"Compose停止: {project_dir}")
    return mw.returnData(True, {"output": result[0][:2000]})


@blueprint.route("/compose/logs", methods=["POST"])
@panel_login_required
def compose_logs():
    """Get docker-compose project logs"""
    project_dir = request.form.get("path", "").strip()
    tail = request.form.get("tail", "100").strip()
    service = request.form.get("service", "").strip()

    if not project_dir:
        return mw.returnData(False, "项目路径不能为空")

    # Sanitize: tail must be a number, service must be alphanumeric
    try:
        tail = str(int(tail))
    except (ValueError, TypeError):
        tail = "100"
    if service and not service.replace('-', '').replace('_', '').isalnum():
        return mw.returnData(False, "无效的服务名")
    svc_flag = service if service else ""
    result = mw.execShell(f"cd '{project_dir}' && docker-compose logs --tail {tail} {svc_flag} 2>&1")
    return mw.returnData(True, {"logs": result[0][:10000]})


@blueprint.route("/compose/pull", methods=["POST"])
@panel_login_required
def compose_pull():
    """Pull images for docker-compose project"""
    project_dir = request.form.get("path", "").strip()
    if not project_dir:
        return mw.returnData(False, "项目路径不能为空")

    result = mw.execShell(f"cd '{project_dir}' && docker-compose pull 2>&1")
    return mw.returnData(True, {"output": result[0][:2000]})


@blueprint.route("/compose/restart", methods=["POST"])
@panel_login_required
def compose_restart():
    """Restart docker-compose project"""
    project_dir = request.form.get("path", "").strip()
    service = request.form.get("service", "").strip()

    if not project_dir:
        return mw.returnData(False, "项目路径不能为空")

    svc_flag = service if service else ""
    result = mw.execShell(f"cd '{project_dir}' && docker-compose restart {svc_flag} 2>&1")
    mw.writeLog("Docker", f"Compose重启: {project_dir}")
    return mw.returnData(True, {"output": result[0][:2000]})


@blueprint.route("/compose/ps", methods=["POST"])
@panel_login_required
def compose_ps():
    """List containers in docker-compose project"""
    project_dir = request.form.get("path", "").strip()
    if not project_dir:
        return mw.returnData(False, "项目路径不能为空")

    result = mw.execShell(f"cd '{project_dir}' && docker-compose ps 2>&1")
    return mw.returnData(True, {"output": result[0]})


# ==================== Docker Registry ====================

@blueprint.route("/registry/list", methods=["POST"])
@panel_login_required
def registry_list():
    """List configured Docker registries"""
    configs = thisdb.getOptionByJson("docker_registries", default=[
        {"name": "Docker Hub", "url": "https://registry-1.docker.io", "default": True},
    ])
    return mw.returnData(True, {"registries": configs})


@blueprint.route("/registry/add", methods=["POST"])
@panel_login_required
def registry_add():
    """Add a Docker registry"""
    name = request.form.get("name", "").strip()
    url = request.form.get("url", "").strip()
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "").strip()

    if not name or not url:
        return mw.returnData(False, "名称和地址不能为空")

    import json
    configs = thisdb.getOptionByJson("docker_registries", default=[])
    configs.append({"name": name, "url": url, "username": username, "password": password})
    thisdb.setOption("docker_registries", json.dumps(configs))
    mw.writeLog("Docker", f"添加仓库: {name}")
    return mw.returnData(True, f"仓库[{name}]添加成功!")


@blueprint.route("/registry/login", methods=["POST"])
@panel_login_required
def registry_login():
    """Login to a Docker registry"""
    url = request.form.get("url", "").strip()
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "").strip()

    if not url:
        return mw.returnData(False, "仓库地址不能为空")

    # Sanitize inputs to prevent command injection
    url = url.replace("'", "").replace('"', '').replace(';', '').replace('`', '')
    username = username.replace("'", "").replace('"', '').replace(';', '').replace('`', '')
    # Write password to temp file to avoid shell injection via heredoc
    import tempfile
    pwd_file = None
    try:
        pwd_file = tempfile.NamedTemporaryFile(mode='w', suffix='.pwd', delete=False)
        pwd_file.write(password)
        pwd_file.close()
        result = mw.execShell(f"docker login '{url}' -u '{username}' --password-stdin < '{pwd_file.name}' 2>&1")
    finally:
        if pwd_file:
            import os
            try:
                os.unlink(pwd_file.name)
            except OSError:
                pass
    if "Login Succeeded" in result[0]:
        return mw.returnData(True, "登录成功!")
    return mw.returnData(False, f"登录失败: {result[0]}")


# ==================== Docker Terminal (容器终端) ====================

@blueprint.route("/container_exec", methods=["POST"])
@panel_login_required
def container_exec():
    """Execute a command in a container"""
    name = request.form.get("name", "").strip()
    cmd = request.form.get("cmd", "").strip()

    if not name:
        return mw.returnData(False, "容器名不能为空")
    if not cmd:
        return mw.returnData(False, "命令不能为空")

    result = _docker(f"exec {name} {cmd}")
    return mw.returnData(True, {"output": result[:5000]})
