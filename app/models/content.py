from typing import Optional
from enum import Enum

from sqlalchemy import Column, String, Text, BigInteger, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB, TIMESTAMP
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime
import uuid


class JobStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    FAILED = "FAILED"


class Base(DeclarativeBase):
    pass


class ContentJob(Base):
    __tablename__ = "content_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    drive_file_id = Column(String(255), nullable=False)
    drive_file_name = Column(String(500), nullable=True)
    status = Column(SQLEnum(JobStatus), default=JobStatus.PENDING, nullable=False)
    transcription = Column(Text, nullable=True)
    generated_content = Column(JSONB, nullable=True)
    telegram_chat_id = Column(BigInteger, nullable=True)
    telegram_message_id = Column(BigInteger, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            "id": str(self.id),
            "drive_file_id": self.drive_file_id,
            "drive_file_name": self.drive_file_name,
            "status": self.status.value,
            "transcription": self.transcription,
            "generated_content": self.generated_content,
            "telegram_chat_id": self.telegram_chat_id,
            "telegram_message_id": self.telegram_message_id,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
