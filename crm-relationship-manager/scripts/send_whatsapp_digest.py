#!/usr/bin/env python3
"""Builds the Sunday "who to reach out to" digest and sends it to your own WhatsApp via CallMeBot.

CallMeBot is free and only ever messages you — this script never contacts
anyone in your contacts list. Reads CALLMEBOT_PHONE / CALLMEBOT_APIKEY from
the environment, falling back to a local `.env` file (gitignored — see
docs/setup_guide.md) since shell environment variables don't persist between
separate Claude tool calls or Routine firings.

Usage:
  python3 send_whatsapp_digest.py            # builds the digest and sends it
  python3 send_whatsapp_digest.py --dry-run  # prints the digest, sends nothing
"""
import json
import os
import sys
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

DATA_PATH = Path(__file__).parent.parent / "data" / "contacts.json"
ENV_PATH = Path(__file__).parent.parent / ".env"


def load_env():
    env = dict(os.environ)
    if ENV_PATH.exists():
        for line in ENV_PATH.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            env.setdefault(key.strip(), value.strip())
    return env


def days_until(date_str, today):
    if not date_str:
        return None
    try:
        target = date.fromisoformat(date_str)
    except ValueError:
        return None
    return (target - today).days


def build_digest(data, today=None):
    today = today or date.today()
    due, birthdays = [], []

    for c in data["contacts"]:
        if c.get("status") == "Paused":
            continue
        follow_up_days = days_until(c.get("next_follow_up_date"), today)
        if follow_up_days is not None and follow_up_days <= 0:
            due.append(c)
        bday_days = days_until(c.get("next_birthday_date") or c.get("birthday"), today)
        if bday_days is not None and 0 <= bday_days <= 7:
            birthdays.append((c, bday_days))

    lines = ["\U0001F44B Sunday Network Check-in", ""]

    if due:
        lines.append(f"Reach out to ({len(due)}):")
        for c in due:
            work = f" ({c['work']})" if c.get("work") else ""
            lines.append(f"\n• {c['name']}{work}")
            lines.append(f"  {c.get('relationship_plan_note', 'Say hello and catch up.')}")
        lines.append("")
    else:
        lines.append("No one is due for follow-up this week. \U0001F389")
        lines.append("")

    if birthdays:
        lines.append("Upcoming birthdays:")
        for c, d in birthdays:
            lines.append(f"\n\U0001F382 {c['name']} — in {d} day(s)")

    return "\n".join(lines).strip(), bool(due or birthdays)


def send_callmebot(text, phone, apikey):
    url = "https://api.callmebot.com/whatsapp.php?" + urllib.parse.urlencode({
        "phone": phone, "text": text, "apikey": apikey,
    })
    with urllib.request.urlopen(url, timeout=15) as resp:
        return resp.read().decode("utf-8", errors="replace")


def main():
    dry_run = "--dry-run" in sys.argv

    with open(DATA_PATH) as f:
        data = json.load(f)

    digest_text, has_content = build_digest(data)
    print(digest_text)
    print()

    if not has_content:
        print("[nothing to send this week]")
        return

    if dry_run:
        print("[dry run — not sent]")
        return

    env = load_env()
    phone, apikey = env.get("CALLMEBOT_PHONE"), env.get("CALLMEBOT_APIKEY")
    if not phone or not apikey:
        print("CALLMEBOT_PHONE / CALLMEBOT_APIKEY not set — see docs/setup_guide.md", file=sys.stderr)
        sys.exit(1)

    result = send_callmebot(digest_text, phone, apikey)
    print(f"[sent] {result}")


if __name__ == "__main__":
    main()
