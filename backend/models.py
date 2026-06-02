from sqlalchemy import Column, String, Text, DateTime, Enum, Boolean, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from database import Base
import uuid
import datetime

class Bug(Base):
    __tablename__ = "bugs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    root_cause = Column(Text)
    fix_description = Column(Text, nullable=False)
    severity = Column(Enum("low", "medium", "high", "critical", name="severity_enum"), default="medium")
    resolved_by = Column(String(100), nullable=False)
    resolved_at = Column(DateTime, default=datetime.datetime.utcnow)
    language = Column(String(50))
    file_path = Column(String(500))
    embedding = Column(Text)  # Store as JSON string — Week 6: replace with pgvector
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    approved = Column(Boolean, default=True)
    occurrence_count = Column(Integer, default=1)

class BugHistory(Base):
    __tablename__ = "bug_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    bug_id = Column(UUID(as_uuid=True), ForeignKey("bugs.id"), nullable=False)
    changed_by = Column(String(100), nullable=False)
    changed_at = Column(DateTime, default=datetime.datetime.utcnow)
    previous_snapshot = Column(JSONB, nullable=False)    