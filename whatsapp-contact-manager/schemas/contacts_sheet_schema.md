# Google Sheet Schema — `Contacts`

Create a Google Sheet with a single tab named **`Contacts`** and these columns in row 1 (exact header names matter — the workflows reference them). `schemas/contacts_template.csv` has this header row ready to import.

| Column | Type | Set by | Notes |
|---|---|---|---|
| `name` | text | you | Full name. Used as the unique key — must be unique per contact. |
| `phone` | text | you | E.164 format, e.g. `+2348012345678`. For your reference only — the system never messages contacts directly. |
| `email` | text | you | |
| `birthday` | date (`YYYY-MM-DD`) | you | Year can be a placeholder (e.g. `1900-04-15`) if you only know month/day. |
| `education` | text | you | |
| `work` | text | you | Current role / employer / position. |
| `relationship_category` | select | you | One of: `New Contact`, `Close Friend`, `Family`, `Professional`, `Mentor`, `Acquaintance` |
| `priority` | select | you | `High`, `Medium`, `Low` — how much you want to invest in this relationship |
| `busy_level` | select | you | `Very Busy`, `Moderate`, `Flexible` |
| `relationship_goal` | text | you | Free text, e.g. "Explore co-counsel opportunities", "Stay close" |
| `notes` | text | system (CM-03) | Running log of discussion notes, newest first, date-stamped |
| `last_contacted_date` | date | system (CM-03) | Set automatically each time you log an interaction |
| `next_follow_up_date` | date | system | Auto-computed from cadence rules |
| `cadence_days` | number | system | Auto-computed follow-up interval |
| `relationship_plan_note` | text | system | Auto-generated suggested approach for this contact |
| `next_birthday_date` | date | system | Auto-computed next occurrence of their birthday |
| `birthday_synced` | `true`/`false` | system | Internal flag — prevents duplicate birthday calendar events |
| `followup_event_created` | `true`/`false` | system | Internal flag — prevents duplicate follow-up calendar events |
| `status` | select | you | `Active` (default) or `Paused` — paused contacts are skipped by reminders |

You only need to fill in the "you" columns for each contact; the "system" columns are written automatically by the workflows and can start blank.
