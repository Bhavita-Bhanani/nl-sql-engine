from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()


class QueryHistory(Base):
    __tablename__ = "query_history"

    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text, nullable=False)
    generated_sql = Column(Text, nullable=True)
    result_count = Column(Integer, nullable=True, default=0)
    explanation = Column(Text, nullable=True)
    success = Column(Boolean, default=True)
    error_message = Column(Text, nullable=True)
    execution_time_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
