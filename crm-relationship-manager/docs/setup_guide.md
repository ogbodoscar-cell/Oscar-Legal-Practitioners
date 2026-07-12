# Setup Guide — Relationship Ledger

This is a conversation with Claude, not a deploy checklist — everything below happens by asking Claude to do it. Two things are needed to go from the sample data currently in `data/contacts.json` to a live system:

## 1. Your contact list

Any of these works — tell Claude which you'd like:
- **Paste it** directly into the chat (name, phone, email, birthday, education, work — whatever columns you have).
- **Upload the Excel file** — Claude can read it directly.
- **Share a Google Sheet** — Claude can read it via the Drive connector (send the link or the file name and ask Claude to find it).

Claude will run `scripts/import_sheet.py` (or the equivalent for a pasted/uploaded list) to fold it into `data/contacts.json`, then `scripts/sync.py recompute` to work out each contact's follow-up cadence. New contacts default to `relationship_category: Acquaintance`, `priority: Medium`, `busy_level: Moderate` unless you specify otherwise — tell Claude if you want different defaults, or go through the list afterward and adjust anyone specific.

## 2. Your free CallMeBot key (for WhatsApp reminders)

1. Save this number to your phone: **+34 644 51 95 23**
2. Send it a WhatsApp message with exactly: `I allow callmebot to send me messages`
3. Wait for a reply with your personal API key.
4. Tell Claude your WhatsApp number and this key — Claude stores them in `crm-relationship-manager/.env` (already gitignored — this file is never committed).

If the number doesn't respond within ~10 minutes it's occasionally rate-limited; try again later.

## 3. Google Calendar

Nothing to set up — Claude already has a live Google Calendar connector in this workspace. Ask Claude to do a first sync once your contact list is in, and it will create the birthday and follow-up events directly.

## 4. Turning on the automatic schedule

Once 1 and 2 are done, ask Claude to set up the daily Routine (or confirm the one it already created). Each firing: recomputes cadence, creates/updates any pending Calendar events, refreshes the dashboard Artifact, and — on Sundays — sends the WhatsApp digest.

## Ongoing use

- **Log an interaction**: tell Claude about the conversation — it updates the contact, resets their follow-up clock, and creates the Calendar reminder.
- **Add someone new**: tell Claude the details as you'd tell a colleague — name, how you met, anything relevant. Claude fills in sensible defaults for anything you don't mention.
- **See the dashboard**: ask Claude to "show me my CRM" or "refresh my dashboard" any time.
- **Tune the cadence rules**: ask Claude to adjust `scripts/cadence.py` — e.g. "follow up with High priority contacts every 3 weeks instead of monthly."
- **Pause someone**: ask Claude to set their `status` to `Paused` — they're skipped by reminders and the weekly digest without deleting their record.
