#!/usr/bin/env python3
"""Injects the current contacts.json into dashboard/dashboard.html, ready to publish as a Claude Artifact.

The dashboard is a static snapshot — it has no way to call any API itself
(Artifacts run in a locked-down sandbox with no outbound network access).
Every refresh, Claude re-runs this script and re-publishes the file with the
Artifact tool so the same URL always shows the latest data.

Usage:
  python3 build_dashboard.py
"""
import json
import re
from datetime import date
from pathlib import Path

DATA_PATH = Path(__file__).parent.parent / "data" / "contacts.json"
DASHBOARD_PATH = Path(__file__).parent.parent / "dashboard" / "dashboard.html"

START_MARKER = "<!-- CRM_DATA_START -->"
END_MARKER = "<!-- CRM_DATA_END -->"


def main():
    with open(DATA_PATH) as f:
        data = json.load(f)
    data["generated_at"] = date.today().isoformat()

    html = DASHBOARD_PATH.read_text()
    pattern = re.compile(re.escape(START_MARKER) + r".*?" + re.escape(END_MARKER), re.DOTALL)
    if not pattern.search(html):
        raise SystemExit(f"Could not find {START_MARKER} ... {END_MARKER} markers in dashboard.html")

    replacement = (
        f'{START_MARKER}\n'
        f'<script id="crm-data" type="application/json">\n'
        f'{json.dumps(data, indent=2)}\n'
        f'</script>\n'
        f'{END_MARKER}'
    )
    html = pattern.sub(lambda _match: replacement, html)
    DASHBOARD_PATH.write_text(html)
    print(f"dashboard.html updated with {len(data['contacts'])} contacts as of {data['generated_at']}.")
    print("Now publish it with the Artifact tool.")


if __name__ == "__main__":
    main()
