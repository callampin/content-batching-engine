import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.content import ContentJob, JobStatus
from app.services.telegram import telegram_service
from workers.tasks import process_video_task

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/telegram", tags=["telegram"])


class TelegramUpdate(BaseModel):
    update_id: int
    callback_query: Optional[dict] = None


class TelegramWebhookRequest(BaseModel):
    update_id: int
    callback_query: Optional[dict] = None


@router.post("/webhook")
async def telegram_webhook(
    update: dict,
    db: AsyncSession = Depends(get_db)
):
    callback_query = update.get("callback_query")

    if not callback_query:
        return {"ok": True}

    callback_data = callback_query.get("data")
    message = callback_query.get("message")
    callback_message = callback_query.get("message")

    if not callback_data:
        return {"ok": True}

    logger.info(f"Received callback: {callback_data}")

    if callback_data.startswith("approve_"):
        job_id = callback_data.replace("approve_", "")
        return await handle_approve(job_id, callback_query, db)

    elif callback_data.startswith("reject_"):
        job_id = callback_data.replace("reject_", "")
        return await handle_reject(job_id, callback_query, db)

    elif callback_data.startswith("retry_"):
        job_id = callback_data.replace("retry_", "")
        return await handle_retry(job_id, callback_query, db)

    return {"ok": True}


async def handle_approve(
    job_id: str,
    callback_query: dict,
    db: AsyncSession
):
    try:
        job_uuid = uuid.UUID(job_id)
    except ValueError:
        return {"ok": False, "error": "Invalid job ID"}

    result = await db.execute(
        select(ContentJob).where(ContentJob.id == job_uuid)
    )
    job = result.scalar_one_or_none()

    if not job:
        return {"ok": False, "error": "Job not found"}

    job.status = JobStatus.APPROVED
    await db.commit()

    callback_message = callback_query.get("message")
    if callback_message:
        chat_id = callback_message.get("chat", {}).get("id")
        message_id = callback_message.get("message_id")

        if chat_id and message_id:
            await telegram_service.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=f"✅ <b>Contenido Aprobado</b>\n\n📁 Archivo: {job.drive_file_name}\nJob ID: {job_id}",
                reply_markup=None
            )

    logger.info(f"Job {job_id} approved")
    return {"ok": True, "message": "Job approved"}


async def handle_reject(
    job_id: str,
    callback_query: dict,
    db: AsyncSession
):
    try:
        job_uuid = uuid.UUID(job_id)
    except ValueError:
        return {"ok": False, "error": "Invalid job ID"}

    result = await db.execute(
        select(ContentJob).where(ContentJob.id == job_uuid)
    )
    job = result.scalar_one_or_none()

    if not job:
        return {"ok": False, "error": "Job not found"}

    job.status = JobStatus.REJECTED
    await db.commit()

    callback_message = callback_query.get("message")
    if callback_message:
        chat_id = callback_message.get("chat", {}).get("id")
        message_id = callback_message.get("message_id")

        if chat_id and message_id:
            await telegram_service.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=f"❌ <b>Contenido Rechazado</b>\n\n📁 Archivo: {job.drive_file_name}\nJob ID: {job_id}",
                reply_markup=None
            )

    logger.info(f"Job {job_id} rejected")
    return {"ok": True, "message": "Job rejected"}


async def handle_retry(
    job_id: str,
    callback_query: dict,
    db: AsyncSession
):
    try:
        job_uuid = uuid.UUID(job_id)
    except ValueError:
        return {"ok": False, "error": "Invalid job ID"}

    result = await db.execute(
        select(ContentJob).where(ContentJob.id == job_uuid)
    )
    job = result.scalar_one_or_none()

    if not job:
        return {"ok": False, "error": "Job not found"}

    if job.status != JobStatus.FAILED:
        return {"ok": False, "error": f"Cannot retry job with status {job.status.value}"}

    job.status = JobStatus.PENDING
    job.error_message = None
    await db.commit()

    process_video_task.delay(job_id)

    callback_message = callback_query.get("message")
    if callback_message:
        chat_id = callback_message.get("chat", {}).get("id")
        message_id = callback_message.get("message_id")

        if chat_id and message_id:
            await telegram_service.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=f"🔄 <b>Reintentando job</b>\n\n📁 Archivo: {job.drive_file_name}\nJob ID: {job_id}",
                reply_markup=None
            )

    logger.info(f"Job {job_id} retry enqueued")
    return {"ok": True, "message": "Job retry enqueued"}
