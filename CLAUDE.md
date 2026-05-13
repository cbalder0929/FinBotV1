# FINBOT.AI — Project Plan
> AI-powered bank & credit card statement analyzer  
> Stack: Python · Azure · Claude API · React (frontend)

---

## Current Status (as of 2026-05-07)

| Phase | Description | Status |
|---|---|---|
| 1 | UI Shell — two-column layout, robot animation | ✅ Done |
| 2 | Backend — file ingestion, PDF/CSV parsing | ✅ Done |
| 3 | Claude AI categorization end-to-end | ✅ Done |
| 4 | Results polish — flagging, export, animations | 🔧 In progress |
| 5 | Azure deployment | ⏳ Planned |
| 6 | Auth, trend charts, budget alerts | ⏳ Future |

---

## Project Overview

FinBot.AI is a two-column web application that accepts PDF and CSV bank/credit card statements, runs them through a three-tier categorization pipeline (rules → cache → Claude AI), and displays a rich breakdown of expenses by category, merchant, date, and amount. The robot mascot animates during processing to signal AI activity.

---

## Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| Frontend | React 18 + Vite 5 | Two-column UI, drag-drop, results panel |
| Styling | Tailwind CSS 3 | Navy blue theme, responsive layout |
| Animation | CSS SVG | Robot desk animation |
| Backend API | Python · FastAPI | File ingestion, Claude API orchestration |
| AI Engine | Anthropic Claude (`claude-sonnet-4-6`) | Statement categorization |
| PDF Parsing | pdfplumber | Extract text from bank statement PDFs |
| CSV Parsing | pandas | Parse tabular statement exports |
| Cloud Host | Azure App Service | Backend deployment (Phase 5) |
| Storage | Azure Blob Storage | Temp file storage (Phase 5) |
| Auth (future) | Azure AD B2C | User accounts for saved history |
| DB (future) | Azure Cosmos DB | Persist categorized transaction history |

---

## Repository Structure

```
AI_TaxPro/
├── frontend/                   # React + Vite app
│   ├── src/
│   │   ├── components/
│   │   │   ├── DropZone.jsx          # Drag-drop upload area
│   │   │   ├── FileQueue.jsx         # Per-file upload status badges
│   │   │   ├── RobotScene.jsx        # SVG robot + animation controller
│   │   │   ├── AnalyzeButton.jsx     # Analyze / Re-analyze button
│   │   │   ├── CategoryTabs.jsx      # Filter tabs per category
│   │   │   ├── SummaryCards.jsx      # Totals / stats row
│   │   │   └── TransactionTable.jsx  # Sortable, filterable expense table
│   │   ├── constants/
│   │   │   └── categories.js         # Single source of truth for category names/emojis
│   │   ├── data/
│   │   │   └── mockData.js           # computeSummary() utility + dev fixtures
│   │   ├── App.jsx                   # Main layout + state machine
│   │   └── main.jsx
│   ├── public/
│   ├── vite.config.js               # Dev proxy: /api/* → localhost:8000
│   ├── tailwind.config.js
│   └── package.json
│
├── backend/                    # FastAPI Python app
│   ├── app/
│   │   ├── main.py                   # FastAPI entry point + CORS + logging
│   │   ├── routes/
│   │   │   ├── upload.py             # POST /upload — parse PDF or CSV
│   │   │   └── analyze.py            # POST /analyze — categorize transactions
│   │   ├── services/
│   │   │   ├── pdf_parser.py         # pdfplumber + multi-pattern regex extraction
│   │   │   ├── csv_parser.py         # pandas + fuzzy column detection
│   │   │   ├── categorizer.py        # Rule-based patterns + emoji/merchant helpers
│   │   │   ├── category_cache.py     # Persistent JSON merchant cache
│   │   │   ├── claude_service.py     # Three-tier categorize + offline fallback
│   │   │   └── transaction_validation.py  # Anomaly flagging (2× category average)
│   │   └── models/
│   │       └── transaction.py        # RawTransaction + EnrichedTransaction (Pydantic)
│   ├── cache/                        # Auto-created; merchant_cache.json lives here
│   ├── requirements.txt
│   └── Dockerfile
│
├── CLAUDE.md                   # This file
├── .env.example
├── .gitignore
└── README.md
```

---

## Phase Breakdown

### Phase 1 — UI Shell ✅
**Goal:** Two-column interface with all visual states. No real AI yet.

- [x] Scaffold React + Vite project with Tailwind
- [x] Build left panel: drag-drop zone, file queue list
- [x] Build robot SVG animation (idle ↔ working states)
- [x] Build right panel: category tabs, summary cards, transaction table
- [x] Implement mock data flow: upload → animate → reveal results
- [x] Apply navy blue theme across all components
- [x] Font: JetBrains Mono (code elements) + Space Grotesk (UI copy)
- [x] Responsive layout (desktop-first, min 1200px)

---

### Phase 2 — Backend Foundation ✅
**Goal:** Real file ingestion and text extraction.

- [x] Initialize FastAPI project with CORS + logging
- [x] `POST /upload` — accept multiple PDF or CSV files (10 MB limit each)
- [x] PDF parser: multi-pattern regex (numeric dates, month-name dates, ISO dates)
- [x] CSV parser: fuzzy column detection, separated debit/credit, skip header rows
- [x] Return structured JSON: `[{ date, description, amount, balance, source_file }]`
- [x] Wire frontend upload to real `/upload` endpoint
- [x] Per-file upload status (queued → uploading → done/error) in FileQueue

---

### Phase 3 — Claude AI Categorization ✅
**Goal:** Claude reads transactions and categorizes them intelligently.

