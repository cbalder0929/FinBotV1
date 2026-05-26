# 🤖 FinBot.AI

> **Your personal AI accountant — drop in a bank statement, get back a clear picture of where your money went.**

---

## 🤔 What Is This?

FinBot.AI is a web app that reads your bank or credit card statements and automatically sorts every transaction into categories like Food, Dining, Transport, Shopping, and more.

Instead of manually going through hundreds of rows in a spreadsheet, you just:

1. **Drop your statement** (PDF or CSV export from your bank) onto the page
2. **Click Analyze** — a robot mascot animates while AI reads your transactions
3. **See a clean breakdown** — category tabs, totals, and a flag on any unusually large charge

No spreadsheet skills needed. No manual tagging. Just drop and go.

---

## 💡 Why Was This Built?

Most people download their bank statements once a year (if ever), open a confusing PDF or CSV, and give up trying to make sense of it.

FinBot.AI was built to solve that frustration:

- **Too many transactions to sort by hand** → AI categorizes them all in seconds
- **PDFs are hard to search or filter** → the app turns them into a clean, interactive table
- **You don't know where your money goes** → category tabs and summary cards make it obvious at a glance
- **AI APIs can get expensive** → a smart three-tier pipeline makes sure Claude (the AI) is only called when it truly needs to be, keeping costs low

The goal is to make personal finance analysis feel effortless — even if you've never touched a spreadsheet in your life.

---

## 🔍 How Does It Work? (Plain English)

Here's the full journey from file upload to categorized results, explained without jargon:

### Step 1 — You upload a statement
You drag a PDF or CSV file onto the left side of the screen. The app supports exports from Chase, Bank of America, American Express, Wells Fargo, and most other banks.

### Step 2 — The backend reads the file
A Python server receives your file and extracts each transaction row — date, merchant name, and amount. It handles the messy formatting banks use (different date styles, combined debit/credit columns, etc.) automatically.

### Step 3 — Transactions get categorized (three ways, in order)

The app uses a clever three-step system to categorize transactions as cheaply and quickly as possible:

| Tier | Method | How it works |
|---|---|---|
| 1️⃣ | **Rule-based matching** | ~150 popular merchants (Starbucks, Amazon, Uber…) are already hard-coded. If your transaction matches one, it's categorized instantly — free, no AI needed. |
| 2️⃣ | **Memory cache** | If Claude AI has seen a merchant before, the answer is saved locally forever. Same merchant next time? Pulled from memory — free again. |
| 3️⃣ | **Claude AI** | Only completely new, unknown merchants get sent to Claude. The AI reads the merchant name and decides the best category. The result is saved to the cache so it never costs twice. |

This means after a couple of uses, almost everything is handled by tiers 1 and 2 — almost zero AI cost.

### Step 4 — Results appear on screen
The right side of the app fills in with:
- **Summary cards** — total spent, number of transactions, top category, flagged items
- **Category tabs** — click any tab (Food, Dining, Transport…) to filter the table
- **Transaction table** — sortable rows with date, merchant, category badge, and amount
- **⚠️ Flag** — any transaction more than 2× the average for its category gets flagged automatically

---

## 🏗️ How Was It Built?

FinBot.AI is split into two parts: a **frontend** (what you see) and a **backend** (the engine behind the scenes).

### Frontend — what you see and click
Built with **React** (a popular JavaScript library for building web UIs) and **Tailwind CSS** (for the navy blue styling). The robot animation is a hand-crafted SVG that switches between idle and working states.

### Backend — the engine
Built with **FastAPI** (a fast Python web framework). When you upload a file, it:
- Uses **pdfplumber** to extract text from PDFs
- Uses **pandas** to read and interpret CSV files
- Passes transactions through the three-tier categorization pipeline described above
- Calls the **Anthropic Claude API** only when necessary

