from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional
import os
import sys

from database import get_db_session, get_schema_context, init_metadata_db
from query_engine import process_query
from models import QueryHistory

# ── Auto-seed the sample database if it doesn't exist ───────────────────────
DEFAULT_DB_PATH = os.getenv("DEFAULT_DB_PATH", "../sample_data/ecommerce.db")

def auto_seed():
    """Seed the sample database automatically if it's missing."""
    db_path = DEFAULT_DB_PATH
    if not os.path.exists(db_path):
        # Try path relative to this file
        base = os.path.dirname(os.path.abspath(__file__))
        alt_path = os.path.join(base, "..", "sample_data", "ecommerce.db")
        seed_script = os.path.join(base, "..", "sample_data", "seed.py")
        os.makedirs(os.path.dirname(os.path.abspath(alt_path)), exist_ok=True)

        if os.path.exists(seed_script):
            print("Auto-seeding sample database...")
            import subprocess
            subprocess.run([sys.executable, seed_script], check=True)
            print("Sample database seeded.")

auto_seed()

# ── Initialise ───────────────────────────────────────────────────────────────
init_metadata_db()

app = FastAPI(
    title="NL-SQL Engine",
    description="Ask your database questions in plain English.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request / Response models ────────────────────────────────────────────────

class QueryRequest(BaseModel):
    question: str
    db_path: Optional[str] = None


class QueryResponse(BaseModel):
    query_id: int
    question: str
    sql: str
    results: list[dict]
    explanation: str
    result_count: int
    execution_time_ms: int
    success: bool
    error: Optional[str] = None


# ── Routes ───────────────────────────────────────────────────────────────────

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "NL-SQL Engine"}


@app.post("/query", response_model=QueryResponse)
def run_query(
    req: QueryRequest,
    db: Session = Depends(get_db_session),
):
    db_path = req.db_path or DEFAULT_DB_PATH

    if not os.path.exists(db_path):
        raise HTTPException(
            status_code=404,
            detail=f"Database file not found: {db_path}. Run sample_data/seed.py first.",
        )

    result = process_query(req.question, db_path, db)
    return result


@app.get("/schema")
def get_schema(db_path: Optional[str] = None):
    path = db_path or DEFAULT_DB_PATH

    if not os.path.exists(path):
        raise HTTPException(
            status_code=404,
            detail=f"Database file not found: {path}",
        )

    try:
        import sqlite3

        conn = sqlite3.connect(path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
        )
        tables_raw = [row[0] for row in cursor.fetchall()]

        schema = []
        for table in tables_raw:
            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            row_count = cursor.fetchone()[0]
            schema.append(
                {
                    "table": table,
                    "row_count": row_count,
                    "columns": [
                        {
                            "name": col[1],
                            "type": col[2],
                            "primary_key": bool(col[5]),
                            "not_null": bool(col[3]),
                        }
                        for col in columns
                    ],
                }
            )
        conn.close()
        return {"tables": schema, "db_path": path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/history")
def get_history(limit: int = 20, db: Session = Depends(get_db_session)):
    entries = (
        db.query(QueryHistory)
        .order_by(QueryHistory.created_at.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "id": e.id,
            "question": e.question,
            "generated_sql": e.generated_sql,
            "result_count": e.result_count,
            "explanation": e.explanation,
            "success": e.success,
            "error_message": e.error_message,
            "execution_time_ms": e.execution_time_ms,
            "created_at": e.created_at.isoformat() if e.created_at else None,
        }
        for e in entries
    ]


@app.delete("/history/{query_id}")
def delete_history_entry(query_id: int, db: Session = Depends(get_db_session)):
    entry = db.query(QueryHistory).filter(QueryHistory.id == query_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="History entry not found")
    db.delete(entry)
    db.commit()
    return {"message": "Deleted successfully"}
