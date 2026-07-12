# Setup Guide — Personal Network Manager

Everything here is free. Total time: ~30-45 minutes.

---

## Step 1: Get your free CallMeBot API key

CallMeBot sends WhatsApp messages to **your own number only** — it's not for messaging other people.

1. Save this number to your phone contacts: **+34 644 51 95 23**
2. Send it a WhatsApp message with exactly this text: `I allow callmebot to send me messages`
3. Wait for a reply containing your personal API key (usually within a minute or two).
4. Note down your **WhatsApp number** (international format, e.g. `+2348012345678`) and your **API key**.

If you don't get a reply within ~10 minutes, the service is occasionally rate-limited — retry later, or check `https://www.callmebot.com/blog/free-api-whatsapp-messages/` for current instructions (the exact contact number occasionally changes).

---

## Step 2: Create the Google Sheet

1. Create a new Google Sheet.
2. Rename the first tab to **`Contacts`**.
3. Import `schemas/contacts_template.csv` (File → Import → Upload → Replace current sheet) to get the header row + two sample contacts.
4. Open your Excel contact list and copy your real contacts in underneath the header, matching the columns described in `schemas/contacts_sheet_schema.md`. Only fill in: `name`, `phone`, `email`, `birthday`, `education`, `work`, `relationship_category`, `priority`, `busy_level`, `relationship_goal`. Leave the rest blank — the workflows fill them in.
5. Copy the Sheet's ID from its URL: `https://docs.google.com/spreadsheets/d/`**`THIS_PART`**`/edit`.

---

## Step 3: Set up n8n credentials

In your n8n instance (the same one used for the legal-practice system, or a separate free instance):

1. **Google Sheets OAuth2** — n8n Settings → Credentials → Add Credential → Google Sheets OAuth2 API. Follow the OAuth prompts (needs a Google Cloud project with the Sheets API enabled — same process as any n8n Google integration).
2. **Google Calendar OAuth2** — same process, Google Calendar API enabled on the same or a new Google Cloud project.
3. Environment variables (n8n Settings → Environment Variables, or your `.env` if self-hosted):

```
CALLMEBOT_PHONE=+2348012345678      # your WhatsApp number from Step 1
CALLMEBOT_APIKEY=123456              # your CallMeBot API key from Step 1
```

---

## Step 4: Import the workflows

Import in any order — they don't depend on each other:

1. `workflows/CM-01_Birthday_And_Followup_Sync.json`
2. `workflows/CM-02_Sunday_Network_Digest.json`
3. `workflows/CM-03_Log_Interaction_New_Contact.json`

For each imported workflow:
1. Open every **Google Sheets** node → set `documentId` to your Sheet's ID from Step 2, and select your `Google Sheets account` credential.
2. Open every **Google Calendar** node → select your `Google Calendar account` credential, and confirm the calendar (defaults to `primary`, i.e. your main calendar).
3. Save.

---

## Step 5: Activate and test

1. Activate all three workflows.
2. In **CM-01**, click "Execute Workflow" once manually — this seeds birthday events for every contact already in your sheet and creates the first round of follow-up reminders.
3. Open **CM-03**'s Form Trigger node and copy its form URL (also reachable any time from n8n → your production form URL). Bookmark it on your phone — this is how you'll log conversations and add new contacts going forward.
4. Submit a test entry through the form and confirm: the Sheet row appears/updates, a calendar event is created, and you get a WhatsApp confirmation.
5. CM-02 runs automatically every Sunday at 9am — you can also trigger it manually to preview the digest before Sunday.

---

## Ongoing use

- **New contact met**: fill out the CM-03 form (mark relationship category as `New Contact`) — it'll schedule your first follow-up within 2 weeks.
- **Had a conversation with someone**: fill out the CM-03 form with their name and discussion notes — cadence and next follow-up recompute automatically based on their priority/busy level/category.
- **Birthdays**: handled automatically by CM-01 once a contact has a `birthday` in the sheet — no action needed.
- **Weekly nudge**: CM-02 sends your Sunday digest automatically; no action needed.
- **Tuning the relationship logic**: edit the `BASE_DAYS`, `BUSY_MULTIPLIER`, and `APPROACH_NOTES` values inside the `Compute Cadence & Birthday` code node in CM-01 and CM-03 (keep both in sync).
