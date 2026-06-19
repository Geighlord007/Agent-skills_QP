#!/usr/bin/env bash
# bootstrap.sh - 给所有 agent 建 symlink
# Idempotent: 跑多少次都不会破坏已有设置

set -e

SKILL_DIR="$HOME/agent-skills/skills"

# Agents to check (label -> target directory)
# Only global paths; add yours as needed
AGENTS=(
  "opencode:$HOME/.config/opencode/skills"
  "claude-code:$HOME/.claude/skills"
  "codex:$HOME/.codex/skills"
  "cursor:$HOME/.cursor/skills"
  "windsurf:$HOME/.codeium/windsurf/skills"
  "gemini-cli:$HOME/.gemini/skills"
  "qwen-code:$HOME/.qwen/skills"
  "kiro-cli:$HOME/.kiro/skills"
  "continue:$HOME/.continue/skills"
  "roo:$HOME/.roo/skills"
  "universal:$HOME/.agents/skills"
)

# Sanity check
if [ ! -d "$SKILL_DIR" ]; then
  echo "❌ 错误: 找不到 $SKILL_DIR"
  echo "   请确认你在 agent-skills 仓库的根目录里跑这个脚本"
  exit 1
fi

# Find all skills (directories containing SKILL.md)
shopt -s nullglob
SKILLS=()
for dir in "$SKILL_DIR"/*/; do
  if [ -f "$dir/SKILL.md" ]; then
    SKILLS+=("$(basename "$dir")")
  fi
done
shopt -u nullglob

if [ ${#SKILLS[@]} -eq 0 ]; then
  echo "⚠️  $SKILL_DIR 里没找到任何 skill"
  echo "   每个 skill 必须是包含 SKILL.md 的子目录，例如:"
  echo "     $SKILL_DIR/my-skill/SKILL.md"
  exit 0
fi

echo "📦 找到 ${#SKILLS[@]} 个 skill: ${SKILLS[*]}"
echo

installed_count=0
for entry in "${AGENTS[@]}"; do
  label="${entry%%:*}"
  target_dir="${entry#*:}"

  # Skip agents that aren't installed (dir doesn't exist)
  if [ ! -d "$target_dir" ]; then
    continue
  fi

  installed_count=$((installed_count + 1))
  echo "→ $label ($target_dir)"

  for skill in "${SKILLS[@]}"; do
    src="$SKILL_DIR/$skill"
    dst="$target_dir/$skill"

    if [ -L "$dst" ] && [ "$(readlink "$dst")" = "$src" ]; then
      echo "  ✓ $skill (已链接)"
    elif [ -e "$dst" ]; then
      echo "  ⚠️  $skill 位置已有东西但不是 symlink，跳过（请手动处理）"
    else
      ln -s "$src" "$dst"
      echo "  + $skill (新建 symlink)"
    fi
  done
  echo
done

if [ $installed_count -eq 0 ]; then
  echo "⚠️  没检测到任何已安装的 agent"
  echo "   检测路径:"
  for entry in "${AGENTS[@]}"; do
    target_dir="${entry#*:}"
    echo "     - $target_dir"
  done
  echo "   装好 agent 后重跑本脚本即可"
else
  echo "✅ 完成 ($installed_count 个 agent 已配置)"
fi
