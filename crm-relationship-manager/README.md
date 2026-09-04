# Relationship Ledger — Claude-native Personal CRM

A personal relationship-management system that lives partly as code in this repo, and partly as a dashboard Artifact in your Claude workspace. There's no server and no separate app — **Claude is the runtime**: it reads your contact data, talks to Google Calendar, sends your WhatsApp reminders, and republishes the dashboard, on a schedule or whenever you ask.

It never messages your contacts. Every WhatsApp message goes to **you**.

---

## Why this looks different from a normal app

Claude Artifacts render in a locked-down sandbox — no outbound network calls of any kind. So the dashboard can't fetch live data itself; it's a **snapshot** that Claude regenerates and republishes. Google Drive also only lets Claude *read* a Google Sheet, not write cells back into one — so a Sheet can't be the live, continuously-updated database either.

That shapes the design:

| Piece | What it is | Why |
|---|---|---|
| `data/contacts.json` | The live database | The one thing in this whole system Claude can both read *and* write reliably |
| Google Calendar | Live, two-way | Claude's Calendar connector has real create/update/delete — birthdays and follow-ups are genuine calendar events, not simulated ones |
| Google Sheet (optional) | One-time/occasional import source | You can keep maintaining contacts in a Sheet by hand and ask Claude to re-import it; it's never the automation's source of truth going forward |
| WhatsApp (CallMeBot) | Sent by Claude via a shell call | No native WhatsApp connector exists in Claude; CallMeBot is free and self-notification-only |
| `dashboard/dashboard.html` | A Claude Artifact | Static snapshot, rebuilt from `data/contacts.json` and republished each sync |

## How you use it

- **Log a conversation or a new contact**: just tell Claude in chat — "I talked to Jane today, she's raising a seed round" or "add a new contact, Tola, met her at the bar dinner, she's a judge's clerk." Claude runs `scripts/log_interaction.py`, creates/updates the Google Calendar follow-up reminder, and (if you like) confirms on WhatsApp.
- **See your dashboard**: ask Claude to "refresh my CRM" any time — it recomputes cadence, syncs Calendar, and republishes the Artifact with current data.
- **Weekly nudge**: every Sunday (once the Routine below is set up) Claude sends you a WhatsApp digest of who's due for a follow-up and whose birthday is coming up.
- **Birthdays**: once a contact has a `birthday` set, Claude creates a recurring yearly Google Calendar event for it automatically.

## How the relationship plan is decided

Rule-based, no paid AI calls: cadence is computed from `priority` (High/Medium/Low), `busy_level` (Very Busy/Moderate/Flexible), and `relationship_category` (New Contact/Close Friend/Family/Professional/Mentor/Acquaintance). See `scripts/cadence.py` — it's the single source of truth for this logic, imported by every other script, so tuning the numbers there updates everything downstream.

## Files

- `data/contacts.json` — the live contact database (currently seeded with 2 sample contacts — see `docs/setup_guide.md` to bring in your real list)
- `scripts/cadence.py` — the cadence/relationship-plan rules, shared by every script
- `scripts/sync.py` — recomputes cadence for all contacts, reports what needs a Calendar sync
- `scripts/log_interaction.py` — logs a conversation or adds a new contact (what Claude runs when you mention something in chat)
- `scripts/import_sheet.py` — one-time import from a CSV export of your Excel/Google Sheet
- `scripts/send_whatsapp_digest.py` — builds and sends the Sunday WhatsApp digest via CallMeBot
- `scripts/build_dashboard.py` — regenerates `dashboard/dashboard.html` from current data, ready to publish as an Artifact
- `dashboard/dashboard.html` — the dashboard itself (design notes are in a comment at the top of the file)
- `docs/setup_guide.md` — start here to go from sample data to your real network
