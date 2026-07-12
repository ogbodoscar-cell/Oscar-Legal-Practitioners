#!/usr/bin/env python3
"""Recomputes cadence for every contact and reports what needs a Google Calendar sync.

This script never talks to Google Calendar itself — it has no API credentials.
Claude runs it, reads the "pending_actions" it prints, creates/updates the
actual Calendar events using its native Google Calendar connector, then calls
`set-event-id` (below) to record the resulting event IDs so the same event
isn't recreated next time.

Usage:
  python3 sync.py recompute
  python3 sync.py set-event-id "Jane Doe" birthday evt_abc123
  python3 sync.py set-event-id "Jane Doe" followup evt_def456
"""
import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from cadence import recompute_contact  # noqa: E402

DATA_PATH = Path(__file__).parent.parent / "data" / "contacts.json"


def load():
    with open(DATA_PATH) as f:
        return json.load(f)


def save(data):
    data["generated_at"] = date.today().isoformat()
    with open(DATA_PATH, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


def cmd_recompute():
    data = load()
    today = date.today()
    pending_birthday = []
    pending_followup = []

    updated_contacts = []
    for contact in data["contacts"]:
        if contact.get("status") == "Paused":
            updated_contacts.append(contact)
            continue

        prev_follow_up = contact.get("next_follow_up_date")
        updated = recompute_contact(contact, today=today)
        updated_contacts.append(updated)

        if updated.get("birthday") and not updated.get("birthday_calendar_event_id"):
            pending_birthday.append({"name": updated["name"], "next_birthday_date": updated["next_birthday_date"]})

        follow_up_changed = updated.get("next_follow_up_date") != prev_follow_up
        if not updated.get("followup_calendar_event_id") or follow_up_changed:
            pending_followup.append({
                "name": updated["name"],
                "next_follow_up_date": updated["next_follow_up_date"],
                "relationship_plan_note": updated["relationship_plan_note"],
            })

    data["contacts"] = updated_contacts
    save(data)

    print(json.dumps({
        "recomputed": len(updated_contacts),
        "pending_birthday_events": pending_birthday,
        "pending_followup_events": pending_followup,
    }, indent=2))


def cmd_set_event_id(name, kind, event_id):
    if kind not in ("birthday", "followup"):
        print("kind must be 'birthday' or 'followup'", file=sys.stderr)
        sys.exit(1)
    data = load()
    field = "birthday_calendar_event_id" if kind == "birthday" else "followup_calendar_event_id"
    found = False
    for contact in data["contacts"]:
        if contact["name"] == name:
            contact[field] = event_id
            found = True
            break
    if not found:
        print(f"No contact named '{name}'", file=sys.stderr)
        sys.exit(1)
    save(data)
    print(f"Set {field} for {name} = {event_id}")


def cmd_clear_followup_event_id(name):
    """Call this when logging a fresh interaction so sync knows to create a new follow-up event."""
    data = load()
    found = False
    for contact in data["contacts"]:
        if contact["name"] == name:
            contact["followup_calendar_event_id"] = None
            found = True
            break
    if not found:
        print(f"No contact named '{name}'", file=sys.stderr)
        sys.exit(1)
    save(data)
    print(f"Cleared followup_calendar_event_id for {name}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "recompute":
        cmd_recompute()
    elif cmd == "set-event-id":
        cmd_set_event_id(sys.argv[2], sys.argv[3], sys.argv[4])
    elif cmd == "clear-followup-event-id":
        cmd_clear_followup_event_id(sys.argv[2])
    else:
        print(f"Unknown command: {cmd}", file=sys.stderr)
        sys.exit(1)
