#!/usr/bin/env python3
"""
journal.py - Append-only daily journal. Personal ledger or shared per-author team journals.

Personal mode (no --author): one file per date (<dir>/YYYY-MM-DD.md).
Team mode (--author <slug>): one file per author per date
(<dir>/YYYY-MM-DD/<slug>.md), so teammates never write the same file.

Each capture run appends a timestamped section, so morning/evening captures
never clobber each other. Re-running can replace instead of duplicating.

Usage:
  pointers... | journal.py append --date 2026-09-16 --repo myapp [--dir ~/timesheets]
  pointers... | journal.py append --date 2026-09-16 --author abhikatta --dir ./docs/journals
  pointers... | journal.py replace --date 2026-09-16 --repo myapp [--dir ~/timesheets]
  journal.py read --date 2026-09-16 [--dir ~/timesheets]
  journal.py read --from 2026-09-08 --to 2026-09-12 [--dir ~/timesheets]

Date accepts YYYY-MM-DD or YYYY/MM/DD. Dir defaults to $JOURNAL_DIR or ~/timesheets.
"""

import argparse
import os
import re
import sys
from datetime import datetime

DATE_RE = re.compile(r"^(\d{4})[/-](\d{2})[/-](\d{2})$")


def normalize_date(raw: str) -> str:
    raw = raw.strip()
    if raw.lower() == "today":
        return datetime.now().strftime("%Y-%m-%d")
    if raw.lower() == "yesterday":
        return datetime.fromtimestamp(
            datetime.now().timestamp() - 86400
        ).strftime("%Y-%m-%d")
    m = DATE_RE.match(raw)
    if not m:
        raise ValueError(f"Bad date {raw!r}: expected YYYY-MM-DD or YYYY/MM/DD")
    return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"


def resolve_dir(cli_dir: str | None = None) -> str:
    d = os.path.expanduser(cli_dir or os.environ.get("JOURNAL_DIR", os.environ.get("TIMESHEET_DIR", "~/timesheets")))
    os.makedirs(d, exist_ok=True)
    return d


def weekday(date_str: str) -> str:
    return datetime.strptime(date_str, "%Y-%m-%d").strftime("%A")


def slugify(raw: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", raw.strip().lower()).strip("-")
    if not slug:
        raise ValueError(f"Bad author {raw!r}: nothing left after slugify.")
    return slug


def target_path(d: str, date_str: str, author: str) -> tuple[str, str]:
    """Return (path, title) for personal or team mode."""
    if author:
        slug = slugify(author)
        os.makedirs(os.path.join(d, date_str), exist_ok=True)
        return os.path.join(d, date_str, f"{slug}.md"), f"# {date_str} ({weekday(date_str)}) — {slug}"
    return os.path.join(d, f"{date_str}.md"), f"# {date_str} ({weekday(date_str)})"


def section_header(repo: str) -> str:
    now = datetime.now().strftime("%H:%M")
    return f"## {now} — {repo}" if repo else f"## {now}"


def read_stdin() -> str:
    text = sys.stdin.read().strip()
    if not text:
        raise ValueError("No pointers received on stdin.")
    return text


def cmd_append(args) -> None:
    d = resolve_dir(args.dir)
    date_str = normalize_date(args.date)
    path, title = target_path(d, date_str, args.author or "")
    body = read_stdin()
    header = section_header("" if args.author else args.repo)
    entry = f"\n{header}\n\n{body}\n"
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"{title}\n{entry}")
    else:
        with open(path, "a", encoding="utf-8") as f:
            f.write(entry)
    print(path)


def cmd_replace(args) -> None:
    d = resolve_dir(args.dir)
    date_str = normalize_date(args.date)
    path, title = target_path(d, date_str, args.author or "")
    body = read_stdin()
    header = section_header("" if args.author else args.repo)
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"{title}\n\n{header}\n\n{body}\n")
    print(path)


def print_file(path: str) -> None:
    with open(path, encoding="utf-8") as f:
        print(f.read().rstrip())
        print()


def read_date(d: str, date_str: str) -> bool:
    """Print personal file and/or team author files for a date. Return True if any found."""
    found = False
    personal = os.path.join(d, f"{date_str}.md")
    if os.path.exists(personal):
        print_file(personal)
        found = True
    team_dir = os.path.join(d, date_str)
    if os.path.isdir(team_dir):
        for name in sorted(os.listdir(team_dir)):
            if name.endswith(".md"):
                print_file(os.path.join(team_dir, name))
                found = True
    return found


def list_dates(d: str, start: str, end: str) -> list[str]:
    dates = set()
    for name in os.listdir(d):
        full = os.path.join(d, name)
        if name.endswith(".md") and start <= name[:-3] <= end:
            dates.add(name[:-3])
        elif os.path.isdir(full) and DATE_RE.match(name) and start <= name <= end:
            if any(f.endswith(".md") for f in os.listdir(full)):
                dates.add(name)
    return sorted(dates)


def cmd_read(args) -> None:
    d = resolve_dir(args.dir)
    if args.date:
        if not read_date(d, normalize_date(args.date)):
            print(f"No entry for {args.date}.")
        return
    start, end = normalize_date(args.frm), normalize_date(args.to)
    if start > end:
        start, end = end, start
    dates = list_dates(d, start, end)
    if not dates:
        print(f"No entries from {start} to {end}.")
        return
    for date_str in dates:
        read_date(d, date_str)


def main() -> None:
    parser = argparse.ArgumentParser(description="Append-only daily journal. Personal ledger or shared per-author team journals.")
    parser.add_argument("--dir", default=None, help="Journal dir (default: $JOURNAL_DIR or ~/timesheets)")
    sub = parser.add_subparsers(dest="cmd", required=True)

    def add_common(p):
        # Repeat --dir on each subcommand so it works before AND after it.
        # SUPPRESS avoids the subparser default clobbering a pre-subcommand value.
        p.add_argument("--dir", default=argparse.SUPPRESS, help="Journal dir (default: $JOURNAL_DIR or ~/timesheets)")
        return p

    p_append = add_common(sub.add_parser("append", help="Append a timestamped entry for a date"))
    p_append.add_argument("--date", required=True)
    p_append.add_argument("--repo", default="")
    p_append.add_argument("--author", default="", help="Team mode: write to <date>/<author>.md")
    p_append.set_defaults(func=cmd_append)

    p_replace = add_common(sub.add_parser("replace", help="Rewrite a date's file (idempotent re-run)"))
    p_replace.add_argument("--date", required=True)
    p_replace.add_argument("--repo", default="")
    p_replace.add_argument("--author", default="", help="Team mode: write to <date>/<author>.md")
    p_replace.set_defaults(func=cmd_replace)

    p_read = add_common(sub.add_parser("read", help="Read entries"))
    p_read.add_argument("--date", default=None)
    p_read.add_argument("--from", dest="frm", default=None)
    p_read.add_argument("--to", dest="to", default=None)
    p_read.set_defaults(func=cmd_read)

    args = parser.parse_args()
    try:
        args.func(args)
    except (ValueError, OSError) as e:
        print(f"journal: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
