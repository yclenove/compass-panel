#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fix-issue.py - 问题自动修复脚本
根据问题类型自动修复代码问题。
支持修复 flake8 的 E302（空行）、E501（行太长）、W291/W293（空格）等问题。
"""

import json
import os
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent.parent
ISSUES_FILE = SCRIPT_DIR / "issues.json"
CONFIG_FILE = SCRIPT_DIR / "iteration-config.json"


def load_issues():
    """加载问题列表"""
    if not ISSUES_FILE.exists():
        print("[ERROR] issues.json 不存在，请先运行 scan-issues.sh")
        sys.exit(1)
    with open(ISSUES_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("issues", [])


def load_config():
    """加载配置"""
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def fix_e301(filepath, line_num):
    """修复 E301: expected 1 blank line before a nested definition"""
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()
    idx = line_num - 1
    if idx > 0 and lines[idx - 1].strip() != "":
        lines.insert(idx, "\n")
        with open(filepath, "w", encoding="utf-8") as f:
            f.writelines(lines)
        return True
    return False


def fix_e302(filepath, line_num):
    """修复 E302: expected 2 blank lines before a function or class definition"""
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()
    idx = line_num - 1
    # 向上数已有空行数
    blank_count = 0
    check = idx - 1
    while check >= 0 and lines[check].strip() == "":
        blank_count += 1
        check -= 1

    needed = 2 - blank_count
    if needed > 0:
        for _ in range(needed):
            lines.insert(idx, "\n")
        with open(filepath, "w", encoding="utf-8") as f:
            f.writelines(lines)
        return True
    return False


def fix_e303(filepath, line_num):
    """修复 E303: too many blank lines"""
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()
    idx = line_num - 1
    # 从当前行向上删除多余空行，保留最多2个
    blank_start = idx
    while blank_start > 0 and lines[blank_start - 1].strip() == "":
        blank_start -= 1

    blanks = idx - blank_start
    if blanks > 2:
        excess = blanks - 2
        del lines[blank_start:blank_start + excess]
        with open(filepath, "w", encoding="utf-8") as f:
            f.writelines(lines)
        return True
    return False


def fix_w291(filepath, line_num):
    """修复 W291: trailing whitespace"""
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()
    idx = line_num - 1
    if idx < len(lines) and lines[idx].rstrip() != lines[idx].rstrip("\n"):
        # 有尾随空格
        lines[idx] = lines[idx].rstrip() + "\n"
        with open(filepath, "w", encoding="utf-8") as f:
            f.writelines(lines)
        return True
    elif idx < len(lines) and lines[idx] != lines[idx].rstrip():
        lines[idx] = lines[idx].rstrip() + "\n"
        with open(filepath, "w", encoding="utf-8") as f:
            f.writelines(lines)
        return True
    return False


def fix_w293(filepath, line_num):
    """修复 W293: whitespace before ':'"""
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()
    idx = line_num - 1
    if idx < len(lines):
        # 删除行首冒号前的空格
        line = lines[idx]
        if re.match(r'^\s+\S', line):
            # 只去除行内多余空格，保留缩进
            pass
        lines[idx] = line.rstrip() + "\n"
        with open(filepath, "w", encoding="utf-8") as f:
            f.writelines(lines)
        return True
    return False


def fix_w292(filepath, line_num):
    """修复 W292: no newline at end of file"""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    if content and not content.endswith("\n"):
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content + "\n")
        return True
    return False


def fix_w391(filepath, line_num):
    """修复 W391: blank line at end of file"""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    if content.endswith("\n\n"):
        content = content.rstrip("\n") + "\n"
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    return False


def fix_e501(filepath, line_num):
    """修复 E501: line too long (>120 chars) - 尝试在合理位置换行"""
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()
    idx = line_num - 1
    if idx >= len(lines):
        return False

    line = lines[idx]
    max_len = 120
    if len(line.rstrip()) <= max_len:
        return False

    indent = len(line) - len(line.lstrip())
    indent_str = line[:indent]
    content = line.lstrip()

    # Python: 尝试在逗号后换行
    if content.endswith(")") or content.endswith("],") or content.endswith("},"):
        # 在倒数第二个参数的逗号后换行
        for i in range(len(content) - 2, indent, -1):
            if content[i] == "," and i + 1 < len(content):
                new_line = content[:i + 1] + "\n" + indent_str + "    " + content[i + 1:]
                if len(indent_str + "    " + content[i + 1:].lstrip()) <= max_len:
                    lines[idx] = new_line
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.writelines(lines)
                    return True
                break

    # 尝试在字符串拼接处换行
    for sep in [" + ", " and ", " or ", " in ", " not "]:
        pos = content.rfind(sep, indent, max_len)
        if pos > indent:
            new_line = content[:pos + len(sep)].rstrip() + "\n" + indent_str + "    " + content[pos + len(sep):]
            lines[idx] = new_line
            with open(filepath, "w", encoding="utf-8") as f:
                f.writelines(lines)
            return True

    return False


def fix_e711(filepath, line_num):
    """修复 E711: comparison to None (use 'is' / 'is not')"""
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()
    idx = line_num - 1
    if idx >= len(lines):
        return False

    line = lines[idx]
    original = line
    line = re.sub(r'(\w+)\s*==\s*None', r'\1 is None', line)
    line = re.sub(r'(\w+)\s*!=\s*None', r'\1 is not None', line)

    if line != original:
        lines[idx] = line
        with open(filepath, "w", encoding="utf-8") as f:
            f.writelines(lines)
        return True
    return False


def fix_e712(filepath, line_num):
    """修复 E712: comparison to True/False"""
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()
    idx = line_num - 1
    if idx >= len(lines):
        return False

    line = lines[idx]
    original = line
    line = re.sub(r'(\w+)\s*==\s*True', r'\1 is True', line)
    line = re.sub(r'(\w+)\s*!=\s*True', r'\1 is not True', line)
    line = re.sub(r'(\w+)\s*==\s*False', r'\1 is False', line)
    line = re.sub(r'(\w+)\s*!=\s*False', r'\1 is not False', line)

    if line != original:
        lines[idx] = line
        with open(filepath, "w", encoding="utf-8") as f:
            f.writelines(lines)
        return True
    return False


# 修复函数映射表
FIX_MAP = {
    "E301": fix_e301,
    "E302": fix_e302,
    "E303": fix_e303,
    "E501": fix_e501,
    "E711": fix_e711,
    "E712": fix_e712,
    "W291": fix_w291,
    "W292": fix_w292,
    "W293": fix_w293,
    "W391": fix_w391,
}


def fix_issue(issue):
    """修复单个问题"""
    code = issue.get("code", "")
    filepath = issue.get("file", "")
    line_num = issue.get("line", 0)

    if not filepath or not os.path.isabs(filepath):
        filepath = str(PROJECT_ROOT / filepath)

    if not os.path.exists(filepath):
        return False, f"文件不存在: {filepath}"

    fix_func = FIX_MAP.get(code)
    if fix_func:
        try:
            result = fix_func(filepath, line_num)
            return result, f"已修复 {code}" if result else f"跳过 {code} (无需修复或无法自动修复)"
        except Exception as e:
            return False, f"修复 {code} 失败: {str(e)}"
    else:
        return False, f"不支持自动修复: {code}"


def main():
    """主函数"""
    print("=" * 60)
    print("  自动问题修复工具")
    print("=" * 60)

    issues = load_issues()

    # 只处理可修复的问题
    fixable = [i for i in issues if i.get("fixable")]
    print(f"\n总问题数: {len(issues)}")
    print(f"可修复数: {len(fixable)}")

    if not fixable:
        print("\n没有可自动修复的问题。")
        return

    # 按文件和行号排序
    fixable.sort(key=lambda x: (x.get("file", ""), x.get("line", 0)))

    fixed_count = 0
    skipped_count = 0
    failed_count = 0

    # 按文件分组，每个文件从后向前修复（避免行号偏移）
    files_issues = {}
    for issue in fixable:
        f = issue.get("file", "")
        if f not in files_issues:
            files_issues[f] = []
        files_issues[f].append(issue)

    for filepath, file_issues in files_issues.items():
        # 按行号降序排列
        file_issues.sort(key=lambda x: x.get("line", 0), reverse=True)
        for issue in file_issues:
            success, msg = fix_issue(issue)
            if success:
                fixed_count += 1
                print(f"  [FIXED] {issue['file']}:{issue['line']} - {issue['code']}")
            elif "不支持" in msg or "不存在" in msg:
                failed_count += 1
                print(f"  [FAIL]  {issue['file']}:{issue['line']} - {msg}")
            else:
                skipped_count += 1
                print(f"  [SKIP]  {issue['file']}:{issue['line']} - {msg}")

    print(f"\n{'=' * 60}")
    print(f"  修复完成: {fixed_count} 已修复, {skipped_count} 跳过, {failed_count} 失败")
    print(f"{'=' * 60}")

    # 更新 issues.json 标记已修复
    if fixed_count > 0:
        remaining = [i for i in issues if not i.get("_fixed")]
        data = {}
        if ISSUES_FILE.exists():
            with open(ISSUES_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        data["remaining_after_fix"] = len(remaining)
        data["last_fix_count"] = fixed_count
        with open(ISSUES_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
