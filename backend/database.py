import sqlite3
from typing import Any
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from models import Base
import os

# ── App metadata DB (stores query history) ──────────────────────────────────
METADATA_DB_PATH = os.getenv("METADATA_DB_PATH", "./app_metadata.db")
metadata_engine = create_engine(
    f"sqlite:///{METADATA_DB_PATH}",
    connect_args={"check_same_thread": False},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=metadata_engine)


def init_metadata_db():
    """Create all metadata tables if they don't exist."""
    Base.metadata.create_all(bind=metadata_engine)


def get_db_session() -> Session:
    """Dependency-injectable session for the metadata DB."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ── Target / user database (SQLite file the user queries) ────────────────────

def get_schema_context(db_path: str) -> str:
    """
    Introspect a SQLite database and return a rich schema description
    suitable for injecting into an LLM prompt.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get all user tables
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
    )
    tables = [row[0] for row in cursor.fetchall()]

    if not tables:
        conn.close()
        return "The database appears to be empty — no tables found."

    schema_lines = ["DATABASE SCHEMA\n" + "=" * 40]

    for table in tables:
        # Column info
        cursor.execute(f"PRAGMA table_info({table})")
        columns = cursor.fetchall()  # (cid, name, type, notnull, dflt, pk)

        # Row count
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        row_count = cursor.fetchone()[0]

        schema_lines.append(f"\nTable: {table} ({row_count} rows)")
        schema_lines.append("-" * 30)
        for col in columns:
            pk_mark = " [PK]" if col[5] else ""
            nn_mark = " NOT NULL" if col[3] else ""
            schema_lines.append(f"  {col[1]} ({col[2]}{pk_mark}{nn_mark})")

        # Foreign keys
        cursor.execute(f"PRAGMA foreign_key_list({table})")
        fks = cursor.fetchall()
        if fks:
            for fk in fks:
                schema_lines.append(f"  FK: {fk[3]} → {fk[2]}.{fk[4]}")

    conn.close()
    return "\n".join(schema_lines)


def execute_sql(sql: str, db_path: str) -> list[dict[str, Any]]:
    """
    Execute a read-only SQL statement against the target database.
    Returns a list of row dicts.
    Raises ValueError for forbidden statements or sqlite errors.
    """
    # Safety: block write operations
    forbidden = ("drop ", "delete ", "update ", "insert ", "alter ", "create ", "truncate ")
    sql_lower = sql.strip().lower()
    for kw in forbidden:
        if sql_lower.startswith(kw) or f" {kw}" in sql_lower:
            raise ValueError(
                f"Write operation '{kw.strip()}' is not allowed. Only SELECT queries are permitted."
            )

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try:
        cursor.execute(sql)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except sqlite3.Error as e:
        raise ValueError(f"SQL execution error: {str(e)}")
    finally:
        conn.close()
