"""Relationship cadence rules — shared by sync.py, log_interaction.py, and build_dashboard.py.

No paid AI calls are needed for this: cadence and the suggested approach are
derived from three fields you set per contact (priority, busy_level,
relationship_category). Edit the tables below to tune the logic; every script
that imports this module picks up the change immediately.
"""
from datetime import date, datetime, timedelta

BASE_DAYS = {"High": 30, "Medium": 60, "Low": 120}
BUSY_MULTIPLIER = {"Very Busy": 1.5, "Moderate": 1.0, "Flexible": 0.75}
NEW_CONTACT_CAP_DAYS = 14

APPROACH_NOTES = {
    "New Contact": "Reference how you met and something specific you discussed. Aim to convert this into a call or coffee within 30 days.",
    "Close Friend": "Casual, frequent check-ins are fine — suggest meeting in person when you can.",
    "Family": "Keep it personal and warm. Prioritize presence over frequency.",
    "Professional": "Lead with a genuine update, ask about their work, and add value (an article, an intro, an opportunity) before asking for anything.",
    "Mentor": "Come with a specific question or an update on advice they gave you. Respect their time — be concise.",
    "Acquaintance": "Low-pressure, occasional check-ins. A birthday message or a relevant share is enough to stay on their radar.",
}

CATEGORIES = ["New Contact", "Close Friend", "Family", "Professional", "Mentor", "Acquaintance"]
PRIORITIES = ["High", "Medium", "Low"]
BUSY_LEVELS = ["Very Busy", "Moderate", "Flexible"]


def _parse_date(value):
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


def round_to_week(days):
    return max(7, round(days / 7) * 7)


def compute_cadence_days(priority, busy_level, category):
    base = BASE_DAYS.get(priority, 60)
    multiplier = BUSY_MULTIPLIER.get(busy_level, 1.0)
    cadence = base * multiplier
    if category == "New Contact":
        cadence = min(cadence, NEW_CONTACT_CAP_DAYS)
    return round_to_week(cadence)


def approach_note(category):
    return APPROACH_NOTES.get(category, APPROACH_NOTES["Acquaintance"])


def next_birthday(birthday_str, today=None):
    b = _parse_date(birthday_str)
    if not b:
        return None
    today = today or date.today()
    candidate = date(today.year, b.month, b.day)
    if candidate < today:
        candidate = date(today.year + 1, b.month, b.day)
    return candidate


def recompute_contact(contact, today=None):
    """Returns a new dict with cadence_days, next_follow_up_date,
    relationship_plan_note, and next_birthday_date recomputed in place.
    Does not touch last_contacted_date, notes, or the synced flags."""
    today = today or date.today()
    priority = contact.get("priority", "Medium")
    busy_level = contact.get("busy_level", "Moderate")
    category = contact.get("relationship_category", "Acquaintance")

    cadence_days = compute_cadence_days(priority, busy_level, category)
    last_contacted = _parse_date(contact.get("last_contacted_date")) or today
    next_follow_up = last_contacted + timedelta(days=cadence_days)

    updated = dict(contact)
    updated["cadence_days"] = cadence_days
    updated["next_follow_up_date"] = next_follow_up.isoformat()
    updated["relationship_plan_note"] = (
        f"Suggested cadence: every {cadence_days} days. {approach_note(category)}"
    )
    nb = next_birthday(contact.get("birthday"), today=today)
    updated["next_birthday_date"] = nb.isoformat() if nb else ""
    return updated
