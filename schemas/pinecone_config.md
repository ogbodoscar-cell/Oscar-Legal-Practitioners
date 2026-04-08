# Pinecone Index Configuration — Oscar Legal Practitioners

## Index Name: `oscar-legal-memory`

| Setting | Value |
|---|---|
| **Index Name** | `oscar-legal-memory` |
| **Dimensions** | `1536` (OpenAI `text-embedding-3-small`) |
| **Metric** | `cosine` |
| **Cloud** | `aws` (or `gcp` — choose closest to your region) |
| **Region** | `us-east-1` (or `eu-west-1` for GDPR considerations) |
| **Pod Type** | `p1.x1` (starter) → scale to `p2.x2` in production |

---

## Namespaces

Pinecone namespaces act as logical partitions within the index. All namespaces share the same vector dimensions.

| Namespace | Contents | Populated By |
|---|---|---|
| `matters` | Embeddings of all intake summaries (one per interaction per matter) | WF-02 |
| `research` | Embeddings of research briefs and findings | WF-04 |
| `drafts` | Embeddings of approved draft documents | WF-07 (on approval) |
| `approved` | Embeddings of all fully approved outputs | WF-07 |

---

## Metadata Schema (per vector)

All vectors stored in Pinecone MUST include the following metadata fields. This enables filtered retrieval by matter, type, or date — which powers the Orchestrator's memory retrieval.

```json
{
  "matter_id":     "LP/2026/001",
  "content_type":  "intake | research_brief | draft | approved_output | clarification",
  "intent":        "litigation | drafting | research | client_communication | ...",
  "channel":       "whatsapp | telegram | email | web",
  "date":          "2026-02-19T10:00:00.000Z",
  "version":       "v1.0-2026-02-19",
  "lawyer_id":     "LAWYER-001",
  "content_hash":  "sha256-hex-string"
}
```

---

## Similarity Thresholds

| Use Case | Threshold | Workflow |
|---|---|---|
| Existing matter detection | `>= 0.88` | WF-02 |
| Related research retrieval | `>= 0.75` | WF-04 |
| Historical context retrieval | `>= 0.70` | WF-02 (history) |
| Duplicate input detection | `>= 0.95` (same content_hash preferred) | WF-01 |

---

## Setup Steps

1. **Create** a Pinecone account at [pinecone.io](https://pinecone.io)
2. **Create** a new index named `oscar-legal-memory` with the settings above
3. **Retrieve** your API key from the Pinecone console
4. **Set** environment variables (see `credentials_checklist.md`):
   - `PINECONE_API_KEY`
   - `PINECONE_INDEX` = `oscar-legal-memory`
   - `PINECONE_PROJECT` = your project ID
   - `PINECONE_ENVIRONMENT` = e.g. `us-east-1-aws`

5. **Create** namespaces lazily — they are created automatically on first upsert in n8n.

---

## Embedding Model

| Setting | Value |
|---|---|
| Model | `text-embedding-3-small` (OpenAI) |
| Dimensions | 1536 |
| Cost | ~$0.02 per 1M tokens |
| API Node in n8n | OpenAI → Embedding → model: `text-embedding-3-small` |

> **Note:** If you switch to a different embedding model in future, you must re-embed all existing vectors — the dimensions must match. Keep a record of which model was used.

---

## Data Lifecycle Policy

| Data Type | Retention | Deletion Trigger |
|---|---|---|
| Intake summaries (`matters` namespace) | Permanent | Manual delete by lawyer |
| Research briefs (`research` namespace) | Permanent | Manual delete by lawyer |
| Draft embeddings (`drafts` namespace) | Permanent unless superseded | New version approval |
| Approved outputs (`approved` namespace) | Permanent | Manual delete only |
| Temporary processing data | Not stored in Pinecone | Never reaches Pinecone |
