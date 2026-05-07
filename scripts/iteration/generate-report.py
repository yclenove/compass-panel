#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate-report.py - 迭代报告生成脚本
生成 markdown 格式的迭代报告到 docs/iteration/reports/ 目录。
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent.parent
CONFIG_FILE = SCRIPT_DIR / "iteration-config.json"
ISSUES_FILE = SCRIPT_DIR / "issues.json"
REPORT_DIR = PROJECT_ROOT / "docs" / "iteration" / "reports"


def load_config():
    """加载配置"""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"current_iteration": 0, "version": "1.0.0"}


def save_config(config):
    """保存配置"""
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


def load_issues():
    """加载问题数据"""
    if ISSUES_FILE.exists():
        with open(ISSUES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"total_count": 0, "issues": [], "by_source": {}, "by_type": {}, "fixable_count": 0}


def get_git_info():
    """获取 git 信息"""
    info = {}
    try:
        info["commit"] = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=PROJECT_ROOT, text=True, stderr=subprocess.DEVNULL
        ).strip()
        info["branch"] = subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=PROJECT_ROOT, text=True, stderr=subprocess.DEVNULL
        ).strip()
        info["commit_msg"] = subprocess.check_output(
            ["git", "log", "-1", "--pretty=%s"],
            cwd=PROJECT_ROOT, text=True, stderr=subprocess.DEVNULL
        ).strip()
        # 最近修改的文件数
        diff_output = subprocess.check_output(
            ["git", "diff", "--stat", "HEAD~1", "HEAD"],
            cwd=PROJECT_ROOT, text=True, stderr=subprocess.DEVNULL
        ).strip()
        info["diff_stat"] = diff_output if diff_output else "无变更"
    except Exception:
        info["commit"] = "N/A"
        info["branch"] = "N/A"
        info["commit_msg"] = "N/A"
        info["diff_stat"] = "N/A"
    return info


def get_project_stats():
    """获取项目统计"""
    stats = {}
    try:
        # Python 文件数
        result = subprocess.run(
            ["find", str(PROJECT_ROOT / "web"), "-name", "*.py", "-type", "f"],
            capture_output=True, text=True, timeout=10
        )
        stats["py_files"] = len(result.stdout.strip().split("\n")) if result.stdout.strip() else 0
    except Exception:
        stats["py_files"] = "N/A"

    try:
        # JS/Vue 文件数
        result = subprocess.run(
            ["find", str(PROJECT_ROOT / "web"), "-name", "*.js", "-o", "-name", "*.vue", "-type", "f"],
            capture_output=True, text=True, timeout=10
        )
        stats["js_files"] = len(result.stdout.strip().split("\n")) if result.stdout.strip() else 0
    except Exception:
        stats["js_files"] = "N/A"

    return stats


