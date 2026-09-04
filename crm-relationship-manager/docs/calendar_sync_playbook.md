# Calendar sync playbook

This is the exact procedure Claude follows on each sync (manual, or when the daily Routine fires). It exists as a written playbook rather than a script because the Google Calendar connector is a Claude-native tool, not something a standalone script can call — Claude is the one holding the credentials.

## Steps

1. **Recompute cadence**: run `python3 scripts/sync.py recompute` from `crm-relationship-manager/`. Read its `pending_birthday_events` and `pending_followup_events` output.

2. **Create/update birthday events** — for each entry in `pending_birthday_events`:
   - Call `create_event` with:
     - `eventType: "BIRTHDAY"`, `allDay: true`
     - `startTime`: the contact's `next_birthday_date` at `T00:00:00Z`
     - `endTime`: the day *after* that, at `T00:00:00Z` (Calendar's all-day end date is exclusive)
     - `summary`: `🎂 {name}'s Birthday`
     - **Do not pass `description` or `overrideReminders`** — the `BIRTHDAY` event type rejects both (returns "invalid argument"). Calendar applies its own default reminders and a yearly `RRULE` automatically — no need to set recurrence either.
   - Record the returned event `id` with: `python3 scripts/sync.py set-event-id "{name}" birthday {event_id}`
   - Because birthdays recur automatically and are only created once (`birthday_calendar_event_id` gates it), this step is a no-op for anyone already synced.

3. **Create/update follow-up events** — for each entry in `pending_followup_events`:
   - If the contact already has a `followup_calendar_event_id` (a previous reminder that's now stale because the date moved), call `update_event` on that ID instead of creating a new one. Otherwise call `create_event`.
   - Regular `DEFAULT` event type. Fields:
     - `summary`: `🤝 Follow up with {name}`
     - `startTime` / `endTime`: `next_follow_up_date` at `09:00`–`09:30`, with `timeZone: "Africa/Lagos"` (adjust if the user's timezone changes)
     - `description`: the contact's `relationship_plan_note`, plus their most recent note if any
     - `overrideReminders`: `[{ method: "popup", minutes: 60 }]`
   - Record the event ID: `python3 scripts/sync.py set-event-id "{name}" followup {event_id}`

4. **Rebuild the dashboard**: run `python3 scripts/build_dashboard.py`, then republish `dashboard/dashboard.html` with the Artifact tool using the same file path (keeps the same URL live).

5. **Sunday only**: also run `python3 scripts/send_whatsapp_digest.py` to send the weekly WhatsApp nudge. Requires `CALLMEBOT_PHONE` / `CALLMEBOT_APIKEY` to already be set in `crm-relationship-manager/.env` — if missing, the script exits with a clear error rather than failing silently.

## Notes

- `data/contacts.json` is the only state that persists between syncs — the Calendar event IDs stored on each contact make every step above idempotent (safe to re-run daily without creating duplicate events).
- If a contact's `next_follow_up_date` changes between syncs (e.g. because you logged a new interaction), `sync.py recompute` detects the change and re-lists them under `pending_followup_events` even though `followup_calendar_event_id` is set — that's the update-vs-create signal in step 3. `log_interaction.py` also proactively clears `followup_calendar_event_id` to force this.
