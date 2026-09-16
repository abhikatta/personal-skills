# Daylog Skill

A single LLM skill that turns your day's git commits into short, copy-paste pointers for Slack and timesheets.

Works with any model: Claude Code, OpenCode, local Llama, etc. The model itself does the summarizing — no API keys, no local server, no scripts needed.

## Requirements

- **Required:** `git` (any recent version).
- **Optional:** [GitHub CLI (`gh`)](https://cli.github.com/) + the `daylog` alias below. Without them the skill falls back to plain `git log` automatically — nothing breaks.

## Setup (one command each)

**1. Install the skill** — clone once, then link it into your agent's skills path:

```bash
git clone https://github.com/abhikatta/personal-skills ~/personal-skills
```

```bash
# Claude Code (project) — also works under ~/.claude/skills for global
mkdir -p .claude/skills && ln -s ~/personal-skills/skills/daylog .claude/skills/daylog

# OpenCode (project) — also works under ~/.config/opencode/skills for global
mkdir -p .opencode/skills && ln -s ~/personal-skills/skills/daylog .opencode/skills/daylog
```

**2. (Optional) Set up the `gh daylog` alias** so `gh daylog YYYY/MM/DD` lists your commits for a day:

```bash
gh alias set daylog --shell - <<'EOF'
git --no-pager log --author="$(git config user.name)" --since="$1 00:00:00" --until="$1 23:59:59"
EOF
```

Verify with `gh alias list`. To overwrite an old definition, add `--clobber`.

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
