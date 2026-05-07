#!/bin/bash
# ============================================================
# iterate.sh - 迭代主控脚本
# 支持命令：init, run, status, report, scan, fix, help
# ============================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ITER_DIR="$SCRIPT_DIR/iteration"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

show_help() {
    echo -e ""
    echo -e "${CYAN}${BOLD}╔══════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}${BOLD}║          自动迭代框架 - 命令帮助                ║${NC}"
    echo -e "${CYAN}${BOLD}╚══════════════════════════════════════════════════╝${NC}"
    echo -e ""
    echo -e "${BOLD}用法:${NC}"
    echo -e "  bash scripts/iterate.sh <命令>"
    echo -e ""
    echo -e "${BOLD}可用命令:${NC}"
    echo -e ""
    echo -e "  ${GREEN}init${NC}      初始化迭代环境"
    echo -e "              创建必要目录、检查依赖、设置权限"
    echo -e ""
    echo -e "  ${GREEN}run${NC}       执行一次完整迭代"
    echo -e "              流程: 扫描 → 修复 → 测试 → 提交 → 报告"
    echo -e ""
    echo -e "  ${GREEN}status${NC}    查看迭代状态"
    echo -e "              显示当前进度、问题统计、报告数量"
    echo -e ""
    echo -e "  ${GREEN}report${NC}    生成迭代报告"
    echo -e "              基于当前扫描结果生成 Markdown 报告"
    echo -e ""
    echo -e "  ${GREEN}scan${NC}      扫描项目问题"
    echo -e "              运行 flake8、TODO 注释、安全检查"
    echo -e ""
    echo -e "  ${GREEN}fix${NC}       自动修复问题"
    echo -e "              修复 flake8 空行、行长度、空格等问题"
    echo -e ""
    echo -e "  ${GREEN}help${NC}      显示此帮助信息"
    echo -e ""
    echo -e "${BOLD}示例:${NC}"
    echo -e "  bash scripts/iterate.sh init     # 首次使用，初始化环境"
    echo -e "  bash scripts/iterate.sh run      # 执行一轮迭代"
    echo -e "  bash scripts/iterate.sh scan     # 仅查看问题"
    echo -e "  bash scripts/iterate.sh fix      # 仅修复问题"
    echo -e "  bash scripts/iterate.sh status   # 查看当前状态"
    echo -e ""
    echo -e "${BOLD}配置文件:${NC}"
    echo -e "  scripts/iteration/iteration-config.json"
    echo -e ""
    echo -e "${BOLD}输出目录:${NC}"
    echo -e "  docs/iteration/reports/          (迭代报告)"
    echo -e "  scripts/iteration/issues.json    (问题清单)"
    echo -e ""
    echo -e "${BOLD}迭代流程:${NC}"
    echo -e "  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐"
    echo -e "  │  扫描   │───▶│  修复   │───▶│  测试   │───▶│  提交   │───▶│  报告   │"
    echo -e "  └─────────┘    └─────────┘    └─────────┘    └─────────┘    └─────────┘"
    echo -e ""
}

# 检查子脚本是否存在
check_scripts() {
    local missing=0
    for script in scan-issues.sh fix-issue.py generate-report.py run-iteration.sh status.sh init.sh; do
        if [ ! -f "$ITER_DIR/$script" ]; then
            echo -e "${RED}[ERROR]${NC} 缺少脚本: $ITER_DIR/$script"
            missing=1
        fi
    done
    if [ "$missing" -eq 1 ]; then
        echo -e "${RED}[ERROR]${NC} 脚本文件不完整，请检查 scripts/iteration/ 目录"
        exit 1
    fi
}

# 主入口
case "${1:-help}" in
    init)
        echo -e "${BLUE}[INIT]${NC} 初始化迭代环境..."
        check_scripts
        bash "$ITER_DIR/init.sh"
        ;;
    run)
        echo -e "${BLUE}[RUN]${NC} 执行迭代..."
        check_scripts
        bash "$ITER_DIR/run-iteration.sh"
        ;;
    status)
        check_scripts
        bash "$ITER_DIR/status.sh"
        ;;
    report)
        echo -e "${BLUE}[REPORT]${NC} 生成迭代报告..."
        check_scripts
        python3 "$ITER_DIR/generate-report.py"
        ;;
    scan)
        echo -e "${BLUE}[SCAN]${NC} 扫描项目问题..."
        check_scripts
        bash "$ITER_DIR/scan-issues.sh"
        ;;
    fix)
        echo -e "${BLUE}[FIX]${NC} 自动修复问题..."
        check_scripts
        python3 "$ITER_DIR/fix-issue.py"
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo -e "${RED}[ERROR]${NC} 未知命令: $1"
        echo ""
        show_help
        exit 1
        ;;
esac
