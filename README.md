# Personal Skills

[![skills.sh](https://skills.sh/b/abhikatta/personal-skills)](https://skills.sh/abhikatta/personal-skills)

Small, single-purpose LLM skills for the daily developer loop. Each one pairs a thin skill prompt with a deterministic script that gathers, verifies, or persists — the model only narrates.

Works with any model: Claude Code, OpenCode, Antigravity, local Llama, etc. No API keys, no servers.

## Skills

| Skill              | What it does                                                                                                                                                                                   |
| ------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `daylog`           | Summarizes a day's git commits into short, copy-paste pointers for Slack and timesheets. Pure prompt, zero dependencies beyond `git`.                                                          |
| `daily-journal` | Captures the day's work **with reasons and decisions** into a persistent journal and recalls past days. Two modes: **personal** (`~/timesheets/YYYY-MM-DD.md`, private) or **team** (`<repo>/docs/journals/YYYY-MM-DD/<author>.md`, shared, one file per author so teammates never conflict). |

## Requirements

- `git` (any recent version) and `python3` (stdlib only, for the journal script). That's it.

## Install

**Option A — one command (recommended):**

```bash
npx skills add abhikatta/personal-skills
```

Pick the skills you want and the agents to install them on. Re-run to update later (`npx skills update`).

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

(Same pattern for `daily-journal`: link `~/personal-skills/skills/daily-journal`.)

## Usage

Talk to your agent in any repo:

- _"Daylog 2026/09/16"_ — pointers for Slack, nothing persisted.
- _"Journal today"_ — captures what changed **and why** (reasons, decisions, bug cause → fix) into your journal.
- _"Journal this"_ (with specific commits/files in context) — journals just that scope.
- _"Log today to the team journal"_ — appends to `docs/journals/2026-09-16/<you>.md` and commits it as `journal: <you> 2026-09-16` (never mixed into code commits).
- _"What did I do last Tuesday?"_ / _"Catch me up since Monday"_ — reads back personal entries or synthesizes the whole team's week, whys included.

After 19:00 local time, the agent nudges you once if today is unjournaled: _"🌙 Reminder: you haven't journaled today…"_

## Team habit: auto-journal after commits

No CI or hooks needed. Each teammate pastes this into their repo's `CLAUDE.md` (or `AGENTS.md`) once — since agents read it automatically, journaling becomes the default behavior:

```markdown
## Work journal

After every commit, append a plain-language entry for what changed **and why**
to `docs/journals/<today>/<your-git-username>.md` under a `## HH:MM` heading
(create folders as needed). Record reasons and decisions, not just changes:
why the old approach failed, how a bug was fixed (cause → fix), and decision
changes as old → new + reason without deleting the old entry. Do not commit
the journal file with code changes — at the end of the day commit journal
files separately as `journal: <username> <YYYY-MM-DD>`.
```

Requires the `daily-journal` skill installed. The per-author files mean teammates never merge-conflict.

## Layout

```
skills/daylog/SKILL.md
skills/daily-journal/SKILL.md
skills/daily-journal/scripts/journal.py
```

Standard `skills/<name>/SKILL.md` layout — no manifest needed. skills.sh discovers it automatically.
