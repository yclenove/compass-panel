#!/bin/bash
# ============================================================
# scan-issues.sh - 问题扫描脚本
# 扫描 flake8 问题、TODO 注释、安全问题，输出到 issues.json
# ============================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
ISSUES_FILE="$SCRIPT_DIR/issues.json"
CONFIG_FILE="$SCRIPT_DIR/iteration-config.json"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info()  { echo -e "${BLUE}[INFO]${NC} $1"; }
log_ok()    { echo -e "${GREEN}[OK]${NC} $1"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

cd "$PROJECT_ROOT"

log_info "开始扫描项目问题..."

# 初始化 issues 数组
ISSUES="[]"
TOTAL_COUNT=0

# -----------------------------------------------------------
# 1. flake8 扫描
# -----------------------------------------------------------
scan_flake8() {
    log_info "运行 flake8 检查..."
    if ! command -v flake8 &>/dev/null; then
        log_warn "flake8 未安装，跳过"
        return
    fi

    local tmpfile
    tmpfile=$(mktemp)
    flake8 web/ --count --statistics --format=json 2>/dev/null > "$tmpfile" || true

    if [ -s "$tmpfile" ]; then
        local count
        count=$(python3 -c "
import json, sys
try:
    data = json.load(open('$tmpfile'))
    print(len(data) if isinstance(data, list) else 0)
except:
    print(0)
" 2>/dev/null || echo "0")

        if [ "$count" -gt 0 ]; then
            # 转换为标准格式
            python3 -c "
import json, sys
try:
    data = json.load(open('$tmpfile'))
    issues = []
    if isinstance(data, list):
        for item in data[:200]:  # 限制最多200条
            issues.append({
                'source': 'flake8',
                'type': 'tech_debt',
                'priority': 2,
                'file': item.get('filename', ''),
                'line': item.get('line_number', 0),
                'column': item.get('column_number', 0),
                'code': item.get('code', ''),
                'message': item.get('text', ''),
                'fixable': item.get('code', '') in [
                    'E301', 'E302', 'E303', 'E304',
                    'W291', 'W292', 'W293', 'W391',
                    'E711', 'E712', 'E721',
                    'E501'
                ]
            })
    print(json.dumps(issues, ensure_ascii=False))
except Exception as e:
    print('[]')
" >> "$tmpfile.issues" 2>/dev/null || echo "[]" > "$tmpfile.issues"

            local new_issues
            new_issues=$(cat "$tmpfile.issues")
            ISSUES=$(python3 -c "
import json
existing = json.loads('''$ISSUES''')
new = json.loads('''$new_issues''')
print(json.dumps(existing + new, ensure_ascii=False))
" 2>/dev/null || echo "$ISSUES")
            TOTAL_COUNT=$((TOTAL_COUNT + count))
            log_ok "flake8: 发现 $count 个问题"
        else
            log_ok "flake8: 无问题"
        fi
    else
        log_ok "flake8: 无问题"
    fi

    rm -f "$tmpfile" "$tmpfile.issues"
}

# -----------------------------------------------------------
# 2. TODO/FIXME 注释扫描
# -----------------------------------------------------------
scan_todos() {
    log_info "扫描 TODO/FIXME 注释..."
    local tmpfile
    tmpfile=$(mktemp)

    grep -rn 'TODO\|FIXME\|HACK\|XXX' web/ \
        --include='*.py' --include='*.js' --include='*.vue' \
        2>/dev/null > "$tmpfile" || true

    local count
    count=$(wc -l < "$tmpfile" | tr -d ' ')

    if [ "$count" -gt 0 ]; then
        python3 -c "
import json, re, sys

issues = []
with open('$tmpfile') as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        m = re.match(r'^(.+?):(\d+):(.*)$', line)
        if m:
            filepath, lineno, content = m.groups()
            tag = 'TODO'
            for t in ['FIXME', 'HACK', 'XXX', 'TODO']:
                if t in content:
                    tag = t
                    break
            issues.append({
                'source': 'todo_comments',
                'type': 'tech_debt',
                'priority': 3 if tag == 'TODO' else 2,
                'file': filepath,
                'line': int(lineno),
                'column': 0,
                'code': tag,
                'message': content.strip(),
                'fixable': False
            })

print(json.dumps(issues[:200], ensure_ascii=False))
" >> "$tmpfile.issues" 2>/dev/null || echo "[]" > "$tmpfile.issues"

        local new_issues
        new_issues=$(cat "$tmpfile.issues")
        ISSUES=$(python3 -c "
import json
existing = json.loads('''$ISSUES''')
new = json.loads('''$new_issues''')
print(json.dumps(existing + new, ensure_ascii=False))
" 2>/dev/null || echo "$ISSUES")
        TOTAL_COUNT=$((TOTAL_COUNT + count))
        log_ok "TODO/FIXME: 发现 $count 个注释"
    else
        log_ok "TODO/FIXME: 无待办注释"
    fi

    rm -f "$tmpfile" "$tmpfile.issues"
}

# -----------------------------------------------------------
# 3. 安全问题扫描（简易）
# -----------------------------------------------------------
scan_security() {
    log_info "扫描常见安全问题..."
    local tmpfile
    tmpfile=$(mktemp)

    # 检查硬编码密码、eval、exec 等
    grep -rn 'password\s*=\s*["\x27][^"\x27]*["\x27]\|eval(\|exec(\|os\.system(' web/ \
        --include='*.py' --include='*.js' --include='*.vue' \
        2>/dev/null | grep -v 'test_\|_test\.\|example\|sample' \
        > "$tmpfile" || true

    local count
    count=$(wc -l < "$tmpfile" | tr -d ' ')

    if [ "$count" -gt 0 ]; then
        python3 -c "
import json, re

issues = []
with open('$tmpfile') as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        m = re.match(r'^(.+?):(\d+):(.*)$', line)
        if m:
            filepath, lineno, content = m.groups()
            code = 'SEC-OTHER'
            if 'password' in content.lower():
                code = 'SEC-HARDCODED-PWD'
            elif 'eval(' in content:
                code = 'SEC-EVAL'
            elif 'exec(' in content:
                code = 'SEC-EXEC'
            elif 'os.system(' in content:
                code = 'SEC-OS-SYSTEM'
            issues.append({
                'source': 'security_scan',
                'type': 'security',
                'priority': 1,
                'file': filepath,
                'line': int(lineno),
                'column': 0,
                'code': code,
                'message': content.strip()[:200],
                'fixable': False
            })

print(json.dumps(issues[:100], ensure_ascii=False))
" >> "$tmpfile.issues" 2>/dev/null || echo "[]" > "$tmpfile.issues"

        local new_issues
        new_issues=$(cat "$tmpfile.issues")
        ISSUES=$(python3 -c "
import json
existing = json.loads('''$ISSUES''')
new = json.loads('''$new_issues''')
print(json.dumps(existing + new, ensure_ascii=False))
" 2>/dev/null || echo "$ISSUES")
        TOTAL_COUNT=$((TOTAL_COUNT + count))
        log_warn "安全扫描: 发现 $count 个潜在问题"
    else
        log_ok "安全扫描: 无明显问题"
    fi

    rm -f "$tmpfile" "$tmpfile.issues"
}

# -----------------------------------------------------------
# 执行扫描
# -----------------------------------------------------------
scan_flake8
scan_todos
scan_security

# -----------------------------------------------------------
# 写入结果
# -----------------------------------------------------------
python3 -c "
import json, datetime

issues = json.loads('''$ISSUES''')

# 按优先级排序
issues.sort(key=lambda x: (x.get('priority', 99), x.get('file', '')))

result = {
    'scan_time': datetime.datetime.now().isoformat(),
    'total_count': len(issues),
    'by_source': {},
    'by_type': {},
    'fixable_count': sum(1 for i in issues if i.get('fixable')),
    'issues': issues
}

for issue in issues:
    src = issue.get('source', 'unknown')
    result['by_source'][src] = result['by_source'].get(src, 0) + 1
    typ = issue.get('type', 'unknown')
    result['by_type'][typ] = result['by_type'].get(typ, 0) + 1

with open('$ISSUES_FILE', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
" 2>/dev/null

log_info "======================================"
log_info "扫描完成"
log_info "总问题数: $TOTAL_COUNT"
log_info "结果文件: $ISSUES_FILE"
log_info "======================================"
