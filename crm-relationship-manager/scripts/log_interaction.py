#!/usr/bin/env python3
"""Logs a conversation with a contact, or adds a brand-new one, then recomputes their cadence.

Claude runs this whenever you mention (in chat) that you talked to someone or
met someone new — there's no separate form. After running it, Claude creates/
updates the follow-up reminder in Google Calendar and records the event ID
with `sync.py set-event-id`.

Usage:
  python3 log_interaction.py "Jane Doe" --notes "Caught up about the arbitration referral"
  python3 log_interaction.py "New Person" --category "New Contact" --priority Medium \
      --busy Moderate --phone "+234..." --email "..." --work "..." --notes "Met at ..."
"""
import argparse
import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from cadence import recompute_contact, CATEGORIES, PRIORITIES, BUSY_LEVELS  # noqa: E402

DATA_PATH = Path(__file__).parent.parent / "data" / "contacts.json"


def load():
    with open(DATA_PATH) as f:
        return json.load(f)


def save(data):
    with open(DATA_PATH, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("name")
    parser.add_argument("--notes", default="")
    parser.add_argument("--contacted-date", default=None, help="YYYY-MM-DD, defaults to today")
    parser.add_argument("--phone")
    parser.add_argument("--email")
    parser.add_argument("--birthday", help="YYYY-MM-DD")
    parser.add_argument("--education")
    parser.add_argument("--work")
    parser.add_argument("--category", choices=CATEGORIES)
    parser.add_argument("--priority", choices=PRIORITIES)
    parser.add_argument("--busy", dest="busy_level", choices=BUSY_LEVELS)
    parser.add_argument("--goal", dest="relationship_goal")
    args = parser.parse_args()

    data = load()
    today_str = args.contacted_date or date.today().isoformat()

    match = None
    for contact in data["contacts"]:
        if contact["name"].strip().lower() == args.name.strip().lower():
            match = contact
            break

    if match is None:
        contact = {
            "name": args.name,
            "phone": args.phone or "",
            "email": args.email or "",
            "birthday": args.birthday or "",
            "education": args.education or "",
            "work": args.work or "",
            "relationship_category": args.category or "New Contact",
            "priority": args.priority or "Medium",
            "busy_level": args.busy_level or "Moderate",
            "relationship_goal": args.relationship_goal or "",
            "notes": [],
            "last_contacted_date": None,
            "birthday_calendar_event_id": None,
            "followup_calendar_event_id": None,
            "status": "Active",
        }
        data["contacts"].append(contact)
        is_new = True
    else:
        contact = match
        is_new = False
        for field, value in (
            ("phone", args.phone), ("email", args.email), ("birthday", args.birthday),
            ("education", args.education), ("work", args.work),
            ("relationship_category", args.category), ("priority", args.priority),
            ("busy_level", args.busy_level), ("relationship_goal", args.relationship_goal),
        ):
            if value:
                contact[field] = value

    if args.notes:
        contact.setdefault("notes", []).insert(0, {"date": today_str, "text": args.notes})
    contact["last_contacted_date"] = today_str
    contact["followup_calendar_event_id"] = None  # force sync.py to (re)create the reminder

    updated = recompute_contact(contact, today=date.today())
    updated["notes"] = contact["notes"]
    updated["followup_calendar_event_id"] = None
    updated["birthday_calendar_event_id"] = contact.get("birthday_calendar_event_id")

    for i, c in enumerate(data["contacts"]):
        if c["name"].strip().lower() == args.name.strip().lower():
            data["contacts"][i] = updated
            break

    save(data)

    print(json.dumps({
        "is_new_contact": is_new,
        "name": updated["name"],
        "next_follow_up_date": updated["next_follow_up_date"],
        "relationship_plan_note": updated["relationship_plan_note"],
        "next_birthday_date": updated["next_birthday_date"],
    }, indent=2))


if __name__ == "__main__":
    main()
