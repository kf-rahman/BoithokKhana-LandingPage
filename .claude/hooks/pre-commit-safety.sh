#!/usr/bin/env bash
#
# Pre-commit safety hook for the Boithok Khana site.
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

# 3. index.html is the whole site — don't ship it with unbalanced tags.
#    A stray unclosed <div> silently swallows the rest of the page.
if git diff --cached --name-only | grep -E '^index\.html$' > /dev/null; then
  echo "index.html changed — checking tag balance..."
  python3 - <<'PYEOF' || FAIL=1
from html.parser import HTMLParser
import subprocess, sys

VOID = {"br", "img", "input", "meta", "link", "hr", "source", "area", "base", "col"}
html = subprocess.run(["git", "show", ":index.html"], capture_output=True, text=True).stdout

class Check(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack = []
        self.problems = []

    def handle_starttag(self, tag, attrs):
        if tag not in VOID:
            self.stack.append((tag, self.getpos()[0]))

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if self.stack and self.stack[-1][0] == tag:
            self.stack.pop()
        else:
            self.problems.append(f"line {self.getpos()[0]}: unexpected </{tag}>")

c = Check()
c.feed(html)
for tag, line in c.stack:
    c.problems.append(f"line {line}: <{tag}> is never closed")

if c.problems:
    print("BLOCKED: index.html has unbalanced tags:")
    for p in c.problems[:10]:
        print("  " + p)
    sys.exit(1)
PYEOF
fi

# 4. Every nav/tab id must have a div to show. A showPage('x') or
#    showMenu('x') pointing at a missing id looks fine in the diff and does
#    nothing on the page — the kind of break a customer finds, not you.
if git diff --cached --name-only | grep -E '^index\.html$' > /dev/null; then
  echo "index.html changed — checking page/tab ids resolve..."
  python3 - <<'PYEOF' || FAIL=1
import re, subprocess, sys

html = subprocess.run(["git", "show", ":index.html"], capture_output=True, text=True).stdout

def ids_with_class(cls):
    return {
        m.group(1)
        for m in re.finditer(r'<div\s+id="([\w-]+)"\s+class="([^"]*)"', html)
        if cls in m.group(2).split()
    }

problems = []
for fn, cls in (("showPage", "page"), ("showMenu", "menu-content")):
    targets = set(re.findall(fn + r"\('([\w-]+)'", html))
    missing = sorted(targets - ids_with_class(cls))
    for m in missing:
        problems.append(f"{fn}('{m}') has no <div id=\"{m}\"> with class {cls}")

if problems:
    print("BLOCKED: index.html links to sections that don't exist:")
    for p in problems:
        print("  " + p)
    sys.exit(1)
PYEOF
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
