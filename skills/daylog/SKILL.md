---
name: daylog
description: >-
  Summarize a day's work from git commits into short, copy-paste pointers for Slack and timesheets.
  Use when the user asks for daylog, daily summary, standup update, timesheet update, or what did I do today.
---

# Daylog Skill

Turn one day's git commits into short, plain-language pointers ready to paste into Slack and daily timesheets.

Requires only `git`. The `gh` CLI and its `daylog` alias are optional shortcuts — never block on them.

## Step 1: Get the date

- If the user gave a date, use it. Accept `YYYY/MM/DD`, `YYYY-MM-DD`, `today`, or `yesterday`, and normalize to `YYYY/MM/DD`.
- If no date was given, use today in `YYYY/MM/DD` format.
- Confirm which date you are summarizing.

## Step 2: Get the commits

Run in the target repo (default: current working directory). Try in this order, using the first one that works:

**Option A — the `gh` alias (if `gh` exists and the alias is configured):**

```bash
gh daylog YYYY/MM/DD
```

**Option B — plain git fallback (always works, no setup needed):**

```bash
git --no-pager log --author="$(git config user.name)" --since="<date> 00:00:00" --until="<date> 23:59:59" --pretty=format:'%h %s (%an, %ad)' --date=short
```

Handle failures as follows:

- `gh: command not found` or alias missing (check with `gh alias list`) → silently use Option B. Optionally offer the one-command alias setup from the README, but never require it.
- Empty `user.name` → retry Option B with `$(git config user.email)` instead. If both are empty, drop the `--author` flag and warn the user the list may include others' commits.
- `fatal: not a git repository` → stop and ask the user which repo to summarize.
- Empty output (exit 0, no commits) → say no commits were found for that date and stop. Suggest checking the date, the repo, or whether commits used a different author identity. Do not invent work.

## Step 3: Summarize

Summarize the commits as bullet pointers following these rules:

1. One pointer per meaningful piece of work. Merge micro-commits (`wip`, `fix typo`, `lint`) into the work they belong to.
2. Plain, non-technical language a manager can understand. Say what was done and why, not how. Avoid file names, function names, and stack traces unless they are the point.
3. Short and concise, but keep ticket IDs, PR numbers, and feature/component names (e.g. `PROJ-123`, `login page`, `payments API`).
4. Active voice, past tense. Each pointer is one line, max two.
5. No header, no greeting, no explanation. Output only the pointers so the user can copy-paste directly.

Example output:

```markdown
- Worked on PROJ-123 login page validation, fixed error handling for expired sessions.
- Updated payments API integration and resolved retry failures on timeout.
- Reviewed PR #45 and addressed feedback on the dashboard filters.
```
