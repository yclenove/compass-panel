#!/bin/bash
# ============================================================
# init.sh - 迭代环境初始化脚本
# 创建必要目录和文件
# ============================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
CONFIG_FILE="$SCRIPT_DIR/iteration-config.json"
REPORT_DIR="$PROJECT_ROOT/docs/iteration/reports"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info()  { echo -e "${BLUE}[INFO]${NC} $1"; }
log_ok()    { echo -e "${GREEN}[OK]${NC} $1"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }

cd "$PROJECT_ROOT"

log_info "初始化自动迭代框架..."
log_info "项目根目录: $PROJECT_ROOT"

# -----------------------------------------------------------
# 创建目录结构
# -----------------------------------------------------------
log_info "创建目录结构..."

mkdir -p "$SCRIPT_DIR"
mkdir -p "$REPORT_DIR"
mkdir -p "$PROJECT_ROOT/docs/iteration"

log_ok "目录结构已创建"
echo "  scripts/iteration/"
echo "  docs/iteration/"
echo "  docs/iteration/reports/"

# -----------------------------------------------------------
# 检查配置文件
# -----------------------------------------------------------
if [ -f "$CONFIG_FILE" ]; then
    log_ok "配置文件已存在: $CONFIG_FILE"
else
    log_warn "配置文件不存在: $CONFIG_FILE"
    log_warn "请确保 iteration-config.json 已正确创建"
fi

# -----------------------------------------------------------
# 检查依赖
# -----------------------------------------------------------
log_info "检查依赖..."

# Python3
if command -v python3 &>/dev/null; then
    PY_VERSION=$(python3 --version 2>&1)
    log_ok "Python3: $PY_VERSION"
else
    log_warn "Python3 未安装 - 部分功能将不可用"
fi

# flake8
if command -v flake8 &>/dev/null; then
    FLAKE8_VERSION=$(flake8 --version 2>&1 | head -1)
    log_ok "flake8: $FLAKE8_VERSION"
else
    log_warn "flake8 未安装 - 代码质量扫描将跳过"
    log_info "安装: pip install flake8"
fi

# git
if command -v git &>/dev/null; then
    GIT_VERSION=$(git --version 2>&1)
    log_ok "Git: $GIT_VERSION"
else
    log_warn "Git 未安装 - 代码提交功能将不可用"
fi

# pytest
if command -v pytest &>/dev/null || python3 -m pytest --version &>/dev/null 2>&1; then
    log_ok "pytest: 已安装"
else
    log_warn "pytest 未安装 - 测试功能将跳过"
    log_info "安装: pip install pytest"
fi

# -----------------------------------------------------------
# 设置脚本可执行权限
# -----------------------------------------------------------
log_info "设置脚本权限..."
chmod +x "$SCRIPT_DIR/scan-issues.sh" 2>/dev/null || true
chmod +x "$SCRIPT_DIR/run-iteration.sh" 2>/dev/null || true
chmod +x "$SCRIPT_DIR/status.sh" 2>/dev/null || true
chmod +x "$SCRIPT_DIR/init.sh" 2>/dev/null || true
chmod +x "$PROJECT_ROOT/scripts/iterate.sh" 2>/dev/null || true

log_ok "脚本权限已设置"

# -----------------------------------------------------------
# 创建 .gitignore 条目提示
# -----------------------------------------------------------
GITIGNORE="$PROJECT_ROOT/.gitignore"
if [ -f "$GITIGNORE" ]; then
    if ! grep -q "scripts/iteration/issues.json" "$GITIGNORE" 2>/dev/null; then
        log_info "建议在 .gitignore 中添加:"
        echo "  scripts/iteration/issues.json"
    fi
fi

# -----------------------------------------------------------
# 初始化完成
# -----------------------------------------------------------
echo ""
echo -e "${GREEN}======================================${NC}"
echo -e "${GREEN}  自动迭代框架初始化完成!${NC}"
echo -e "${GREEN}======================================${NC}"
echo ""
echo "目录结构:"
echo "  scripts/iteration/"
echo "    ├── iteration-config.json  (配置文件)"
echo "    ├── scan-issues.sh         (问题扫描)"
echo "    ├── fix-issue.py           (问题修复)"
echo "    ├── generate-report.py     (报告生成)"
echo "    ├── run-iteration.sh       (迭代主脚本)"
echo "    ├── status.sh              (状态查看)"
echo "    └── init.sh                (初始化)"
echo "  scripts/iterate.sh           (主控脚本)"
echo "  docs/iteration/"
echo "    ├── README.md              (文档)"
echo "    └── reports/               (迭代报告)"
echo ""
echo "快速开始:"
echo "  bash scripts/iterate.sh run     # 执行一次迭代"
echo "  bash scripts/iterate.sh status  # 查看状态"
echo "  bash scripts/iterate.sh help    # 查看帮助"
echo ""
