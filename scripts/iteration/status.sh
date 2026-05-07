#!/bin/bash
# ============================================================
# status.sh - 迭代状态查看脚本
# 显示当前迭代进度、问题状态、报告数量
# ============================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
CONFIG_FILE="$SCRIPT_DIR/iteration-config.json"
ISSUES_FILE="$SCRIPT_DIR/issues.json"
REPORT_DIR="$PROJECT_ROOT/docs/iteration/reports"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

echo -e ""
echo -e "${CYAN}${BOLD}╔══════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}${BOLD}║          自动迭代框架 - 状态总览                ║${NC}"
echo -e "${CYAN}${BOLD}╚══════════════════════════════════════════════════╝${NC}"
echo -e ""

# -----------------------------------------------------------
# 配置信息
# -----------------------------------------------------------
if [ -f "$CONFIG_FILE" ]; then
    CURRENT_ITER=$(python3 -c "
import json
with open('$CONFIG_FILE') as f:
    c = json.load(f)
    print(c.get('current_iteration', 0))
" 2>/dev/null || echo "0")

    MAX_ITER=$(python3 -c "
import json
with open('$CONFIG_FILE') as f:
    print(json.load(f).get('max_iterations', 100))
" 2>/dev/null || echo "100")

    VERSION=$(python3 -c "
import json
with open('$CONFIG_FILE') as f:
    print(json.load(f).get('version', 'N/A'))
" 2>/dev/null || echo "N/A")

    echo -e "${BOLD}迭代配置${NC}"
    echo -e "  版本:        ${GREEN}$VERSION${NC}"
    echo -e "  当前迭代:    ${GREEN}#$CURRENT_ITER${NC} / $MAX_ITER"
    echo -e "  剩余迭代:    $((MAX_ITER - CURRENT_ITER))"

    # 进度条
    if [ "$MAX_ITER" -gt 0 ]; then
        PROGRESS=$((CURRENT_ITER * 100 / MAX_ITER))
        FILLED=$((PROGRESS / 5))
        EMPTY=$((20 - FILLED))
        BAR=$(printf "%${FILLED}s" | tr ' ' '█')$(printf "%${EMPTY}s" | tr ' ' '░')
        echo -e "  进度:        [${GREEN}${BAR}${NC}] ${PROGRESS}%"
    fi
    echo -e ""
else
    echo -e "${RED}  配置文件不存在: $CONFIG_FILE${NC}"
    echo -e "  请先运行: bash scripts/iterate.sh init"
    echo -e ""
fi

# -----------------------------------------------------------
# 问题状态
# -----------------------------------------------------------
echo -e "${BOLD}问题状态${NC}"
if [ -f "$ISSUES_FILE" ]; then
    TOTAL=$(python3 -c "
import json
with open('$ISSUES_FILE') as f:
    print(json.load(f).get('total_count', 0))
" 2>/dev/null || echo "0")

    FIXABLE=$(python3 -c "
import json
with open('$ISSUES_FILE') as f:
    print(json.load(f).get('fixable_count', 0))
" 2>/dev/null || echo "0")

    SCAN_TIME=$(python3 -c "
import json
with open('$ISSUES_FILE') as f:
    print(json.load(f).get('scan_time', 'N/A'))
" 2>/dev/null || echo "N/A")

    BY_SOURCE=$(python3 -c "
import json
with open('$ISSUES_FILE') as f:
    data = json.load(f)
    for src, cnt in data.get('by_source', {}).items():
        print(f'    {src}: {cnt}')
" 2>/dev/null || echo "    无数据")

    BY_TYPE=$(python3 -c "
import json
with open('$ISSUES_FILE') as f:
    data = json.load(f)
    for typ, cnt in data.get('by_type', {}).items():
        print(f'    {typ}: {cnt}')
" 2>/dev/null || echo "    无数据")

    echo -e "  总问题数:    ${YELLOW}$TOTAL${NC}"
    echo -e "  可修复数:    ${GREEN}$FIXABLE${NC}"
    echo -e "  扫描时间:    $SCAN_TIME"
    echo -e ""
    echo -e "  ${BOLD}按来源:${NC}"
    echo -e "$BY_SOURCE"
    echo -e ""
    echo -e "  ${BOLD}按类型:${NC}"
    echo -e "$BY_TYPE"
else
    echo -e "  ${YELLOW}尚未运行扫描${NC}"
    echo -e "  运行: bash scripts/iterate.sh scan"
fi
echo -e ""

# -----------------------------------------------------------
# 报告统计
# -----------------------------------------------------------
echo -e "${BOLD}迭代报告${NC}"
if [ -d "$REPORT_DIR" ]; then
    REPORT_COUNT=$(ls -1 "$REPORT_DIR"/*.md 2>/dev/null | wc -l | tr -d ' ')
    echo -e "  报告数量:    ${GREEN}$REPORT_COUNT${NC}"

    if [ "$REPORT_COUNT" -gt 0 ]; then
        LATEST=$(ls -1t "$REPORT_DIR"/*.md 2>/dev/null | head -1)
        LATEST_NAME=$(basename "$LATEST" 2>/dev/null || echo "N/A")
        echo -e "  最新报告:    $LATEST_NAME"
        echo -e "  报告目录:    docs/iteration/reports/"
    fi
else
    echo -e "  ${YELLOW}报告目录不存在${NC}"
fi
echo -e ""

# -----------------------------------------------------------
# Git 状态
# -----------------------------------------------------------
echo -e "${BOLD}Git 状态${NC}"
if command -v git &>/dev/null; then
    BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "N/A")
    COMMIT=$(git rev-parse --short HEAD 2>/dev/null || echo "N/A")
    CHANGES=$(git status --porcelain 2>/dev/null | wc -l | tr -d ' ')

    echo -e "  当前分支:    ${GREEN}$BRANCH${NC}"
    echo -e "  最新提交:    $COMMIT"
    echo -e "  未提交变更:  ${YELLOW}$CHANGES${NC} 个文件"
else
    echo -e "  ${RED}git 未安装${NC}"
fi
echo -e ""

# -----------------------------------------------------------
# 快捷命令提示
# -----------------------------------------------------------
echo -e "${CYAN}${BOLD}══════════════════════════════════════════════════${NC}"
echo -e "${BOLD}可用命令:${NC}"
echo -e "  bash scripts/iterate.sh run     - 执行一次迭代"
echo -e "  bash scripts/iterate.sh scan    - 仅扫描问题"
echo -e "  bash scripts/iterate.sh fix     - 仅修复问题"
echo -e "  bash scripts/iterate.sh report  - 仅生成报告"
echo -e "  bash scripts/iterate.sh status  - 查看状态"
echo -e "  bash scripts/iterate.sh help    - 帮助信息"
echo -e ""
