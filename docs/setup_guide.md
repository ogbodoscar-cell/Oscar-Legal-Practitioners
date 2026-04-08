# Setup Guide — Oscar Legal Practitioners n8n System

## Prerequisites
- n8n instance (self-hosted or n8n Cloud)
- All API credentials from `docs/credentials_checklist.md`
- Airtable base configured per `schemas/airtable_schema.md`
- Pinecone index configured per `schemas/pinecone_config.md`

---

## Step 1: Import Workflows

Import workflows in this exact order to preserve webhook dependencies:

1. Go to **n8n → Workflows → Import from File**
2. Import in this sequence:
   1. `WF-07_Approval_Delivery.json` ← import first (other workflows call this)
   2. `WF-04_Research_Agent.json`
   3. `WF-05_Drafting_Agent.json`
   4. `WF-06_CRM_Agent.json`
   5. `WF-03_Orchestrator.json`
   6. `WF-02_Matter_Memory.json`
   7. `WF-01_Unified_Intake.json` ← activate last

---

## Step 2: Set Credentials

For each imported workflow:
1. Open the workflow
2. Click any node with a credential error (marked in red)
3. Select or create the correct credential from the dropdown
4. Save and close

Refer to `docs/credentials_checklist.md` for the exact credential names.

---

## Step 3: Set Environment Variables

In your n8n instance, set all variables from `docs/credentials_checklist.md`. If self-hosted:

```bash
# Add to your n8n .env file or Docker environment
N8N_WEBHOOK_BASE_URL=https://your-n8n-instance.com
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_WHATSAPP_FROM=+14155238886
AIRTABLE_BASE_ID=appXXXXXXXXXXXXXX
GOOGLE_DRIVE_ID=My Drive
GOOGLE_DRIVE_MATTERS_FOLDER_ID=1AbCdEf...
GOOGLE_DRIVE_CRM_FOLDER_ID=1XyZ123...
PINECONE_API_KEY=pcsk_2kuRCF_Jw6CA79SuXvqLbVwcUuKyXnPxAzMEsrHR8zsDtRiaMpCW3NpMBaoX2rVZLB52tC
PINECONE_INDEX=oscar-legal-memory
PINECONE_PROJECT=your-project-id
PINECONE_ENVIRONMENT=us-east-1-aws
TAVILY_API_KEY=tvly-XXXXXXXXXX
FIRM_EMAIL_FROM=noreply@oscarlegalpractitioners.ng
DEFAULT_LAWYER_ID=LAWYER-001
```

---

## Step 4: Configure Webhook Security

For **each webhook trigger node** across all workflows:
1. Open the node settings
2. Set **Authentication** = `Header Auth`
3. Set **Header Name** = `X-Oscar-Secret`
4. Set **Header Value** = your chosen secret key
5. Update Twilio, Telegram, and your frontend to send this header on all requests

---

## Step 5: Configure Twilio WhatsApp Webhook

In Twilio Console → Messaging → WhatsApp Sandbox (or Business API):
```
Webhook URL: https://your-n8n-instance.com/webhook/intake-whatsapp
HTTP Method: POST
```

---

## Step 6: Configure Telegram Webhook

Run this URL in your browser (replace with your bot token):
```
https://api.telegram.org/bot{YOUR_TELEGRAM_BOT_TOKEN}/setWebhook?url=https://your-n8n-instance.com/webhook/...
```

Note: For Telegram, activate the **Telegram Trigger** node inside WF-01 — it self-registers the webhook when activated.

---

## Step 7: Create Google Drive Folder Structure

Manually create this structure in Google Drive:
```
Oscar Legal Practitioners/
├── Matters/          ← Set this folder ID as GOOGLE_DRIVE_MATTERS_FOLDER_ID
└── CRM_Content/      ← Set this folder ID as GOOGLE_DRIVE_CRM_FOLDER_ID
```

---

## Step 8: Activate Workflows

Activate in this order:
1. WF-07 (Approval & Delivery)
2. WF-04, WF-05, WF-06 (Specialist Agents)
3. WF-03 (Orchestrator)
4. WF-02 (Matter Memory)
5. **WF-01 (Unified Intake) — activate last** ← this opens the system to input

---

## Step 9: Using the Approval Loop
The system is designed for "Human-in-the-Loop" legal practice:
- **WhatsApp/Telegram/Email**: You will receive a preview of all agent outputs (Research, Drafts, CRM).
- **To Approve**: Reply with **APPROVE**. The system will finalize the matter and store the output in memory.
```markdown
- **To Revise (Direct Edit)**: Open the Google Drive link, edit the document directly, and then reply with **APPROVE**. The system will finalize the version currently saved in Drive.
```
- **To Reject**: Reply with **REJECT [reason]**. The system will loop back to the Orchestrator, which will analyze your reason and attempt a completely different legal strategy.

---

## Step 10: Test with Sample Payloads
See `docs/testing_guide.md` for full test scenarios and sample payloads.

---

## Monitoring

- View execution history: **n8n → Executions**
- Filter by workflow name to see per-workflow logs
- Check Airtable `Agent Logs` table for agent decision audit trail
- Check Airtable `Approvals` table for all lawyer approval decisions
