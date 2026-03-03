from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.content import JobStatus


class ContentJobBase(BaseModel):
    drive_file_id: str


class ContentJobCreate(ContentJobBase):
    telegram_chat_id: Optional[int] = None


class GeneratedContent(BaseModel):
    twitter_thread: dict
    linkedin_post: str
    reels_scripts: list[dict]


class ContentJobResponse(BaseModel):
    id: str
    drive_file_id: str
    drive_file_name: Optional[str]
    status: JobStatus
    transcription: Optional[str]
    generated_content: Optional[GeneratedContent]
    telegram_chat_id: Optional[int]
    telegram_message_id: Optional[int]
    error_message: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class ContentJobListResponse(BaseModel):
    jobs: list[ContentJobResponse]
    total: int


class TelegramCallbackData(BaseModel):
    job_id: str
    action: str
