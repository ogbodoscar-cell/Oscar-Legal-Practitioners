# Oscar Legal Practitioners — AI Virtual Legal Practice Assistant

> **Nigeria-First AI Legal Practice Automation System**
> Built on n8n | GPT-4o | Google Gemini | Pinecone | Airtable | Google Drive | Twilio

---

## What This System Does

Oscar Legal Practitioners is a modular, n8n-orchestrated AI automation platform for Nigerian lawyers. It converts unstructured legal inputs — voice notes, scanned court documents, WhatsApp messages, emails — into structured legal work products, with mandatory lawyer approval before anything leaves the system.

**It functions as a junior-to-senior associate hybrid. It never replaces lawyer judgment.**

---

## Architecture

```
[Lawyer Input: WhatsApp / Telegram / Email / Web]
        ↓
  WF-01: Unified Intake & Preprocessing
  (OCR / Whisper Transcription / Classification)
        ↓
  WF-02: Matter Memory
  (Matter ID: LP/YYYY/NNN, Pinecone, Airtable, Google Drive)
        ↓
  WF-03: Orchestrator Engine
  (GPT-4o Senior Barrister — Legal Strategy & Agent Dispatch)
    ↙       ↓        ↘
WF-04     WF-05     WF-06
Research  Drafting   CRM
Agent     Agent      Agent (Gemini)
    ↘       ↓        ↙
  WF-07: Approval & Delivery
  (Channel-mirrored gate: APPROVE / REVISE / REJECT)
        ↓ (on APPROVE)
[Google Drive + Airtable + Pinecone Storage]
```

---

## Workflow Files

| File | Workflow | Purpose |
|---|---|---|
| `WF-01_Unified_Intake.json` | Unified Intake | All channels → OCR/Transcription → Classification |
| `WF-02_Matter_Memory.json` | Matter Memory | ID gen, Pinecone embed, Airtable, Drive |
| `WF-03_Orchestrator.json` | Orchestrator Engine | Legal reasoning, agent dispatch |
| `WF-04_Research_Agent.json` | Research Agent | LawPavilion + web + internal memory |
| `WF-05_Drafting_Agent.json` | Drafting Agent | GPT-4o Nigerian legal drafter + PII masking |
| `WF-06_CRM_Agent.json` | CRM Agent | Gemini newsletters, engagement letters |
| `WF-07_Approval_Delivery.json` | Approval & Delivery | Channel-mirrored gate + Pinecone storage |

---

## Key Design Decisions

| Decision | Implementation |
|---|---|
| **LLM Strategy** | GPT-4o (analysis/drafting) + Gemini (client comms) |
| **Matter ID** | `LP/YYYY/NNN` auto-generated, lawyer override allowed |
| **Primary Store** | Pinecone (vector master) |
| **Drive Role** | Ingestion pipeline & document storage |
| **Approval Gate** | Mirrors input channel (WhatsApp→WhatsApp, Email→Email) |
| **Orchestrator Depth** | Deep legal reasoning + strategy suggestions |
| **PII Protection** | Tokenised before any LLM call, restored on output |
| **No Autonomous Client Messaging** | Every output requires lawyer APPROVE reply |

---

## Quick Start

1. Read `docs/credentials_checklist.md` → set up all API accounts
2. Configure Airtable per `schemas/airtable_schema.md`
3. Create Pinecone index per `schemas/pinecone_config.md`
4. Follow `docs/setup_guide.md` to import and activate workflows
5. Run tests per `docs/testing_guide.md`

---

## Security & Ethics

- ✅ No raw client PII ever sent to AI models — tokenised internally
- ✅ All API keys in n8n Credentials Vault only
- ✅ All webhooks protected with header authentication
- ✅ Approval gate mandatory — no autonomous output delivery
- ✅ All drafts watermarked: "DRAFT — SUBJECT TO SOLICITOR REVIEW"
- ✅ Inferences by AI always labelled `[INFERENCE: ...]`
- ✅ Agent decision audit trail in Airtable `Agent Logs`
- ✅ Nigerian legal ethics principles embedded in system prompts

---

## Future Expansion (Post-MVP)

- [ ] Multi-lawyer role-based access
- [ ] Voice summary outputs from research briefs
- [ ] Client onboarding self-service portal
- [ ] NigeriaLII direct API integration
- [ ] WhatsApp voice reply for approval
- [ ] Matter analytics dashboard
- [ ] Conflict of interest checker

---

*Oscar Legal Practitioners — Built for Nigerian Legal Practice Excellence*
