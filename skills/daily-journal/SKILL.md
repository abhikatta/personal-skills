---
name: daily-journal
description: >-
  Capture the day's work into a persistent journal with reasons and decisions, not just changes.
  Use when the user says journal today, journal this, log today, save the daylog, catch up on the week,
  what did I/we do on <date>, or asks anything at/after 7pm local time (evening journal reminder).
---

# Daily Journal Skill

Summarize the day's commits **with the reasoning behind them** and persist to a journal: personal (`$JOURNAL_DIR`, default `~/timesheets`) or shared team journals (`<repo>/docs/journals/YYYY-MM-DD/<author>.md`). The script is the source of truth for storage. The model only narrates.

## Storage choice (ask once, then remember)

- **Personal:** `$JOURNAL_DIR` (falls back to `$TIMESHEET_DIR`, then `~/timesheets`), one file per date. Private, never committed to a shared repo.
- **Team:** `<repo>/docs/journals`, one folder per date with one file per author (`2026-09-16/abhikatta.md`). Shared, committed with prefix `journal:` (see Mode 1, Step 4).

If the journal dir points inside a repo's `docs/journals`, use team mode. Otherwise ask the user which they want.

## Mode 1: Capture — "journal today" / "journal this"

### Step 1: Get the date, repo, and author

- Date: user-given or today, normalized to `YYYY-MM-DD`. Confirm it.
- Repo: current working directory (verify with `git rev-parse --show-toplevel`); use `git -C <path>` if the workspace differs.
- "Journal this" (specific commits/files): scope to what the user pointed at instead of the whole day.
- Author slug: the user's `git config user.name`, verbatim and consistent every time (the script slugifies it: `Abhinay Katta` → `abhinay-katta`). Required in team mode, ignored in personal mode.

### Step 2: Get the commits

```bash
git --no-pager log --author="$(git config user.name)" --since="<date> 00:00:00" --until="<date> 23:59:59" --pretty=format:'%h %s (%an, %ad)' --date=short
```

Same fallbacks as `daylog`: empty `user.name` → retry with `user.email`; both empty → drop `--author` with a warning. No commits → stop, do not invent work.

### Step 3: Write entries with WHAT + WHY

One entry per meaningful piece of work (merge `wip`/`typo` micro-commits). Each entry records:

1. **What** changed, plainly, with short commit hashes in parentheses: `- Moved cart state from useContext to zustand (a1b2c3d)`.
2. **Why** it changed: the reason, the problem with the old approach, the decision behind it. A new dev reading this in 6 months must understand the reasoning, not just the diff.
3. **Bugs as cause → fix**: what was broken, why, and how the fix addresses the cause — never just "fixed bug X".
4. **Changed decisions as old → new + reason, never rewrites**: if a decision replaced an earlier one, keep both visible: `- Switched checkout validation from client-side to server-side (d4e5f6g). Reason: client rules were bypassed by direct API calls; the earlier client-side approach (see 2026-09-02) stays recorded above.`

Sources for the why, in order: commit bodies (`git log --format=%B <hash>`), diff context (`git show --stat <hash>`), then the surrounding code. Ask the user only if the why is material and truly unrecoverable; otherwise write the what and mark `(reason not recorded)`.

Bad: `- Refactored state management to use zustand.`
Good: `- Moved cart state from useContext to zustand (a1b2c3d). useContext re-rendered the whole tree on every keystroke in checkout; zustand scopes updates to subscribers.`

### Step 4: Persist via the script (never hand-write journal files)

Personal:

```bash
<entries> | python3 <skill-dir>/scripts/journal.py append --date YYYY-MM-DD --repo <name>
```

Team (`--dir` pointing at the repo's `docs/journals`):

```bash
<entries> | python3 <skill-dir>/scripts/journal.py append --date YYYY-MM-DD --author <slug> --dir <repo>/docs/journals
```

- Later runs append a new timestamped section (morning/evening never clobber each other; teammates never share a file, so no merge conflicts).
- Re-running to fix an entry: use `replace` instead of `append` (idempotent rewrite). Decisions themselves stay append-only per Step 3.4.

### Step 5: Team mode — commit the journal

Commit journal files separately from code, never mixed into a code commit:

```bash
git add docs/journals/<date>/<slug>.md && git commit -m "journal: <slug> <date>"
```

### Step 6: Report back

Show the entries (ready to paste into Slack) plus the journal file path.

## Mode 2: Recall and catch-up

Read through the script, never by guessing paths:

```bash
python3 <skill-dir>/scripts/journal.py read --date YYYY-MM-DD
python3 <skill-dir>/scripts/journal.py read --from YYYY-MM-DD --to YYYY-MM-DD
```

- Personal (_"what did I do last Tuesday?"_) → read, then summarize.
- Team catch-up (_"what happened last week?"_, _"catch me up since Monday"_) → range-read the team dir, then synthesize per-author highlights **including the whys and decision changes**. Say which dates/authors had no entries.

## Evening nudge

When handling **any** query at or after 19:00 local time, check today's journal first:

```bash
python3 <skill-dir>/scripts/journal.py read --date today
```

If there is no entry for today yet, append exactly one line at the end of your response:

`🌙 Reminder: you haven't journaled today — say "journal today" before you log off.`

If an entry already exists, say nothing. Never nudge twice in one day — the existence check guarantees that.