### AI — the brain
[Claude](https://console.anthropic.com) by Anthropic is the AI model used for categorization. It's given a list of unknown merchant names and asked to return a category for each one. The model used is `claude-sonnet-4-6`.

### Cloud (coming soon)
The plan is to host the backend on **Azure App Service** and store uploaded files temporarily in **Azure Blob Storage** — automatically deleted after 24 hours for privacy.

---

## 🚀 Running It Locally (Step by Step)

Don't worry — you just need Python and Node.js installed. If you've run a project before with `npm install` or `pip install`, you're good.

### 1. Clone the project

```bash
git clone https://github.com/cbalder0929/FinBotV1.git
cd FinBotV1
```

### 2. Set up the backend (Python)

```bash
cd backend

# Create a virtual environment (a clean sandbox for Python packages)
python -m venv venv

# Activate it:
# Windows:
venv\Scripts\activate
# Mac / Linux:
source venv/bin/activate

# Install the required Python packages
pip install -r requirements.txt

# Copy the environment variable template
copy ..\\.env.example .env      # Windows
# cp ../.env.example .env       # Mac/Linux

# Open backend/.env and paste your Anthropic API key:
# ANTHROPIC_API_KEY=sk-ant-...

# Start the backend server
uvicorn app.main:app --reload
```

Backend is running at **http://localhost:8000**

### 3. Set up the frontend (React)

Open a **second terminal window**:

```bash
cd frontend
npm install       # download all the frontend packages
npm run dev       # start the development server
```

App is open at **http://localhost:5173**

---

## 🔑 Your API Key

The app needs an Anthropic API key to call Claude AI.

1. Go to [console.anthropic.com](https://console.anthropic.com) and sign up (free tier available)
2. Create an API key
3. Paste it into `backend/.env`:

```
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

> **No key? No problem.** The app still works without a key — it just uses the rule-based matching and cache for categorization. Unknown merchants will be labeled **Other** instead.

---

## 📂 Supported File Types

| Bank | PDF | CSV |
|---|---|---|
| Chase | ✓ | ✓ |
| Bank of America | ✓ | ✓ |
| American Express | ✓ | ✓ |
| Wells Fargo | ✓ | ✓ |
| Capital One | — | ✓ |
| Any standard export | — | ✓ |

**PDF** — must be a text-based PDF (the kind your bank emails you), not a scanned image.  
**CSV** — most bank "Export to CSV" downloads work automatically, no column renaming needed.

---

## 🏷️ Transaction Categories

| Emoji | Category | Example merchants |
|---|---|---|
| 🛒 | Food | Mariano's, Whole Foods, ALDI, Jewel, Costco |
| 🍔 | Dining | Portillo's, Starbucks, Chipotle, DoorDash, Uber Eats |
| 🚇 | Transport | Uber, Lyft, CTA Ventra, Amtrak, Shell, Chevron |
| 🌿 | Cannabis | Sunnyside, Zen Leaf, Cresco, Verilife |
| ⚡ | Utilities | ComEd, AT&T, Comcast, Nicor, T-Mobile |
| 🛍️ | Shopping | Amazon, Target, Walmart, Best Buy, Home Depot |
| 💊 | Health | CVS, Walgreens, hospital, dental, pharmacy |
| 🎮 | Entertainment | Netflix, Spotify, Steam, Ticketmaster, AMC |
| 💰 | Income | Direct deposit, payroll, Zelle received |
| 📦 | Other | Unrecognized merchants |

---

## ⚙️ Environment Variables

| Variable | Required | What it does |
|---|---|---|
| `ANTHROPIC_API_KEY` | Yes (for AI) | Your Claude API key from [console.anthropic.com](https://console.anthropic.com) |
| `MAX_FILE_SIZE_MB` | No | Max upload size per file in MB (default: `10`) |
| `ALLOWED_ORIGINS` | No | Comma-separated URLs allowed to call the API (for CORS) |
| `AZURE_BLOB_CONNECTION_STRING` | Phase 5 | Azure Storage connection string (not needed yet) |
| `AZURE_BLOB_CONTAINER` | Phase 5 | Blob container name (not needed yet) |

---

## 📁 Project Structure

```
FinBotV1/
├── frontend/              # Everything you see in the browser
│   └── src/
│       ├── components/        # UI pieces: upload zone, robot, results table, etc.
│       ├── constants/         # Category names and emoji definitions
│       └── data/              # Helper to compute summary totals
│
├── backend/               # The Python server
│   └── app/
│       ├── routes/            # API endpoints: /upload and /analyze
│       ├── services/          # PDF parser, CSV parser, AI categorizer, cache
│       └── models/            # Data shapes (what a transaction looks like)
│
├── .env.example           # Template for your environment variables
└── CLAUDE.md              # Full project plan and phase breakdown
```

---

## 🛠️ Tech Stack (for the curious)

| Layer | Tool | Why |
|---|---|---|
| Frontend UI | React 18 + Vite 5 | Fast, modern web UI framework |
| Styling | Tailwind CSS 3 | Utility-first CSS — easy navy blue theme |
| HTTP requests | Axios | Clean API calls from the frontend |
| Backend | Python + FastAPI | Fast, simple Python API framework |
| PDF reading | pdfplumber | Extracts text from bank PDF statements |
| CSV reading | pandas | Reads tabular data from CSV exports |
| AI | Anthropic Claude (`claude-sonnet-4-6`) | Categorizes unknown merchants |
| Cloud (soon) | Azure App Service + Blob Storage | Hosting and temp file storage |

---

## 📈 Development Status

| Phase | Description | Status |
|---|---|---|
| 1 | UI Shell — two-column layout, robot animation, mock data | ✅ Done |
| 2 | Backend — real file ingestion, PDF/CSV parsing | ✅ Done |
| 3 | Claude AI categorization, caching, offline fallback | ✅ Done |
| 4 | Results polish — CSV export, animations | 🔧 In progress |
| 5 | Azure deployment | ⏳ Planned |
| 6 | Auth, trend charts, budget alerts | ⏳ Future |

---

*Built with ☕ and a mild obsession with not having to manually sort bank statements ever again.*
