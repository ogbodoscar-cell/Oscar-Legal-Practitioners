# Testing Guide — Oscar Legal Practitioners

## Overview

This guide provides sample payloads, multi-agent scenarios, failure simulations, and duplicate input tests.

---

## Test Environment Setup

Use **Postman** or **curl** to send test payloads to WF-01's web webhook:

```
POST https://your-n8n-instance.com/webhook/intake-web
Headers:
  Content-Type: application/json
  X-Oscar-Secret: your-webhook-secret
```

---

## Test 1: Plain Text Matter (Litigation)

**Scenario:** Lawyer sends a text message describing a new court matter.

```json
{
  "body": {
    "sender": "+2348012345678",
    "channel": "web",
    "content": "Client (Claimant, an SME) is being sued for breach of a supply contract by their supplier (Defendant). Contract value is N5 million. Hearing is 15 March 2026 at the Federal High Court Lagos. We need to file a Statement of Defence. Urgency is high.",
    "file_url": ""
  }
}
```

**Expected Flow:** WF-01 → Text cleanup → GPT-4o classifies as `litigation`, `high` urgency → WF-02 generates `LP/2026/001` → WF-03 dispatches Research + Drafting → Research brief generated → Statement of Defence drafted → WF-07 sends review via web/WhatsApp.

---

## Test 2: WhatsApp Voice Note (Transcription Path)

**Scenario:** Lawyer sends a voice note via WhatsApp.

Simulated Twilio payload (POST to `/webhook/intake-whatsapp`):
```json
{
  "From": "whatsapp:+2348099887766",
  "To": "whatsapp:+14155238886",
  "Body": "",
  "MediaUrl0": "https://api.twilio.com/2010-04-01/Accounts/ACxxx/Messages/MMxxx/Media/ME123",
  "MediaContentType0": "audio/ogg",
  "NumMedia": "1"
}
```

**Expected Flow:** WF-01 detects `media_type = voice` → OpenAI Whisper transcription → If Whisper fails: Google STT fallback → Clean text → Classification → Orchestrator

---

## Test 3: PDF Document Upload (OCR Path)

**Scenario:** Lawyer uploads a scanned court document via web.

```json
{
  "body": {
    "sender": "lawyer@oscarlegalpractitioners.ng",
    "channel": "email",
    "content": "",
    "file_url": "https://drive.google.com/file/d/xxx/view",
    "file_type": "application/pdf",
    "file_name": "CourtOrder_March2026.pdf"
  }
}
```

**Expected Flow:** WF-01 detects `media_type = pdf` → n8n OCR node extracts text → Text cleanup → Classification (likely `research` or `drafting`) → Orchestrator

---

## Test 4: Duplicate Input Simulation

**Scenario:** Same payload sent twice within minutes.

Send **Test 1 payload twice** in quick succession.

**Expected Behaviour:**
- First run: creates `LP/2026/001`, processes normally
- Second run: WF-02 Pinecone query returns cosine similarity > 0.88 → detected as existing matter `LP/2026/001` → updates existing Airtable record, does NOT create a new Matter ID → forwards to Orchestrator with existing matter context

**Verify in Airtable Matters:** Only one record for this matter, `last_activity` updated on second run.

---

## Test 5: Multi-Agent Scenario (Research + Drafting together)

**Scenario:** Complex matter requiring both research and a draft document.

```json
{
  "body": {
    "sender": "+2348055443322",
    "channel": "web",
    "content": "Client (Applicant) was dismissed from employment without due process — no query, no hearing, summary dismissal. Client worked for 7 years. We need to (1) research wrongful dismissal law and relevant cases in Nigeria, and (2) draft a demand letter to the former employer.",
    "file_url": ""
  }
}
```

**Expected Flow:** Orchestrator dispatches BOTH `research` AND `drafting` agents → Research Agent searches LawPavilion + web for Nigerian employment law + wrongful dismissal precedents → Drafting Agent simultaneously prepares a demand letter → Both outputs merged → WF-07 sends consolidated review to lawyer.

---

## Test 6: Clarification Request

**Scenario:** Ambiguous input that the Orchestrator cannot complete without clarification.

```json
{
  "body": {
    "sender": "+2348077123456",
    "channel": "whatsapp",
    "content": "Handle the land matter for me",
    "file_url": ""
  }
}
```

**Expected Flow:** Orchestrator identifies insufficient facts → `clarifications_needed` array is non-empty → WF-07 sends clarification questions to WhatsApp: e.g. "1. What is the nature of the land dispute? 2. Who are the parties involved? 3. What urgency?" → System waits for reply → On reply, loops back to Orchestrator with enriched context.

---

## Test 7: Failure Simulation — OCR Timeout

**Scenario:** Simulate an OCR failure.

Temporarily disable the OCR node inside WF-01, then send Test 3 payload.

**Expected Behaviour:** n8n catches the error via the error handler → Lawyer receives WhatsApp/Email notification: "⚠️ Oscar Legal: We could not process your document. Please resend or contact the office." → Agent Log records `status = failed`, `error_message = OCR_TIMEOUT`.

**Verify:** Airtable `Agent Logs` table has a `failed` record for this execution.

---

## Test 8: CRM Agent Standalone (Weekly Newsletter)

**Scenario:** Test the weekly CRON-triggered newsletter generation.

**Manual trigger:** In n8n, open WF-06, click the `Weekly Newsletter Trigger (CRON)` node, click **Execute Node** (runs that node only, triggering the rest of the workflow manually).

**Expected Flow:** Fetches active clients from Airtable → Gemini generates segmented newsletter content → Saves to Google Drive CRM folder → Returns to WF-07 for lawyer approval before any sending.

**Verify:** New file in Google Drive `CRM_Content/` folder, new record in Airtable `Agent Logs`.

---

## Test 9: Approval Flow — APPROVE

After any test that reaches WF-07:

**WhatsApp:** Reply `APPROVE` to the review message from the system.

**Expected Flow:** WF-07 Wait node resumes → Parser detects "APPROVE" → Airtable `Approvals` record created with `decision = approved` → Draft status updated in `Drafts` table → Approved output embedded into Pinecone `approved` namespace.

---

## Test 10: Approval Flow — REVISE

Reply `REVISE: Please add a prayer for costs and change the tone to be more formal.`

**Expected Flow:** Parser detects "REVISE" prefix → Extracts revision notes → Loops back to WF-03 Orchestrator with `is_revision = true` and revision feedback → Orchestrator re-runs drafting with the feedback → New draft version generated → Sent back for approval.

---

## Verification Checklist

After completing all tests:

- [ ] All 10 test flows executed without unhandled crashes
- [ ] Airtable `Matters` table has correct matter IDs in `LP/YYYY/NNN` format
- [ ] No duplicate matter IDs created for identical inputs
- [ ] Airtable `Agent Logs` has entries for every workflow execution
- [ ] Google Drive `Matters/` folder has sub-folders for each new matter
- [ ] Google Drive `CRM_Content/` has at least one newsletter draft
- [ ] Airtable `Drafts` table has records for each draft produced
- [ ] Airtable `Approvals` table has approved and revision records
- [ ] Pinecone `approved` namespace has vectors for approved outputs
- [ ] PII (real names, emails, phone numbers) does NOT appear in Pinecone vector metadata
- [ ] All WhatsApp/Telegram/Email messages are only sent to the lawyer, never to clients
