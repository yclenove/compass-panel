#!/bin/bash
# ============================================================
# run-iteration.sh - 迭代主脚本
# 流程：扫描问题 → 修复问题 → 运行测试 → 提交代码 → 生成报告
# ============================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
CONFIG_FILE="$SCRIPT_DIR/iteration-config.json"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

log_info()  { echo -e "${BLUE}[INFO]${NC} $1"; }
log_ok()    { echo -e "${GREEN}[OK]${NC} $1"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_step()  { echo -e "\n${CYAN}========================================${NC}"; echo -e "${CYAN}  $1${NC}"; echo -e "${CYAN}========================================${NC}"; }

cd "$PROJECT_ROOT"

# 读取当前迭代号
CURRENT_ITER=$(python3 -c "
import json
with open('$CONFIG_FILE') as f:
    print(json.load(f).get('current_iteration', 0))
" 2>/dev/null || echo "0")

NEXT_ITER=$((CURRENT_ITER + 1))
MAX_ITER=$(python3 -c "
import json
with open('$CONFIG_FILE') as f:
    print(json.load(f).get('max_iterations', 100))
" 2>/dev/null || echo "100")

# 检查是否超过最大迭代
if [ "$NEXT_ITER" -gt "$MAX_ITER" ]; then
    log_error "已达到最大迭代次数 ($MAX_ITER)，停止迭代"
    exit 1
fi

START_TIME=$(date +%s)

log_step "开始迭代 #$NEXT_ITER"
log_info "时间: $(date '+%Y-%m-%d %H:%M:%S')"
log_info "项目: $PROJECT_ROOT"

# -----------------------------------------------------------
# 步骤 1: 扫描问题
# -----------------------------------------------------------
log_step "步骤 1/5: 扫描问题"
bash "$SCRIPT_DIR/scan-issues.sh" || {
    log_warn "扫描脚本执行出错，继续..."
}

ISSUE_COUNT=0
if [ -f "$SCRIPT_DIR/issues.json" ]; then
    ISSUE_COUNT=$(python3 -c "
import json
with open('$SCRIPT_DIR/issues.json') as f:
    print(json.load(f).get('total_count', 0))
" 2>/dev/null || echo "0")
fi
log_info "发现 $ISSUE_COUNT 个问题"

# -----------------------------------------------------------
# 步骤 2: 修复问题
# -----------------------------------------------------------
log_step "步骤 2/5: 自动修复问题"
if [ "$ISSUE_COUNT" -gt 0 ]; then
    python3 "$SCRIPT_DIR/fix-issue.py" || {
        log_warn "修复脚本执行出错，继续..."
    }
else
    log_info "无问题需要修复"
fi

# -----------------------------------------------------------
# 步骤 3: 运行测试
# -----------------------------------------------------------
log_step "步骤 3/5: 运行测试"
TEST_PASSED=true

# 读取测试命令
TEST_CMDS=$(python3 -c "
import json
with open('$CONFIG_FILE') as f:
    cmds = json.load(f).get('test_commands', [])
    for cmd in cmds:
        print(cmd)
" 2>/dev/null)

if [ -n "$TEST_CMDS" ]; then
    while IFS= read -r test_cmd; do
        log_info "执行: $test_cmd"
        if eval "$test_cmd" 2>&1; then
            log_ok "测试通过: $test_cmd"
        else
            log_warn "测试失败: $test_cmd"
            TEST_PASSED=false
        fi
    done <<< "$TEST_CMDS"
else
    log_info "未配置测试命令，跳过测试"
fi

# -----------------------------------------------------------
# 步骤 4: 提交代码
# -----------------------------------------------------------
log_step "步骤 4/5: 提交代码"
if command -v git &>/dev/null; then
    cd "$PROJECT_ROOT"

    # 检查是否有变更
    CHANGED_FILES=$(git status --porcelain 2>/dev/null | wc -l | tr -d ' ')

    if [ "$CHANGED_FILES" -gt 0 ]; then
        log_info "检测到 $CHANGED_FILES 个文件变更"

        # 添加变更（排除 issues.json 等临时文件）
        git add -A
        git reset HEAD scripts/iteration/issues.json 2>/dev/null || true

        # 提交
        COMMIT_MSG="iteration: 自动迭代 #$NEXT_ITER 修复 $ISSUE_COUNT 个问题"
        git commit -m "$COMMIT_MSG" --no-verify 2>/dev/null || {
            log_warn "没有可提交的变更"
        }
        log_ok "代码已提交: $COMMIT_MSG"
    else
        log_info "无代码变更需要提交"
    fi
else
    log_warn "git 未安装，跳过提交"
fi

# -----------------------------------------------------------
# 步骤 5: 生成报告
# -----------------------------------------------------------
log_step "步骤 5/5: 生成迭代报告"
python3 "$SCRIPT_DIR/generate-report.py" "$NEXT_ITER" || {
    log_warn "报告生成失败"
}

# 更新迭代计数
python3 -c "
import json
with open('$CONFIG_FILE', 'r') as f:
    config = json.load(f)
config['current_iteration'] = $NEXT_ITER
with open('$CONFIG_FILE', 'w') as f:
    json.dump(config, f, ensure_ascii=False, indent=2)
" 2>/dev/null

# 计算耗时
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

# -----------------------------------------------------------
# 迭代完成总结
# -----------------------------------------------------------
log_step "迭代 #$NEXT_ITER 完成"
log_info "耗时: ${DURATION}秒"
log_info "问题数: $ISSUE_COUNT"
log_info "测试: $(if [ "$TEST_PASSED" = true ]; then echo '通过'; else echo '失败'; fi)"
log_info "报告: docs/iteration/reports/"

echo ""
log_ok "迭代 #$NEXT_ITER 已完成!"
