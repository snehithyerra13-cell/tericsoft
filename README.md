# AI-Powered Sales Lead Qualification Assistant

An intelligent full-stack sales engineering application that takes prospective customer requirements, performs real-time local semantic keyword retrieval across an enterprise product knowledge base, and uses Groq's high-speed Llama 3.3 LLM to generate structured lead qualification intelligence.

---

## 🌟 Features

- **Automated Lead Qualification**: Evaluates unstructured prospect RFPs, emails, or requirement notes in seconds.
- **Lightweight Local Knowledge Retrieval**: Fast, deterministic TF-IDF and Cosine Similarity retrieval pipeline over 10+ enterprise products without needing expensive vector databases or GPUs.
- **Grounded AI Synthesis via Groq**: Strictly prevents hallucinations by grounding the Groq LLM only on retrieved context.
- **Structured Pydantic Validation**: Guarantees type-safe responses (Lead Summary, Relevant Products with explanations, Inferred Needs, Recommended Next Step, and Discovery Questions).
- **Lead Scoring & Priority**: Transparent heuristic evaluation assigning a qualification score (0-100) and priority level (High, Medium, Low).
- **Full SQL Persistence**: Automatically stores every inquiry, retrieved product context, and AI analysis in SQLite for auditability.
- **Lead History & Catalog Browser**: Interactive dashboard allowing sales reps to review past evaluations and inspect the underlying product knowledge base.
- **Resilient & Safe**: Gracefully handles missing API keys, rate limits, and network errors with human-friendly guidance.

---

## 🏗️ Architecture

```
Prospective Customer Requirement (Web UI)
                 │
                 ▼
     [ React + Vite Frontend ]
                 │
                 ▼ (HTTP POST /api/leads/analyze)
     [ FastAPI Backend Service ]
                 │
                 ├──► 1. Preprocess requirement query (Tokenization & Stopwords)
                 │
                 ├──► 2. Local TF-IDF Cosine Similarity Engine
                 │         └── Scans 10+ seeded products in SQLite
                 │         └── Selects Top 3 most relevant products with scores
                 │
                 ├──► 3. Grounded Prompt Formulation
                 │         └── Injects ONLY retrieved products into System/User Prompt
                 │
                 ├──► 4. Groq LLM (`llama-3.3-70b-versatile`)
                 │         └── Returns structured JSON
                 │
                 ├──► 5. Pydantic Safe Parsing & Fallback Recovery
                 │
                 ├──► 6. SQLite Persistence (`leads` and `products` tables)
                 │
                 ▼
     [ Interactive Qualification Report ]
```

---

## 💻 Tech Stack

- **Frontend**: React 18, Vite, Modern CSS (Responsive Design, Dark SaaS Theme), Lucide Icons.
- **Backend**: Python 3.13, FastAPI, Pydantic v2, SQLAlchemy 2.0, SQLite.
- **AI & LLM**: Groq Python SDK (`groq`), `llama-3.3-70b-versatile` (configurable via `.env`).
- **Retrieval Engine**: Local Sublinear TF-IDF + Weighted Field Cosine Similarity (Zero-cost, CPU-only).
- **Testing**: Pytest, FastAPI TestClient (`httpx`).

---

## 📁 Project Structure

