# Running the Option A revamp locally (client demo)

Instructions for demoing the **Option A "Continuity"** homepage revamp on a
laptop, with no internet dependency beyond the Google font and the Tableau
view counts.

Branch: `revamp-test`. Nothing here is published. The live site
(statistics.penanginstitute.org) is unaffected by anything in this folder.

---

## TL;DR

```bash
cd /Users/subashanannair/Documents/02_projects/PENANG_INSTITUTE/pistats-revamp-test
quarto preview --port 8080
```

Then open **http://localhost:8080**. That is the whole demo.

---

## Before the meeting

### 1. Check Quarto is installed

```bash
quarto --version
```

Built and tested on **1.9.37**, which is what is installed on this machine. No R
and no Python packages are needed: the dashboards are Tableau embeds, not
computed documents, so a full render runs on Quarto alone (verified with a
clean `rm -rf _site && quarto render`, 19 of 19 files).

### 2. Refresh the Tableau view counts (optional, 5 seconds)

```bash
cd /Users/subashanannair/Documents/02_projects/PENANG_INSTITUTE/pistats-revamp-test
python3 scripts/fetch_view_counts.py
```

This writes `keyPenangMetrics/output/view_counts.json` and prints
`wrote 12 counts to ...`. It needs internet.

If you skip this, the counters simply do not appear. The cards still render
correctly, so a failed fetch will not embarrass you in front of the client.

### 3. Do a dry run

Run the TL;DR command, open the page, and confirm you see the checklist in
"What to point at" below. Do this **before** Friday, not during.

---

## Running it

```bash
cd /Users/subashanannair/Documents/02_projects/PENANG_INSTITUTE/pistats-revamp-test
quarto preview --port 8080
```

Quarto renders the site, starts a local server, and opens your browser at
http://localhost:8080. Leave the terminal window open: closing it stops the
server.

Port 8080 is already the configured default in `_quarto.yml`, so plain
`quarto preview` works too. Pass `--port` only if 8080 is busy.

To stop: press `Ctrl+C` in that terminal.

### Alternative: serve a pre-built copy

If you would rather not have Quarto rebuilding during the meeting, build once
beforehand and serve the static output:

```bash
cd /Users/subashanannair/Documents/02_projects/PENANG_INSTITUTE/pistats-revamp-test
quarto render
python3 -m http.server 8877 --directory _site
```

Then open http://localhost:8877. This is slightly more predictable because
nothing recompiles while you are presenting.

---

## What to point at

The client asked for Jost at roughly 14px, and that is the headline change.
Everything below has been verified working:

| Feature | What to say |
|---|---|
| **Typography** | Google Jost throughout, body text at exactly 14px |
| **"Data as of 2025"** (grey) | The period each figure actually covers |
| **"Updated 13 Aug 2026"** (red) | When the data pipeline last refreshed, updates itself every run |
| **View counters** | Live Tableau Public numbers, e.g. Population at 32,502 views |
| **Search box** | Searches across all dashboards and datasets |
| **Dashboards menu** | Regrouped into Economic / Sector-specific / Social |
| **Datasets page** | New top-level page in the navbar |

The two footer lines on each card are the April 2026 badge proposal, finally
built. They are worth calling out: the red line is what tells a reader the site
is being maintained, which is the thing that was invisible during the three
week data outage in July.

---

## Known rough edges

Be ready for these, in case the client spots them:

* **The "Dataset" link on each card goes to the dashboard**, not to a dataset.
  It is a placeholder pending a decision on where dataset links should point.
  Safest handling: do not click it during the demo.
* **View counts are fetched at build time**, not live in the browser. The number
  is correct as of whenever you last ran the script.
* **Residential Property** is still flagged as an open question in the original
  mock (keep it in the menu or not).

---

## Troubleshooting

**The freshness badges and view counters are missing.**

You almost certainly opened `_site/index.html` by double-clicking it. Both
features load their data with `fetch()`, which the browser blocks on `file://`
URLs. Use `quarto preview` or the `http.server` command above, and go through
`http://localhost:...`. This is the single most likely thing to go wrong.

**The numbers look stale after re-running the fetch script.**

The browser caches those JSON files. Hard reload with `Cmd+Shift+R`, or open
the page in a private window.

**Port already in use.**

```bash
lsof -ti:8080 | xargs kill
```

Or just pick another port with `--port 8081`.

**The font looks wrong (not geometric).**

Jost loads from fonts.googleapis.com, so it needs internet. Without it the page
falls back to the system sans-serif and still looks tidy, just not as specified.
If the venue wifi is unreliable, load the page once beforehand so the font is
cached.

**Quarto reports a render error.**

Rebuild from clean:

```bash
rm -rf _site .quarto && quarto render
```

---

## Refreshing the underlying data

The metrics shown come from the `keyPenangMetrics` submodule, currently holding
a copy of live production data (last pipeline run: 13 Aug 2026). To pull the
current published figures:

```bash
cd /Users/subashanannair/Documents/02_projects/PENANG_INSTITUTE/pistats-revamp-test
BASE=https://statistics.penanginstitute.org/keyPenangMetrics/output
for f in metrics_grid.yaml metrics_grid.json penang-monthly-stats.yaml; do
  curl -s "$BASE/$f" -o "keyPenangMetrics/output/$f"
done
quarto render index.qmd
```

Do not commit those files. They belong to the submodule, and the submodule
pointer in this worktree is deliberately left alone (it is behind
`origin/main`, and committing it would roll the site's data backwards).
