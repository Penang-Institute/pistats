#!/usr/bin/env python3
"""Fetch Tableau Public view counts for every dashboard workbook.

Maps each dashboards/*/*.qmd page (via its embedded views/<workbook> URL) to
the workbook's viewCount from the Tableau Public profile API, and writes
keyPenangMetrics/output/view_counts.json as {page_stem: count}.

Run from the repo root before `quarto render` (pipeline / CI step).
Note: the profile API is undocumented; if it changes, this script fails
loudly and the site simply keeps showing the previous counts file.
"""
import json
import re
import subprocess
from pathlib import Path

API = ("https://public.tableau.com/public/apis/workbooks"
       "?profileName=penang.institute&start=0&count=50&visibility=NON_HIDDEN")  # API rejects count > 50
OUT = Path("keyPenangMetrics/output/view_counts.json")


def main() -> None:
    # ponytail: curl instead of urllib - Tableau's edge rejects Python's TLS
    # fingerprint with HTTP 400; curl (and GitHub Actions runners) pass fine
    raw = subprocess.run(
        ["curl", "-sf", "--max-time", "30", "-H", "User-Agent: Mozilla/5.0", API],
        check=True, capture_output=True, text=True,
    ).stdout
    data = json.loads(raw)
    counts = {w["workbookRepoUrl"]: w.get("viewCount", 0) for w in data["contents"]}

    out = {}
    # some pages keep the embed in a companion .js file (e.g. pop.qmd + pop.js)
    for src in list(Path("dashboards").glob("*/*.qmd")) + list(Path("dashboards").glob("*/*.js")):
        m = re.search(r"views/([A-Za-z0-9_]+)", src.read_text(encoding="utf-8"))
        if m and m.group(1) in counts:
            out.setdefault(src.stem, counts[m.group(1)])

    if not out:
        raise SystemExit("no workbook matches found - API shape changed?")
    OUT.write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    print(f"wrote {len(out)} counts to {OUT}")


if __name__ == "__main__":
    main()
