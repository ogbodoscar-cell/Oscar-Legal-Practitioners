# Credentials Checklist — Oscar Legal Practitioners

> **Security Rule:** ALL credentials must be stored exclusively in **n8n's built-in Credentials Vault**. Never hard-code keys in workflow nodes. Never put keys in `Set` or `Code` nodes. Use environment variables for all base URLs and IDs.

---

## n8n Credentials to Create

Go to: `n8n Settings → Credentials → Add Credential`

| Credential Name | Type in n8n | Service | Where Used |
|---|---|---|---|
| `OpenAI API` | OpenAI API | OpenAI | WF-01, WF-02, WF-03, WF-04, WF-05, WF-07 |
| `Google Gemini API` | Google PaLM API | Google AI Studio | WF-06 |
| `Twilio Basic Auth` | HTTP Basic Auth | Twilio | WF-01, WF-07 |
| `Telegram API` | Telegram API | Telegram BotFather | WF-01, WF-07 |
| `Practice Email IMAP` | IMAP | Your email host | WF-01 |
| `Practice Email SMTP` | SMTP | Your email host | WF-07 |
| `Airtable API` | Airtable Token | Airtable | WF-02, WF-04, WF-05, WF-06, WF-07 |
| `Google Drive OAuth2` | Google Drive OAuth2 | Google Cloud Console | WF-02, WF-05, WF-06, WF-07 |
| `Google Docs OAuth2` | Google Docs OAuth2 | Google Cloud Console | WF-05 (research brief creation) |
| `Oscar Internal Secret` | HTTP Header Auth | Internal (n8n→n8n) | WF-04→WF-05, WF-05→WF-07 inter-workflow calls |
| `Pinecone API Key` | HTTP Header Auth | Pinecone | WF-02, WF-04, WF-07 |
| `Tavily API` | Tavily API | Tavily | WF-04 (web search tool) |
| `LawPavilion API Key` | HTTP Header Auth | LawPavilion | WF-04 |
| `Google STT API Key` | HTTP Header Auth | Google Cloud | WF-01 (fallback) |

---

## Environment Variables to Set

Go to: `n8n Settings → Environment Variables` (or set in `.env` if self-hosted)

| Variable Name | Example Value | Description |
|---|---|---|
| `N8N_WEBHOOK_BASE_URL` | `https://your-n8n-instance.com` | n8n instance base URL (no trailing slash) |
| `TWILIO_ACCOUNT_SID` | `ACxxxxxxxx...` | Twilio Account SID |
| `TWILIO_WHATSAPP_FROM` | `+14155238886` | Twilio WhatsApp sandbox/production number |
| `AIRTABLE_BASE_ID` | `appXXXXXXXXXXXXXX` | Airtable Base ID (from URL) |
| `GOOGLE_DRIVE_ID` | `My Drive` | Google Drive root reference |
| `GOOGLE_DRIVE_MATTERS_FOLDER_ID` | `1AbCdEf...` | Drive folder ID for all matters |
| `GOOGLE_DRIVE_CRM_FOLDER_ID` | `1XyZ123...` | Drive folder ID for CRM content |
| `PINECONE_API_KEY` | `xxxxxxxx-xxxx-...` | Pinecone API key |
| `PINECONE_INDEX` | `oscar-legal-memory` | Pinecone index name |
| `PINECONE_PROJECT` | `your-project-id` | Pinecone project ID |
| `PINECONE_ENVIRONMENT` | `us-east-1-aws` | Pinecone environment string |
| `TAVILY_API_KEY` | `tvly-XXXXXXXXXX` | Tavily web search API key |
| `LAWPAVILION_API_KEY` | `lp-XXXXXXXXXX` | LawPavilion legal database API key |
| `FIRM_EMAIL_FROM` | `noreply@oscarlegalpractitioners.ng` | Firm email for outbound comms |
| `DEFAULT_LAWYER_ID` | `LAWYER-001` | Default lawyer ID for new matters |

---

## Service Setup Checklist

### OpenAI
- [ ] Create account at [platform.openai.com](https://platform.openai.com)
- [ ] Generate API key with `model: gpt-4o` and `text-embedding-3-small` access
- [ ] Set billing limits to avoid runaway costs

### Google Gemini
- [ ] Enable Gemini API at [aistudio.google.com](https://aistudio.google.com)
- [ ] Generate API key
- [ ] Model: `gemini-1.5-pro-latest`

### Twilio WhatsApp
- [ ] Create Twilio account at [twilio.com](https://twilio.com)
- [ ] Set up WhatsApp Sandbox (testing) or apply for Business API (production)
- [ ] Configure webhook URL: `{N8N_WEBHOOK_BASE_URL}/webhook/intake-whatsapp`

### Telegram
- [ ] Create bot via [@BotFather](https://t.me/BotFather) on Telegram
- [ ] Set webhook: `https://api.telegram.org/bot{TOKEN}/setWebhook?url={N8N_WEBHOOK_BASE_URL}/webhook/...`

### Airtable
- [ ] Create base named `Oscar_Legal_Practitioners`
- [ ] Create all 5 tables per `airtable_schema.md`
- [ ] Generate Personal Access Token (PAT) with `data.records:read` and `data.records:write` scopes

### Google Drive, Google Docs & Google Cloud
- [ ] Create Google Cloud project
- [ ] Enable **Google Drive API**, **Google Docs API**, and **Google Speech-to-Text API**
- [ ] Create **two separate OAuth2 credentials** in n8n: one for Google Drive, one for Google Docs
- [ ] Create two Drive folders: `Matters` and `CRM_Content`
- [ ] **Note:** Research briefs from WF-04 will be created as Google Docs inside the matter's Drive folder

### Pinecone
- [ ] Create index per `pinecone_config.md`
- [ ] Note API key, project ID, and environment string

### LawPavilion / NigeriaLII
- [ ] Obtain API access from [lawpavilion.com](https://lawpavilion.com)
- [ ] Alternatively configure to use [Nigeria-law.org](https://nigeria-law.org) or [LawNigeria.com](https://lawnigeria.com) endpoints
- [ ] Update WF-04 HTTP Request URL with actual endpoint

### Tavily
- [ ] Create account at [tavily.com](https://tavily.com)
- [ ] Generate API key
- [ ] Free tier: 1,000 searches/month; upgrade for production

---

## Webhook Security

All webhook triggers in these workflows use **Header Authentication**. After importing workflows into n8n:

1. For each Webhook node: set `Authentication` = `Header Auth`
2. Set header name: `X-Oscar-Secret`
3. Set header value: a strong random secret (e.g. generate with `openssl rand -hex 32`)
4. Store this same secret in all systems that call the webhook (Twilio, Telegram webhook config, your frontend)
