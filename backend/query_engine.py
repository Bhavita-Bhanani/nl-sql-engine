import time
from sqlalchemy.orm import Session
from database import get_schema_context, execute_sql
from llm import generate_sql, explain_results
from models import QueryHistory


def process_query(question: str, db_path: str, db: Session) -> dict:
    """
    Full NL → SQL → Results → Explanation pipeline.
    Retries up to 2 times if SQL execution fails.

    Returns a dict with: sql, results, explanation, query_id, execution_time_ms, success
    """
    start_time = time.time()

    history_entry = QueryHistory(question=question, success=False)
    db.add(history_entry)
    db.flush()  # get the id

    try:
        # Step 1: Get schema context
        schema_context = get_schema_context(db_path)

        # Step 2: Generate SQL (with retry on failure)
        sql = None
        results = None
        last_error = None
        MAX_RETRIES = 2

        for attempt in range(MAX_RETRIES + 1):
            try:
                sql = generate_sql(
                    question,
                    schema_context,
                    error_feedback=last_error if attempt > 0 else "",
                )
                results = execute_sql(sql, db_path)
                last_error = None
                break  # success
            except ValueError as e:
                last_error = str(e)
                if attempt == MAX_RETRIES:
                    raise

        if results is None:
            raise RuntimeError("Failed to generate a valid SQL query after retries.")

        # Step 3: Generate explanation
        explanation = explain_results(question, sql, results)

        # Step 4: Compute timing
        execution_time_ms = int((time.time() - start_time) * 1000)

        # Step 5: Update history
        history_entry.generated_sql = sql
        history_entry.result_count = len(results)
        history_entry.explanation = explanation
        history_entry.success = True
        history_entry.execution_time_ms = execution_time_ms
        db.commit()
        db.refresh(history_entry)

        return {
            "query_id": history_entry.id,
            "question": question,
            "sql": sql,
            "results": results,
            "explanation": explanation,
            "result_count": len(results),
            "execution_time_ms": execution_time_ms,
            "success": True,
        }

    except Exception as e:
        execution_time_ms = int((time.time() - start_time) * 1000)
        error_msg = str(e)

        history_entry.success = False
        history_entry.error_message = error_msg
        history_entry.execution_time_ms = execution_time_ms
        if sql:
            history_entry.generated_sql = sql
        db.commit()
        db.refresh(history_entry)

        return {
            "query_id": history_entry.id,
            "question": question,
            "sql": sql or "",
            "results": [],
            "explanation": "",
            "result_count": 0,
            "execution_time_ms": execution_time_ms,
            "success": False,
            "error": error_msg,
        }
