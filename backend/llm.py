import httpx
import re
import os
import json
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"


def _call_groq(messages: list[dict], timeout: int = 30) -> str:
    """
    Call the Groq API with a list of messages.
    Returns the response text.
    """
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": GROQ_MODEL,
        "messages": messages,
        "temperature": 0.1,
        "max_tokens": 1024,
    }

    try:
        response = httpx.post(
            GROQ_API_URL,
            headers=headers,
            json=payload,
            timeout=timeout,
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()
    except httpx.ConnectError:
        raise ConnectionError("Cannot connect to Groq API. Check your internet connection.")
    except httpx.TimeoutException:
        raise TimeoutError("Groq API took too long to respond.")
    except httpx.HTTPStatusError as e:
        raise RuntimeError(f"Groq API error {e.response.status_code}: {e.response.text}")
    except Exception as e:
        raise RuntimeError(f"Groq error: {str(e)}")


def _clean_sql(raw: str) -> str:
    """
    Strip markdown code fences and extra whitespace from LLM SQL output.
    """
    raw = re.sub(r"```(?:sql)?", "", raw, flags=re.IGNORECASE)
    raw = raw.replace("```", "")

    lines = [line.strip() for line in raw.strip().splitlines() if line.strip()]

    sql_lines = []
    started = False
    for line in lines:
        upper = line.upper()
        if upper.startswith(("SELECT", "WITH", "EXPLAIN")):
            started = True
        if started:
            sql_lines.append(line)
            if line.rstrip().endswith(";"):
                break

    result = " ".join(sql_lines) if sql_lines else " ".join(lines)
    result = result.strip().rstrip(";") + ";"
    return result


def generate_sql(question: str, schema_context: str, error_feedback: str = "") -> str:
    """
    Ask Groq to convert a natural language question into SQL.
    """
    system_msg = {
        "role": "system",
        "content": (
            "You are an expert SQL query generator. Your ONLY job is to output a single valid SQLite SELECT query.\n"
            "Rules:\n"
            "- Output ONLY the SQL query. No explanations, no markdown, no code fences.\n"
            "- Use only SELECT statements. Never use DROP, DELETE, UPDATE, INSERT, ALTER, CREATE.\n"
            "- Use only the tables and columns that exist in the provided schema.\n"
            "- Always use proper JOINs when data spans multiple tables.\n"
            "- Limit results to 100 rows unless the user asks for more.\n"
            "- Use SQLite-compatible syntax.\n"
            "- End the query with a semicolon."
        ),
    }

    if error_feedback:
        user_content = (
            f"{schema_context}\n\n"
            f"Question: {question}\n\n"
            f"Your previous SQL failed with this error:\n{error_feedback}\n\n"
            f"Fix the SQL and output ONLY the corrected query:"
        )
    else:
        user_content = (
            f"{schema_context}\n\n"
            f"Question: {question}\n\n"
            f"Output ONLY the SQL SELECT query to answer this question:"
        )

    messages = [system_msg, {"role": "user", "content": user_content}]
    raw = _call_groq(messages, timeout=30)
    return _clean_sql(raw)


def explain_results(question: str, sql: str, results_sample: list[dict]) -> str:
    """
    Ask Groq to explain the query results in plain English.
    """
    sample_str = json.dumps(results_sample[:5], indent=2, default=str)
    row_count = len(results_sample)

    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful data analyst. Given a question, a SQL query, and sample results, "
                "write a concise 1-2 sentence plain English answer. Be specific with numbers and names from the data."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Question: {question}\n\n"
                f"SQL used:\n{sql}\n\n"
                f"Results ({row_count} rows total, showing up to 5):\n{sample_str}\n\n"
                f"Write a plain English answer:"
            ),
        },
    ]

    try:
        return _call_groq(messages, timeout=20)
    except Exception:
        return f"Query returned {row_count} result{'s' if row_count != 1 else ''}."
