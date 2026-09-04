#!/usr/bin/env python3
"""One-time (or repeatable) import of your Excel/Google Sheet contact export into contacts.json.

Google Drive lets Claude *read* a Sheet but has no tool to write cells back
into one, so the Sheet can't be the live database. This script is how your
existing contact list gets folded in: export/copy it to CSV, then run this.
Existing contacts (matched by name, case-insensitive) keep their cadence
history (last_contacted_date, notes, calendar event IDs); only the static
fields present in the CSV are overwritten. New names become new contacts
with sensible defaults.

Usage:
  python3 import_sheet.py contacts_export.csv

Recognized headers (case-insensitive, common variants accepted):
  name | full name
  phone | phone number
  email
  birthday | dob | date of birth
  education
  work | occupation | job | position
"""
import csv
import json
import sys
from pathlib import Path

DATA_PATH = Path(__file__).parent.parent / "data" / "contacts.json"

HEADER_ALIASES = {
    "name": "name", "full name": "name",
    "phone": "phone", "phone number": "phone",
    "email": "email",
    "birthday": "birthday", "dob": "birthday", "date of birth": "birthday",
    "education": "education",
    "work": "work", "occupation": "work", "job": "work", "position": "work",
    "relationship_category": "relationship_category", "category": "relationship_category",
    "priority": "priority",
    "busy_level": "busy_level", "busy": "busy_level",
    "relationship_goal": "relationship_goal", "goal": "relationship_goal",
}


def normalize_row(row):
    out = {}
    for key, value in row.items():
        if key is None:
            continue
        norm_key = HEADER_ALIASES.get(key.strip().lower())
        if norm_key and value:
            out[norm_key] = value.strip()
    return out


def load():
    with open(DATA_PATH) as f:
        return json.load(f)


def save(data):
    with open(DATA_PATH, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)

    csv_path = sys.argv[1]
    data = load()
    by_name = {c["name"].strip().lower(): c for c in data["contacts"]}

    added, updated_count = 0, 0
    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for raw_row in reader:
            row = normalize_row(raw_row)
            if not row.get("name"):
                continue
            key = row["name"].strip().lower()
            if key in by_name:
                by_name[key].update(row)
                updated_count += 1
            else:
                contact = {
                    "name": row["name"],
                    "phone": row.get("phone", ""),
                    "email": row.get("email", ""),
                    "birthday": row.get("birthday", ""),
                    "education": row.get("education", ""),
                    "work": row.get("work", ""),
                    "relationship_category": row.get("relationship_category", "Acquaintance"),
                    "priority": row.get("priority", "Medium"),
                    "busy_level": row.get("busy_level", "Moderate"),
                    "relationship_goal": row.get("relationship_goal", ""),
                    "notes": [],
                    "last_contacted_date": None,
                    "birthday_calendar_event_id": None,
                    "followup_calendar_event_id": None,
                    "status": "Active",
                }
                by_name[key] = contact
                data["contacts"].append(contact)
                added += 1

    save(data)
    print(f"Imported: {added} new contacts, {updated_count} existing contacts refreshed.")
    print("Run `python3 sync.py recompute` next to compute cadence for the new contacts.")


if __name__ == "__main__":
    main()
