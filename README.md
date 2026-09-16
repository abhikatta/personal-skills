# Daylog Skill

[![skills.sh](https://skills.sh/b/abhikatta/personal-skills)](https://skills.sh/abhikatta/personal-skills)

A single LLM skill that turns your day's git commits into short, copy-paste pointers for Slack and timesheets.

Works with any model: Claude Code, OpenCode, Antigravity, local Llama, etc. The model itself does the summarizing — no API keys, no local server, no scripts needed.

## Requirements

- **Required:** `git` (any recent version).
- **Optional:** [GitHub CLI (`gh`)](https://cli.github.com/) + the `daylog` alias below. Without them the skill falls back to plain `git log` automatically — nothing breaks.

## Install

**Option A — one command (recommended):**

```bash
npx skills add abhikatta/personal-skills
```

Pick the skill and the agents to install it on. Re-run to update later (`npx skills update`).

**Option B — manual link** (clone once, link into your agent's skills path):

```bash
git clone https://github.com/abhikatta/personal-skills ~/personal-skills
```

```bash
# Antigravity / Gemini (global)
mkdir -p ~/.gemini/config/skills && ln -s ~/personal-skills/skills/daylog ~/.gemini/config/skills/daylog

# Claude Code (project; ~/.claude/skills for global)
mkdir -p .claude/skills && ln -s ~/personal-skills/skills/daylog .claude/skills/daylog

# OpenCode (project; ~/.config/opencode/skills for global)
mkdir -p .opencode/skills && ln -s ~/personal-skills/skills/daylog .opencode/skills/daylog
```

## `gh daylog` alias (optional)

So `gh daylog YYYY/MM/DD` lists your commits for a day:

```bash
gh alias set daylog --shell - <<'EOF'
git --no-pager log --author="$(git config user.name)" --since="$1 00:00:00" --until="$1 23:59:59"
EOF
```

Verify with `gh alias list`. To overwrite an old definition, add `--clobber`. The skill works without this (plain `git log` fallback).

## Usage

Talk to your agent in any repo:

- _"Daylog 2026/09/16"_
- _"Summarize what I did today for Slack"_
- _"Give me my timesheet update for yesterday"_

The agent fetches that day's commits (via `gh daylog` or plain `git log` if `gh`/the alias is missing) and returns plain-language bullet pointers — short and concise, ticket IDs and feature names kept, no extra fluff — ready to paste into Slack or your timesheet.

## Layout

```
skills/daylog/SKILL.md
```

Standard `skills/<name>/SKILL.md` layout — no manifest needed. skills.sh discovers it automatically.