def generate_report(iteration_num):
    """生成迭代报告"""
    config = load_config()
    issues_data = load_issues()
    git_info = get_git_info()
    project_stats = get_project_stats()

    now = datetime.now()
    timestamp = now.strftime("%Y%m%d_%H%M%S")
    report_filename = f"iteration_{iteration_num:03d}_{timestamp}.md"
    report_path = REPORT_DIR / report_filename

    # 确保报告目录存在
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    # 构建报告内容
    lines = []
    lines.append(f"# 迭代报告 #{iteration_num}")
    lines.append("")
    lines.append(f"**生成时间**: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"**迭代版本**: {config.get('version', 'N/A')}")
    lines.append(f"**Git 分支**: {git_info.get('branch', 'N/A')}")
    lines.append(f"**提交哈希**: {git_info.get('commit', 'N/A')}")
    lines.append(f"**最新提交**: {git_info.get('commit_msg', 'N/A')}")
    lines.append("")

    # 问题统计
    lines.append("## 问题扫描统计")
    lines.append("")
    lines.append(f"| 指标 | 数值 |")
    lines.append(f"|------|------|")
    lines.append(f"| 总问题数 | {issues_data.get('total_count', 0)} |")
    lines.append(f"| 可修复数 | {issues_data.get('fixable_count', 0)} |")
    lines.append("")

    # 按来源统计
    by_source = issues_data.get("by_source", {})
    if by_source:
        lines.append("### 按来源分布")
        lines.append("")
        lines.append("| 来源 | 数量 |")
        lines.append("|------|------|")
        for source, count in sorted(by_source.items()):
            lines.append(f"| {source} | {count} |")
        lines.append("")

    # 按类型统计
    by_type = issues_data.get("by_type", {})
    if by_type:
        lines.append("### 按类型分布")
        lines.append("")
        lines.append("| 类型 | 数量 |")
        lines.append("|------|------|")
        for typ, count in sorted(by_type.items()):
            lines.append(f"| {typ} | {count} |")
        lines.append("")

    # 问题详情（Top 20）
    issues = issues_data.get("issues", [])
    if issues:
        lines.append("## 问题详情 (Top 20)")
        lines.append("")
        lines.append("| # | 文件 | 行号 | 代码 | 可修复 | 描述 |")
        lines.append("|---|------|------|------|--------|------|")
        for i, issue in enumerate(issues[:20], 1):
            filepath = os.path.relpath(issue.get("file", ""), PROJECT_ROOT) if issue.get("file") else "N/A"
            line = issue.get("line", "N/A")
            code = issue.get("code", "N/A")
            fixable = "是" if issue.get("fixable") else "否"
            msg = issue.get("message", "")[:80]
            lines.append(f"| {i} | `{filepath}` | {line} | {code} | {fixable} | {msg} |")
        lines.append("")

    # 项目统计
    lines.append("## 项目统计")
    lines.append("")
    lines.append(f"| 指标 | 数值 |")
    lines.append(f"|------|------|")
    lines.append(f"| Python 文件数 | {project_stats.get('py_files', 'N/A')} |")
    lines.append(f"| JS/Vue 文件数 | {project_stats.get('js_files', 'N/A')} |")
    lines.append("")

    # Git 变更
    lines.append("## 最近变更")
    lines.append("")
    lines.append("```")
    lines.append(git_info.get("diff_stat", "无变更"))
    lines.append("```")
    lines.append("")

    # 下一步建议
    lines.append("## 下一步建议")
    lines.append("")
    if issues_data.get("total_count", 0) > 0:
        fixable_count = issues_data.get("fixable_count", 0)
        if fixable_count > 0:
            lines.append(f"- 优先修复 {fixable_count} 个可自动修复的问题")
        security_count = by_type.get("security", 0)
        if security_count > 0:
            lines.append(f"- **紧急**: 处理 {security_count} 个安全相关问题")
        tech_debt = by_type.get("tech_debt", 0)
        if tech_debt > 0:
            lines.append(f"- 清理 {tech_debt} 个技术债务项")
        lines.append("- 运行完整测试套件验证修复")
    else:
        lines.append("- 当前无已知问题，代码质量良好")
    lines.append("")

    lines.append("---")
    lines.append(f"*此报告由自动迭代框架生成*")

    # 写入文件
    content = "\n".join(lines)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"[OK] 报告已生成: {report_path}")
    return report_path


def main():
    """主函数"""
    config = load_config()

    if len(sys.argv) > 1:
        try:
            iteration_num = int(sys.argv[1])
        except ValueError:
            print(f"[ERROR] 无效的迭代编号: {sys.argv[1]}")
            sys.exit(1)
    else:
        iteration_num = config.get("current_iteration", 0)

    report_path = generate_report(iteration_num)

    # 更新配置中的当前迭代
    config["current_iteration"] = iteration_num
    save_config(config)

    print(f"\n迭代 #{iteration_num} 报告生成完毕")
    print(f"报告路径: {report_path}")


if __name__ == "__main__":
    main()
