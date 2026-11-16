#!/usr/bin/env python3
"""Archive GitHub traffic for this repo into site/data/traffic.json (stdlib only).

GitHub keeps clone and view counts for 14 days. This merges each run's window into a per-day
history so the numbers survive, and the Home page reads the file.

Needs a token that can read repo traffic (fine-grained: Administration read; classic: repo).
The default Actions token cannot.

  GH_TOKEN=... python3 tools/traffic.py
"""
import datetime
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "site" / "data" / "traffic.json"
SCHEMA = "navidx-traffic/1"
DEFAULT_REPO = "tp9imka/navigation-index"
# The repo went public on this day. Earlier clones were its own CI and deploy builds only.
TRACKING_SINCE = "2026-11-16"
API = "https://api.github.com"
TIMEOUT_S = 30
MAX_REFERRERS = 10


def fetch(repo, path, token):
    req = urllib.request.Request(f"{API}/repos/{repo}{path}", headers={
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "navigation-index-traffic",
    })
    with urllib.request.urlopen(req, timeout=TIMEOUT_S) as resp:
        return json.load(resp)


def merge_days(stored, clones, views, since):
    """Per-day history. A day inside the API window is overwritten (the latest day is partial until
    the next run); a day that has left the window keeps what was stored."""
    days = {d["date"]: dict(d) for d in stored if d["date"] >= since}
    for key, uniq, rows in (("clones", "unique_cloners", clones), ("views", "unique_visitors", views)):
        for row in rows:
            date = row["timestamp"][:10]
            if date < since:
                continue
            day = days.setdefault(date, {"date": date, "clones": 0, "unique_cloners": 0,
                                         "views": 0, "unique_visitors": 0})
            day[key], day[uniq] = row["count"], row["uniques"]
    return [days[d] for d in sorted(days)]


def window_uniques(payload, key, since):
    """GitHub's 14-day unique count, or None while that window still reaches before `since`:
    uniques cannot be re-derived per day, so a mixed window has no truthful value."""
    rows = payload.get(key) or []
    if not rows or rows[0]["timestamp"][:10] < since:
        return None
    return payload["uniques"]


def build(stored, clones, views, referrers, repo_info, repo, today, since=TRACKING_SINCE):
    days = merge_days((stored or {}).get("days", []), clones.get("clones", []), views.get("views", []), since)
    return {
        "schema": SCHEMA,
        "generated_by": "tools/traffic.py",
        "repo": repo,
        "since": since,
        "updated": today,
        "totals": {"clones": sum(d["clones"] for d in days), "views": sum(d["views"] for d in days)},
        "window_14d": {"unique_cloners": window_uniques(clones, "clones", since),
                       "unique_visitors": window_uniques(views, "views", since)},
        "stars": repo_info["stargazers_count"],
        "forks": repo_info["forks_count"],
        # Same 14-day window as the uniques: empty until none of it predates `since`.
        "referrers_14d": [{"referrer": r["referrer"], "count": r["count"], "uniques": r["uniques"]}
                          for r in referrers[:MAX_REFERRERS]]
                         if window_uniques(views, "views", since) is not None else [],
        "days": days,
    }


def main():
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not token:
        sys.exit("traffic: set GH_TOKEN to a token that can read repo traffic")
    repo = os.environ.get("GITHUB_REPOSITORY") or DEFAULT_REPO
    try:
        clones = fetch(repo, "/traffic/clones", token)
        views = fetch(repo, "/traffic/views", token)
        referrers = fetch(repo, "/traffic/popular/referrers", token)
        repo_info = fetch(repo, "", token)
    except urllib.error.HTTPError as err:
        sys.exit(f"traffic: GitHub answered {err.code} for {err.url} (token needs traffic read access)")
    stored = json.loads(OUT.read_text()) if OUT.exists() else None
    today = datetime.datetime.now(datetime.timezone.utc).date().isoformat()
    payload = build(stored, clones, views, referrers, repo_info, repo, today)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=1) + "\n")
    print(f"traffic: {len(payload['days'])} days since {payload['since']}, "
          f"clones {payload['totals']['clones']}, views {payload['totals']['views']}, stars {payload['stars']}")


if __name__ == "__main__":
    main()
