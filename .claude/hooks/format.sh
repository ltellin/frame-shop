#!/usr/bin/env bash
# PostToolUse hook: auto-format the file that was just edited.
# Reads the hook payload as JSON on stdin; formats *.py with ruff. Never fails
# the edit — a formatter problem must not block work.
set -u

payload=$(cat)
file=$(printf '%s' "$payload" | jq -r '.tool_input.file_path // .tool_input.path // empty' 2>/dev/null || true)
[ -z "${file:-}" ] && exit 0
[ -f "$file" ] || exit 0

repo="${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel 2>/dev/null)}"
ruff="$repo/backend/.venv/bin/ruff"
[ -x "$ruff" ] || exit 0

case "$file" in
  *.py)
    "$ruff" format "$file" >/dev/null 2>&1 || true
    "$ruff" check --fix --quiet "$file" >/dev/null 2>&1 || true
    ;;
esac

exit 0