- [x] Set up Anthropic Python SDK (`claude-sonnet-4-6`)
- [x] Three-tier categorization to minimize API usage:
  - **Tier 1 — Rule-based:** ~150 merchant patterns matched locally, free
  - **Tier 2 — Persistent cache:** Claude's past results reused forever (JSON file)
  - **Tier 3 — Claude API:** Only called for genuinely new/unknown merchants
- [x] Graceful offline degradation when API key missing or credits exhausted
- [x] `?offline=true` query param to skip Claude entirely
- [x] Anomaly flagging: amounts > 2× category average get a ⚠️ badge
- [x] Per-file and per-request error messages surfaced to frontend
- [x] Backend structured logging (rules/cache/AI counts per request)

---

### Phase 4 — Results Display Polish 🔧
**Goal:** Rich, readable results panel.

- [x] Category filter tabs filter the transaction table live
- [x] Summary cards show real totals (total spent, # transactions, top category, flagged)
- [x] Each transaction row: date · merchant · category badge · amount · mini bar chart
- [x] Flagged logic: amounts > 2× category average get a ⚠️ badge (transaction_validation.py)
- [ ] Export button: download categorized data as CSV
- [ ] Smooth staggered animation on results reveal

---

### Phase 5 — Azure Deployment ⏳
**Goal:** Live hosted app.

- [ ] Dockerize FastAPI backend
- [ ] Deploy to Azure App Service (B1 tier to start)
- [ ] Azure Blob Storage for temp file uploads (auto-delete after 24h via lifecycle policy)
- [ ] Set environment variables: `ANTHROPIC_API_KEY`, Azure connection strings
- [ ] Deploy React frontend to Azure Static Web Apps
- [ ] Configure CORS between frontend and backend
- [ ] Add basic rate limiting (10 requests/min per IP)

---

### Phase 6 — Future Enhancements
- [ ] User auth via Azure AD B2C — save history across sessions
- [ ] Multi-month trend charts (Chart.js / D3)
- [ ] Budget alerts — set spending limits per category
- [ ] Support for more statement formats (Capital One, Wells Fargo)
- [ ] Mobile-responsive layout
- [ ] Side-by-side month comparison

---

## Claude API Strategy

### Three-Tier Pipeline (minimize API spend)

Every transaction passes through three tiers in order:

1. **Rule-based (`categorizer.py`)** — Regex patterns for ~150 known merchants. Free, instant. Anything that matches never reaches Claude.
2. **Cache (`category_cache.py`)** — Persistent JSON at `cache/merchant_cache.json`. Key = normalized first two words of description (digits/punctuation stripped). Free. Once Claude categorizes "STARBUCKS", every future Starbucks transaction is free.
3. **Claude API** — Only receives genuinely unseen descriptions. Result is immediately written back to the cache.

### Offline / Degraded Mode

When Claude is unavailable (no key, rate limit, credits exhausted):
- Auth/rate-limit errors → silently fall back to Tiers 1+2, unknown merchants tagged `Other / Unrecognized merchant`
- Force offline: `POST /analyze?offline=true`

### System Prompt Schema

```
Schema: [{ "merchant": str, "category": str, "subcategory": str|null, "note": str }]
```

Emoji and flagged are resolved locally after Claude responds — emoji from `CATEGORY_EMOJIS` lookup, flagged by `transaction_validation.apply_anomaly_flags()`.

### Batching

Up to 50 transactions per Claude API call. `analyze.py` loops in `BATCH_SIZE = 50` chunks.

---

## Environment Variables

```env
# backend/.env  (gitignored — never commit this file)
ANTHROPIC_API_KEY=sk-ant-...
AZURE_BLOB_CONNECTION_STRING=DefaultEndpointsProtocol=https;...   # Phase 5
AZURE_BLOB_CONTAINER=finbot-uploads                               # Phase 5
MAX_FILE_SIZE_MB=10
ALLOWED_ORIGINS=http://localhost:5173,https://finbot.yourdomain.com
```

---

## Key Dependencies

### Backend (`requirements.txt`)
```
fastapi>=0.136.1
uvicorn[standard]>=0.46.0
anthropic>=0.100.0
pdfplumber>=0.11.9
pandas>=3.0.2
python-multipart>=0.0.27
pydantic>=2.13.4
python-dotenv>=1.2.2
```

### Frontend (`package.json` key deps)
```json
{
  "react": "^18",
  "react-dom": "^18",
  "tailwindcss": "^3",
  "axios": "^1.6",
  "framer-motion": "^11"
}
```

---

## Development Notes

- **PDF layouts vary by bank.** The regex parser handles numeric, month-name, and ISO date formats. For exotic layouts, extend `_PATTERNS` in `pdf_parser.py`. A Claude-based PDF fallback is available via `claude_service.extract_transactions_from_pdf_text()` but removed from the upload route to save API calls — re-add it to `upload.py` if needed.
- **Expanding rule coverage.** Add merchant patterns to `categorizer.py` `RULES` list. More rules = fewer API calls. Each regex is a `(pattern, category)` tuple.
- **Cache reset.** Delete `backend/cache/merchant_cache.json` to clear all cached categorizations.
- **Privacy.** Never log raw transaction descriptions to external services. The backend logs counts and filenames only.
- **Anomaly flagging.** Implemented in `transaction_validation.py`. Requires at least 2 transactions in a category to establish an average; single-transaction categories are never flagged.
- **Model ID.** Use `claude-sonnet-4-6` (not `claude-sonnet-4`). Verify your account has access at console.anthropic.com.

---

*Last updated: 2026-05-07*