```
my project/
│
├── backend/
│   ├── main.py                 # FastAPI application and route handlers
│   ├── config.py               # Pydantic Settings & environment configuration
│   ├── database.py             # SQLite SQLAlchemy engine and session setup
│   ├── models.py               # Database models (Lead, Product)
│   ├── schemas.py              # Pydantic validation models
│   ├── crud.py                 # Database CRUD operations
│   ├── seed.py                 # 10 enterprise SaaS products seed catalog
│   ├── requirements.txt        # Python backend dependencies
│   ├── .env.example            # Sample environment variables file
│   ├── .env                    # Local environment variables (git-ignored)
│   │
│   ├── ai/
│   │   ├── groq_client.py      # Groq API client with safe JSON parsing & recovery
│   │   └── prompts.py          # Grounded Sales Qualification prompts
│   │
│   ├── retrieval/
│   │   └── retriever.py        # TF-IDF & Cosine Similarity vector search
│   │
│   └── tests/
│       ├── test_api.py         # End-to-end API integration tests
│       └── test_retrieval.py   # Unit tests for retrieval engine
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Header.jsx           # Top navigation with live Groq/Catalog status
│   │   │   ├── LeadInputForm.jsx    # Textarea, presets, and analyze action
│   │   │   ├── AnalysisResult.jsx   # Structured result breakdown & accordion
│   │   │   ├── LeadHistory.jsx      # Historical lead qualification drawer
│   │   │   └── ProductsModal.jsx    # Knowledge base catalog viewer
│   │   ├── services/
│   │   │   └── api.js               # Frontend API communication layer
│   │   ├── App.jsx                  # Main application state and layout
│   │   ├── index.css                # Polished dark modern UI styling
│   │   └── main.jsx                 # React root entrypoint
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
│
├── .gitignore                  # Git ignore rules (.env, node_modules, *.db)
└── README.md                   # Complete documentation
```

---

## ⚙️ Setup & Installation

### 1. Prerequisites
- Python 3.10+ (tested on Python 3.13)
- Node.js 18+ and npm

### 2. Backend Setup
Navigate to the project root and install Python dependencies:

```bash
cd backend
pip install -r requirements.txt
```

Initialize the database and seed the 10 catalog products:
```bash
python seed.py
```
*(Note: The database is also automatically initialized and seeded on backend startup if empty).*

### 3. Frontend Setup
Navigate to the frontend directory and install dependencies:

```bash
cd ../frontend
npm install
```

---

## 🔑 Environment Variables

In `backend/`, copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Edit `backend/.env`:
```ini
# Required for live LLM qualifications:
GROQ_API_KEY=gsk_your_groq_api_key_here

# Configurable Groq model (defaults to llama-3.3-70b-versatile):
GROQ_MODEL=llama-3.3-70b-versatile

# SQLite database URL:
DATABASE_URL=sqlite:///./leads.db
```

> **Safety Notice:** If `GROQ_API_KEY` is not set, the application continues to run safely and returns a clear, user-friendly configuration message without crashing the server.

---

## 🚀 Running the Application

### Start the Backend
From the project root:
```bash
python -m uvicorn backend.main:app --reload --port 8000
```
- API Docs: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/api/health`

### Start the Frontend
In a new terminal window:
```bash
cd frontend
npm run dev
```
Open `http://localhost:5173` in your browser.

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Checks server health, Groq key readiness, and catalog count |
| `GET` | `/api/products` | Lists all 10 products in the knowledge base |
| `POST` | `/api/leads/analyze` | Qualifies a lead via TF-IDF retrieval + Groq LLM |
| `GET` | `/api/leads` | Retrieves historical qualified leads |

### Sample POST `/api/leads/analyze` Request:
```json
{
  "requirement": "We are a growing e-commerce company and need automated customer support with analytics."
}
```

### Sample Response:
```json
{
  "lead_id": 1,
  "requirement": "We are a growing e-commerce company and need automated customer support with analytics.",
  "retrieved_products": [
    {
      "id": 2,
      "name": "AI Customer Support Platform",
      "category": "Customer Support",
      "description": "Next-generation generative AI customer service platform...",
      "features": ["24/7 automated resolution...", "Customer sentiment scoring..."],
      "solution": "Reduces customer wait times by 80%...",
      "score": 0.374
    }
  ],
  "analysis": {
    "lead_summary": "An expanding e-commerce enterprise seeking omnichannel ticket deflection and support intelligence...",
    "relevant_products": [
      {
        "name": "AI Customer Support Platform",
        "reason": "Provides 24/7 automated tier-1 ticket resolution across chat and email."
      }
    ],
    "potential_customer_needs": [
      "Deflect high-volume routine inquiries",
      "Gain real-time visibility into customer sentiment"
    ],
    "recommended_next_step": "Arrange a technical demonstration highlighting ticket deflections and Zendesk integration.",
    "follow_up_questions": [
      "What is your peak ticket volume during promotional cycles?",
      "Which helpdesk CRM do your agents currently rely on?",
      "What percentage of tier-1 inquiries do you aim to deflect?"
    ],
    "lead_score": 85,
    "priority": "High"
  },
  "created_at": "2026-09-16T18:30:00Z"
}
```

