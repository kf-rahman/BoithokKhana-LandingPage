#!/usr/bin/env bash
#
# Pre-commit safety hook for the family catering order system.
# Wired up via .claude/settings.json as a PreToolUse hook on Bash
# commands matching `git commit`, OR installed as an actual git
# pre-commit hook (see install instructions at bottom of this file).
#
# Exit non-zero to BLOCK the commit. Keep checks fast — this runs on
# every commit attempt.

set -euo pipefail

FAIL=0

echo "Running pre-commit safety checks..."

# 1. Never commit .env or secrets files
if git diff --cached --name-only | grep -E '^\.env($|\.)' > /dev/null; then
  echo "BLOCKED: attempting to commit a .env file. Remove it from the commit."
  FAIL=1
fi

# 2. Catch obvious hardcoded API keys (Anthropic, generic patterns)
if git diff --cached -U0 | grep -E '(sk-ant-[A-Za-z0-9_-]{20,}|sk-[A-Za-z0-9]{20,})' > /dev/null; then
  echo "BLOCKED: a string matching an API key pattern was found in the diff."
  echo "If this is a false positive, review the diff manually before retrying."
  FAIL=1
fi

# 3. Block float usage for money fields (project non-negotiable)
#    Heuristic only — flags for human review, doesn't try to be perfect.
if git diff --cached -U0 -- '*.py' | grep -E '^\+.*\b(price|amount|cost|total)\b.*:\s*float\b' > /dev/null; then
  echo "WARNING: a diff line appears to type a money-related field as 'float'."
  echo "Per CLAUDE.md, money must be integer cents or Decimal, never float."
  echo "Review backend/app/models and backend/app/schemas before committing."
  FAIL=1
fi

# 4. Backend tests must pass if backend files changed
if git diff --cached --name-only | grep -E '^backend/' > /dev/null; then
  echo "Backend files changed — running pytest..."
  if [ -d "backend" ]; then
    # Prefer the project virtualenv so the hook works regardless of the
    # committer's active shell (the venv carries the test/runtime deps).
    backend_py="python"
    if [ -x "backend/.venv/bin/python" ]; then
      backend_py="$PWD/backend/.venv/bin/python"
    fi
    (cd backend && "$backend_py" -m pytest -q) || {
      echo "BLOCKED: backend tests are failing. Fix before committing."
      FAIL=1
    }
  fi
fi

# 5. Frontend type-check must pass if frontend files changed
if git diff --cached --name-only | grep -E '^frontend/' > /dev/null; then
  echo "Frontend files changed — running type-check..."
  if [ -d "frontend" ]; then
    (cd frontend && npm run type-check --silent) || {
      echo "BLOCKED: frontend type-check is failing. Fix before committing."
      FAIL=1
    }
  fi
fi

if [ "$FAIL" -ne 0 ]; then
  echo ""
  echo "Pre-commit checks failed. Commit blocked."
  exit 1
fi

echo "Pre-commit checks passed."
exit 0

# --- Install as a real git hook (recommended) ---
# From repo root:
#   cp .claude/hooks/pre-commit-safety.sh .git/hooks/pre-commit
#   chmod +x .git/hooks/pre-commit
#
# --- Or wire as a Claude Code PreToolUse hook (catches agent commits too) ---
# In .claude/settings.json:
# {
#   "hooks": {
#     "PreToolUse": [
#       {
#         "matcher": "Bash",
#         "hooks": [
#           { "type": "command", "command": "./.claude/hooks/pre-commit-safety.sh" }
#         ]
#       }
#     ]
#   }
# }
