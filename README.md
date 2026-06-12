# NL-SQL Engine 🤖

> Ask your database anything in plain English. No SQL knowledge required.

A full-stack AI application that converts natural language questions into SQL queries using a local LLM (no API keys, no cost), executes them against a real database, and returns both the results and a plain-English explanation.

---

## Features

- **Natural Language → SQL** — Powered by Llama 3 running locally via Ollama
- **Schema-aware** — Automatically reads your database schema and feeds it to the LLM
- **Retry logic** — If generated SQL fails, sends the error back to the LLM to self-correct
- **Results table** — Paginated, exportable to CSV
- **SQL viewer** — Syntax-highlighted generated SQL with copy button
- **AI explanation** — Plain-English summary of what the results mean
- **Query history** — All past queries saved, re-runnable with one click
- **Schema sidebar** — Visual explorer of all tables, columns, and types
- **100% local** — No OpenAI key, no cloud calls, runs entirely on your machine

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend API | Python 3.11 + FastAPI |
| LLM | Llama 3 via Ollama (local) |
| Database | SQLite + SQLAlchemy ORM |
| Frontend | React 18 + Vite |
| Styling | Tailwind CSS |
| HTTP Client | Axios |

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    React Frontend                        │
│   QueryInput → ResultTable / SQLDisplay / Explanation    │
└───────────────────────┬─────────────────────────────────┘
                        │ HTTP (axios)
                        ▼
┌─────────────────────────────────────────────────────────┐
│                  FastAPI Backend                         │
│                                                         │
│  POST /query                                            │
│    ├─ 1. Introspect DB schema                           │
│    ├─ 2. Build LLM prompt (schema + question)           │
│    ├─ 3. Call Ollama → get SQL                          │
│    ├─ 4. Execute SQL on SQLite                          │
│    ├─ 5. If error → retry with error feedback (×2)      │
│    ├─ 6. Call Ollama → explain results                  │
│    └─ 7. Save to history, return everything             │
│                                                         │
│  GET  /schema    GET  /history    DELETE /history/:id   │
└───────┬──────────────────────┬───────────────────────┬──┘
        │                      │                       │
        ▼                      ▼                       ▼
  Ollama (local)         ecommerce.db           app_metadata.db
  llama3 model           (sample data)          (query history)
```

---

## Setup (one-time, ~10 minutes)

### 1. Install Ollama

Download from **https://ollama.com** — it's a single installer (works on Windows, Mac, Linux).

Then pull the Llama 3 model:

```bash
ollama pull llama3
```

Ollama runs automatically as a background service after install.

### 2. Create the sample database

```bash
cd sample_data
python seed.py
```

This creates `sample_data/ecommerce.db` with 5 tables and realistic e-commerce data:
- **customers** (50 rows) — name, email, city, country, tier
- **products** (30 rows) — name, category, price, stock
- **orders** (200 rows) — with statuses: pending/shipped/delivered/cancelled
- **order_items** (500 rows) — line items per order
- **reviews** (150 rows) — ratings and comments

### 3. Start the backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

Backend runs at: **http://localhost:8000**  
Interactive API docs: **http://localhost:8000/docs**

### 4. Start the frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at: **http://localhost:5173**

---

## Example Questions to Try

```
Show me the top 5 customers by total spending
Which products have low stock (less than 20)?
What is the average order value by country?
Show monthly sales totals for the last 6 months
Which product category generates the most revenue?
Who are our gold tier customers?
What is the average product rating per category?
How many orders were cancelled this year?
Which supplier has the most products?
Show all orders from customers in the UK
```

---

## Project Structure

```
nl-sql-engine/
├── backend/
│   ├── main.py           # FastAPI routes
│   ├── database.py       # Schema introspection + SQL execution
│   ├── llm.py            # Ollama integration (generate SQL + explain)
│   ├── query_engine.py   # Full pipeline with retry logic
│   ├── models.py         # SQLAlchemy model for query history
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.jsx               # Main layout + state
│   │   └── components/
│   │       ├── QueryInput.jsx    # Textarea + example chips
│   │       ├── ResultTable.jsx   # Paginated table + CSV export
│   │       ├── SQLDisplay.jsx    # Syntax-highlighted SQL + copy
│   │       ├── QueryHistory.jsx  # Past queries list
│   │       └── SchemaViewer.jsx  # Collapsible table/column explorer
│   └── package.json
├── sample_data/
│   └── seed.py           # Creates ecommerce.db with realistic data
└── README.md
```

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/query` | Run a natural language query |
| GET | `/schema` | Get database schema |
| GET | `/history` | Get last 20 queries |
| DELETE | `/history/{id}` | Delete a history entry |
| GET | `/health` | Health check |

Full interactive docs available at `http://localhost:8000/docs` when the backend is running.

---

## How It Works

1. **Schema Introspection** — On each query, the backend reads the database structure (tables, columns, types, row counts) and formats it as text context.

2. **LLM Prompt Construction** — The schema context + user question are combined into a carefully engineered prompt that instructs the model to output only valid SQLite SELECT statements.

3. **SQL Generation** — Ollama runs Llama 3 locally and returns the SQL. The response is cleaned (markdown fences stripped, semicolons normalised).

4. **Safe Execution** — A keyword blocklist prevents any write operations (DROP, DELETE, UPDATE, etc.). The SQL is executed against the SQLite file and results returned as a list of dicts.

5. **Self-correction** — If execution fails, the error message is sent back to the LLM with a request to fix the SQL. Up to 2 retries.

6. **Explanation** — A second LLM call summarises the results in plain English.

7. **Persistence** — Every query (success or failure) is saved to a separate `app_metadata.db` for history.

---

## Extending the Project

- **Use your own database** — Pass any SQLite file path in the API request
- **Swap the LLM** — Change `OLLAMA_MODEL` in `.env` to `codellama`, `mistral`, or any Ollama-supported model
- **Add PostgreSQL support** — Replace SQLite connections in `database.py` with a psycopg2/asyncpg driver
- **Add charts** — Use the results data to render bar/line charts with Recharts or Chart.js