---

## 🔍 Retrieval Approach

The knowledge retrieval layer is implemented in [`backend/retrieval/retriever.py`](backend/retrieval/retriever.py):
1. **Tokenization & Stopword Filtering**: Strips punctuation and removes common English conversational noise.
2. **Multi-Field Document Weighting**: Product attributes are weighted to prioritize precision:
   - `name`: 3.0x weight
   - `category`: 2.0x weight
   - `solution`: 2.0x weight
   - `features`: 1.0x weight
   - `description`: 1.0x weight
3. **Sublinear TF-IDF**: Evaluates term significance using \( \text{TF} = 1 + \ln(\text{count}) \) and smoothed \( \text{IDF} = \ln((1 + N) / (1 + \text{df})) + 1 \).
4. **Cosine Similarity**: Calculates vector dot products normalized by Euclidean norms to deliver exact top-3 product rankings with calibrated relevance scores.
5. **Zero External Dependency**: Pure CPU implementation using Python standard math libraries — no external vector DBs, no OpenAI API fees, and instant sub-millisecond execution.

---

## 🤖 Prompting Strategy & LLM Grounding

The prompting system is located in [`backend/ai/prompts.py`](backend/ai/prompts.py):
- **Strict Grounding Directive**: The LLM is instructed under a system prompt that it acts as a Sales Lead Qualification Assistant and is **strictly prohibited** from referencing or inventing products not found in the injected knowledge context.
- **Top-K Context Injection**: Only the top 3 scored products are formatted with their categories, descriptions, feature bullets, and solutions.
- **Enforced JSON Output**: The request specifies `response_format={"type": "json_object"}`.
- **Defensive Parsing**: [`backend/ai/groq_client.py`](backend/ai/groq_client.py) includes regex stripping of code fences, outermost bracket extraction, and automated fallback schema construction to protect against malformed responses.

---

## 🗄️ Database Design

SQLite relational schema managed via SQLAlchemy:
- **`products`**:
  - `id`: Integer Primary Key
  - `name`: Unique product name (indexed)
  - `category`: Solution domain (indexed)
  - `description`: Detailed capability summary
  - `features`: JSON array of key capabilities
  - `solution`: Primary business value proposition
- **`leads`**:
  - `id`: Integer Primary Key
  - `customer_requirement`: Raw inquiry text
  - `retrieved_context`: JSON-serialized array of top-3 matched products & similarity scores
  - `ai_analysis`: Complete JSON-serialized qualification object
  - `created_at`: UTC Timestamp

---

## 🧪 Automated Testing

Run the automated test suite with pytest:

```bash
python -m pytest backend/tests -v
```

The test suite includes 10 test cases covering:
1. System health check & database product count verification.
2. Retrieval engine keyword matching (support, cyber risk, sales pipeline).
3. Retrieval empty-query fallbacks.
4. Input validation (whitespace, minimum length).
5. Missing Groq API key handling (verifies clean 503 response without server crash).
6. End-to-end qualification pipeline with mocked Groq responses and SQLite persistence validation.

---

## 🛡️ Security Best Practices

- **Zero Hardcoded Secrets**: Secrets are loaded from `.env` via `pydantic-settings`.
- **Git Hygiene**: `.gitignore` prevents `.env`, `*.db`, and cache files from ever reaching version control.
- **Backend-Only LLM Calls**: The client browser never communicates directly with Groq or handles secret keys.
- **Input Sanitization & Length Limits**: Enforced 4,000 character maximums and minimum length thresholds.

---

## 📝 AI Coding Disclosure

This project was architected and built by a senior full-stack AI engineer leveraging automated coding tools for rapid prototyping and iteration. The system architecture, retrieval math, prompt grounding, and database persistence have been reviewed and verified for production readiness.
