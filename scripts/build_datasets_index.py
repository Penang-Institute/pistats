#!/usr/bin/env python3
"""Generate the Datasets page body from the dashboards themselves.

Every dashboard .qmd carries a "Download data" callout listing its source
datasets. Rather than copy those links onto datasets.qmd — where they would
silently rot the moment a dashboard changed — this script reads them at build
time and writes `_datasets_generated.md`, which datasets.qmd includes.

Wired in as a Quarto `pre-render` step, so it runs on every render, local and
CI alike. The generated file is gitignored: it is build output, not source.

Run from the project root:  python3 scripts/build_datasets_index.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

OUT = Path("_datasets_generated.md")
DASHBOARDS = Path("dashboards")

SECTIONS = {"econ": "Economic", "sector": "Sector-specific", "social": "Social"}

# Attribution is presentation metadata and does not exist in the .qmd files,
# so it lives here. A stem missing from this map renders without a source line
# rather than with a wrong one.
SOURCES = {
    "cpi": "DOSM / OpenDOSM", "gdp": "DOSM publication", "labour": "DOSM / OpenDOSM",
    "trade": "METS Online", "finance": "Penang State Government",
    "grad": "Ministry of Higher Education", "health": "Ministry of Health",
    "manf": "MIDA", "prop": "NAPIC", "gender": "DOSM", "hhinc": "DOSM",
    "pop": "DOSM / OpenDOSM",
}

LINK = re.compile(r"\[([^\]]+)\]\((https?://[^)]+)\)")
HEADING = re.compile(r"^#{3,6}\s+(.*)")


def parse(qmd: Path) -> dict:
    """Pull the title and the Download-data links out of one dashboard."""
    lines = qmd.read_text(encoding="utf-8").splitlines()

    title = next(
        (m.group(1) for m in (re.match(r'^title:\s*"(.*?)"', l) for l in lines) if m),
        qmd.stem,
    )

    start = next((i for i, l in enumerate(lines) if 'title="Download data"' in l), None)
    groups: dict[str, list[tuple[str, str]]] = {}
    if start is not None:
        current = "Datasets"
        for line in lines[start + 1:]:
            if line.strip() == ":::":          # callout closed
                break
            h = HEADING.match(line.strip())
            if h:
                current = h.group(1).strip()
                continue
            for name, url in LINK.findall(line):
                groups.setdefault(current, []).append((name.strip(), url.strip()))

    return {
        "stem": qmd.stem,
        "section": SECTIONS[qmd.parent.name],
        "path": f"dashboards/{qmd.parent.name}/{qmd.stem}.html",
        "title": title,
        "source": SOURCES.get(qmd.stem),
        "groups": groups,
    }


def render(entries: list[dict]) -> str:
    total = sum(len(v) for e in entries for v in e["groups"].values())
    out = [
        f"*{total} datasets across {len(entries)} dashboards. "
        "This page is generated from the dashboards themselves, so it always "
        "matches what each dashboard actually uses.*",
        "",
    ]
    for section in ("Economic", "Sector-specific", "Social"):
        in_section = [e for e in entries if e["section"] == section]
        if not in_section:
            continue
        out += [f"## {section}", ""]
        for e in in_section:
            count = sum(len(v) for v in e["groups"].values())
            out += ["::: {.ds-card}", ""]
            out.append(
                f"### [{e['title']}]({e['path']}) "
                f"[{count} dataset{'s' if count != 1 else ''}]{{.ds-count}}"
            )
            if e["source"]:
                out.append(f"[Source: {e['source']}]{{.ds-source}}")
            out.append("")
            if not e["groups"]:
                out += ["[No datasets are listed on this dashboard yet.]{.ds-empty}", ""]
            for group, links in e["groups"].items():
                out += [f"[{group}]{{.ds-group}}", "", "::: {.ds-list}", ""]
                out += [f"- [{name}]({url})" for name, url in links]
                out += ["", ":::", ""]
            out += [":::", ""]
    return "\n".join(out) + "\n"


def main() -> int:
    if not DASHBOARDS.is_dir():
        print(f"error: run from the project root; no {DASHBOARDS}/", file=sys.stderr)
        return 1

    entries = [
        parse(q)
        for q in sorted(DASHBOARDS.glob("*/*.qmd"))
        if q.parent.name in SECTIONS
    ]
    if not entries:
        print("error: no dashboards found — has the folder layout changed?", file=sys.stderr)
        return 1

    OUT.write_text(render(entries), encoding="utf-8")
    total = sum(len(v) for e in entries for v in e["groups"].values())
    print(f"wrote {OUT} — {total} datasets across {len(entries)} dashboards")

    empty = [e["stem"] for e in entries if not e["groups"]]
    if empty:
        print(f"  note: no datasets listed on: {', '.join(empty)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
