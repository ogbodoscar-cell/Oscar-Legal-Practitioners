# Personal Network Manager — WhatsApp + Google Calendar

A free, standalone system for staying in touch with your personal/professional network. It is **not** part of the Oscar Legal Practitioners client-CRM system — it lives in this folder as its own self-contained project, reusing only the fact that you already run n8n.

It never messages your contacts. Every WhatsApp message it sends goes to **you** — it's a personal reminder system, not an outreach bot.

---

## What it does

1. **Imports your Excel contact list** (name, phone, email, birthday, education, work) into a Google Sheet that becomes the live database.
2. **Creates a recurring birthday event** in your Google Calendar for every contact, with reminders.
3. **Every Sunday**, sends you a WhatsApp digest of who's due for a follow-up this week, plus birthdays coming up in the next 7 days.
4. **Lets you log a conversation or a new contact** (via a simple web form), which:
   - Saves/updates the contact in your Google Sheet
   - Works out a suggested **follow-up cadence and relationship-building approach**, based on the contact's priority to you, how busy they are, and the type of relationship (new contact, professional, mentor, close friend, family, acquaintance)
   - Creates the next follow-up reminder directly in Google Calendar
   - Confirms back to you on WhatsApp

---

## Is the WhatsApp API paid or free?

| Option | Cost | Notes |
|---|---|---|
| **CallMeBot** (used here) | Free | Unofficial, built for exactly this use case (self-notifications). No business account. Modest rate limits; not for messaging other people. |
| Meta WhatsApp Cloud API (official, direct) | Free within a 24h reply window, paid outside it | Requires Meta Business verification — more setup than this personal use case needs. |
| Twilio (used elsewhere in this repo for client messaging) | Paid | Reliable and official, but adds cost for a system that only messages yourself. |
| Baileys / whatsapp-web.js (self-hosted) | Free | Automates your personal WhatsApp Web session. More capable but technically against WhatsApp's ToS — risk of a flagged number if used heavily. |

This system uses **CallMeBot** because it's free, requires no business account, and is designed for exactly this "notify myself" pattern. See `docs/setup_guide.md` for how to get your free API key.

---

## Architecture

```
Excel contacts  →  Google Sheet ("Contacts")  ←──────────────┐
                          │                                   │
        ┌─────────────────┼──────────────────┐                │
        ▼                 ▼                  ▼                │
  CM-01 (daily)     CM-02 (Sunday 9am)   CM-03 (on-demand form)│
  Sync birthdays &   Build & send        Log an interaction /  │
  follow-ups to      WhatsApp digest      add a new contact    │
  Google Calendar    via CallMeBot        → updates Sheet ─────┘
        │                                 → creates calendar reminder
        ▼                                 → sends WhatsApp confirmation
  Google Calendar
  (birthday + follow-up reminders,
   with native Calendar notifications)
```

All three pieces are plain n8n workflows (`workflows/CM-01…CM-03.json`) — free to run on a self-hosted n8n instance, same as the rest of your automation.

---

## How the relationship plan is decided (free, rule-based — no LLM needed)

No paid AI calls are required for the core system. Cadence is computed from three fields you set per contact:

| Priority | Base cadence |
|---|---|
| High | every 30 days |
| Medium | every 60 days |
| Low | every 120 days |

Adjusted by how busy they are (`Very Busy` ×1.5, `Moderate` ×1, `Flexible` ×0.75), and capped at 14 days for anyone tagged `New Contact` so you follow up quickly while the connection is fresh. Each relationship category (`Professional`, `Mentor`, `Close Friend`, `Family`, `Acquaintance`, `New Contact`) also gets a short suggested approach (e.g. "lead with a genuine update and add value before asking for anything" for `Professional`/`Mentor`). The exact rules are in the `Compute Cadence & Birthday` code node inside CM-01 and CM-03 — edit the numbers/text there any time.

If you later want richer, personalized plans (e.g. drafted opening lines per person), you can drop in an LLM node before the "Save to Contacts Sheet" step — but that's optional and out of scope for the free version.

---

## Files

- `workflows/CM-01_Birthday_And_Followup_Sync.json` — daily: syncs birthdays + creates follow-up calendar reminders
- `workflows/CM-02_Sunday_Network_Digest.json` — weekly: Sunday WhatsApp digest of who to reach out to
- `workflows/CM-03_Log_Interaction_New_Contact.json` — on-demand form: log a chat or add a new contact
- `schemas/contacts_sheet_schema.md` — Google Sheet column reference
- `schemas/contacts_template.csv` — starter sheet you can import your Excel data into
- `docs/setup_guide.md` — step-by-step setup, including the free CallMeBot API key

Start with `docs/setup_guide.md`.
