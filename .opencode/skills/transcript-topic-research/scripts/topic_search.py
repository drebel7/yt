#!/usr/bin/env python3
"""Deterministic regex search over transcript TXT files (no LLM).

Scans transcript files, counts keyword hits and writes a Markdown thematic
index. Designed to be called by the transcript-topic-research skill.
"""

import argparse
import json
import os
import re
import sys
from datetime import date


def read_header(path):
    """Return (title, url, published, language) from a transcript header."""
    title = url = published = language = ""
    try:
        with open(path, encoding="utf-8", errors="replace") as handle:
            for _ in range(8):
                line = handle.readline()
                if not line:
                    break
                line = line.rstrip("\r\n")
                if line.startswith("Title: "):
                    title = line[7:].strip()
                elif line.startswith("URL: "):
                    url = line[5:].strip()
                elif line.startswith("Published: "):
                    published = line[11:].strip()
                elif line.startswith("Language: "):
                    language = line[10:].strip()
    except OSError as exc:
        print(f"warning: cannot read {path}: {exc}", file=sys.stderr)
    return title, url, published, language


def iter_transcripts(root):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]
        for name in filenames:
            if name.lower().endswith(".txt"):
                yield os.path.join(dirpath, name)


def md_cell(text):
    return text.replace("|", "\\|").replace("\n", " ").strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default="transkrypcje", help="transcript root directory")
    parser.add_argument("--topic", required=True, help="topic slug used in the output name")
    parser.add_argument("--pattern", required=True, help="Python regex, case-insensitive")
    parser.add_argument("--out", help="output Markdown path")
    parser.add_argument("--json", help="optional JSON output path")
    parser.add_argument("--label", help="human-readable topic label for the heading")
    parser.add_argument("--case-sensitive", action="store_true", help="match case-sensitively")
    args = parser.parse_args()

    root = os.path.abspath(args.root)
    out_path = os.path.abspath(args.out or os.path.join(root, "_tematy", f"{args.topic}.md"))
    out_dir = os.path.dirname(out_path)
    os.makedirs(out_dir, exist_ok=True)

    try:
        regex = re.compile(args.pattern, 0 if args.case_sensitive else re.IGNORECASE)
    except re.error as exc:
        print(f"error: invalid regex: {exc}", file=sys.stderr)
        return 2

    rows = []
    total_hits = 0
    for path in iter_transcripts(root):
        # The thematic indexes live under _tematy and are not transcripts.
        if os.path.abspath(path).startswith(os.path.abspath(os.path.join(root, "_tematy")) + os.sep):
            continue
        try:
            with open(path, encoding="utf-8", errors="replace") as handle:
                text = handle.read()
        except OSError as exc:
            print(f"warning: cannot read {path}: {exc}", file=sys.stderr)
            continue

        hits = len(regex.findall(text))
        if not hits:
            continue

        title, url, published, language = read_header(path)
        channel = os.path.basename(os.path.dirname(path)) or "root"
        if not title:
            title = os.path.splitext(os.path.basename(path))[0]
        if not published:
            match = re.match(r"(\d{4}-\d{2}-\d{2})", os.path.basename(path))
            published = match.group(1) if match else "0000-00-00"
        rel_link = os.path.relpath(path, out_dir).replace(os.sep, "/")
        rows.append(
            {
                "date": published,
                "channel": channel,
                "title": title,
                "url": url,
                "language": language,
                "hits": hits,
                "path": path,
                "link": rel_link,
            }
        )
        total_hits += hits

    rows.sort(key=lambda row: (row["date"], row["channel"].lower(), row["title"].lower()))
    label = args.label or args.topic

    by_channel = {}
    for row in rows:
        entry = by_channel.setdefault(row["channel"], {"files": 0, "hits": 0})
        entry["files"] += 1
        entry["hits"] += row["hits"]
    channel_rows = sorted(by_channel.items(), key=lambda item: (-item[1]["hits"], item[0].lower()))

    lines = [
        f"# Thematic index — {label}",
        "",
        "Deterministic regex search (no LLM) over transcript files.",
        "",
        f"- **Pattern:** `{args.pattern}` ({'case-sensitive' if args.case_sensitive else 'case-insensitive'})",
        f"- **Root:** `{os.path.relpath(root, os.getcwd()).replace(os.sep, '/')}`",
        f"- **Files with matches:** {len(rows)}",
        f"- **Total matches:** {total_hits}",
        f"- **Generated:** {date.today().isoformat()}",
        "",
        "## Matches by channel",
        "",
        "| Channel | Files | Hits |",
        "| --- | ---: | ---: |",
    ]
    for channel, stats in channel_rows:
        lines.append(f"| {md_cell(channel)} | {stats['files']} | {stats['hits']} |")

    lines.extend(
        [
            "",
            "## Files",
            "",
            "| Date | Channel | Title | Language | Hits | File |",
            "| --- | --- | --- | --- | ---: | --- |",
        ]
    )
    for row in rows:
        title = md_cell(row["title"])
        link = f"[{title}](<{row['link']}>)"
        if row["url"]:
            title_cell = link
        else:
            title_cell = title
        lines.append(
            f"| {row['date']} | {md_cell(row['channel'])} | {title_cell} | {md_cell(row['language'] or '?')} | {row['hits']} | `{row['link']}` |"
        )

    if not rows:
        lines.extend(["", "_No matches._"])

    with open(out_path, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines).rstrip() + "\n")

    if args.json:
        json_path = os.path.abspath(args.json)
        os.makedirs(os.path.dirname(json_path), exist_ok=True)
        with open(json_path, "w", encoding="utf-8") as handle:
            json.dump(
                {
                    "topic": args.topic,
                    "label": label,
                    "pattern": args.pattern,
                    "case_sensitive": args.case_sensitive,
                    "root": root,
                    "generated": date.today().isoformat(),
                    "files": len(rows),
                    "hits": total_hits,
                    "matches": [{k: v for k, v in row.items() if k != "path"} for row in rows],
                },
                handle,
                ensure_ascii=False,
                indent=2,
            )

    print(f"{len(rows)} files, {total_hits} matches -> {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
