#!/usr/bin/env python3
"""
将共享记忆库的一行指针挂载到本机主流 Agent 入口文件：
- ~/.claude/CLAUDE.md (Claude Code & Devin)
- ~/.codex/AGENTS.md (Codex)
- ~/.gemini/GEMINI.md (Gemini CLI)

安全原则：
1. 默认展示将要修改的内容；如原文件已存在且内容不同，先备份为 .bak.<时间戳>（可逆隔离，不删原件）。
2. 入口文件只写一行指针，避免把长规则直接塞进入口造成上下文膨胀。
"""
import argparse
import os
import shutil
import time

TARGETS = [
    ("Claude Code / Devin", os.path.expanduser("~/.claude/CLAUDE.md")),
    ("Codex", os.path.expanduser("~/.codex/AGENTS.md")),
    ("Gemini CLI", os.path.expanduser("~/.gemini/GEMINI.md")),
]


def build_pointer_text(vault_dir: str) -> str:
    agents_md = os.path.join(vault_dir, "AGENTS.md")
    return f"# 全局：共享记忆（指针）\n\n遵循 `{agents_md}`。本文件不复制规则正文。\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="挂载多 Agent 共享记忆一行指针")
    parser.add_argument("--vault-dir", required=True, help="共享记忆目录绝对路径（内含 AGENTS.md 与 USER.md）")
    parser.add_argument("--dry-run", action="store_true", help="只预览变更，不实际写入")
    args = parser.parse_args()

    vault_dir = os.path.abspath(os.path.expanduser(args.vault_dir))
    pointer_text = build_pointer_text(vault_dir)
    ts = time.strftime("%Y%m%d-%H%M%S")

    print(f"目标记忆库真源: {vault_dir}")
    print(f"写入指针内容:\n---\n{pointer_text.strip()}\n---\n")

    for label, path in TARGETS:
        existing = None
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                existing = f.read()

        if existing == pointer_text:
            print(f"[跳过] {label} ({path}) 已是最新指针")
            continue

        if args.dry_run:
            status = "将备份并更新" if existing is not None else "将新建"
            print(f"[预览] {label} ({path}) -> {status}")
            continue

        os.makedirs(os.path.dirname(path), exist_ok=True)
        if existing is not None and existing.strip():
            bak_path = f"{path}.bak.{ts}"
            shutil.copy2(path, bak_path)
            print(f"[备份] 原文件已备份至 {bak_path}")

        with open(path, "w", encoding="utf-8") as f:
            f.write(pointer_text)
        print(f"[完成] {label} 指针已写入 {path}")


if __name__ == "__main__":
    main()
