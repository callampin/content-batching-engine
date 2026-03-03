import asyncio
import logging
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from workers.celery_app import celery_app
from app.database import async_session_maker, engine_sync
from app.models.content import ContentJob, JobStatus
from app.services.drive import drive_service
from app.services.media import extract_audio, cleanup_temp_files
from app.services.ai.whisper import transcribe_audio_with_retry
from app.services.ai.gemini import generate_content_with_retry
from app.services.telegram import telegram_service

logger = logging.getLogger(__name__)


def run_async(coro):
    return asyncio.run(coro)


async def get_job_from_db(job_id: str) -> ContentJob:
    async with async_session_maker() as session:
        result = await session.execute(
            select(ContentJob).where(ContentJob.id == uuid.UUID(job_id))
        )
        return result.scalar_one_or_none()


async def update_job_status(
    job_id: str,
    status: JobStatus,
    transcription: str = None,
    generated_content: dict = None,
    error_message: str = None
) -> None:
    async with async_session_maker() as session:
        result = await session.execute(
            select(ContentJob).where(ContentJob.id == uuid.UUID(job_id))
        )
        job = result.scalar_one_or_none()

        if job:
            job.status = status
            if transcription is not None:
                job.transcription = transcription
            if generated_content is not None:
                job.generated_content = generated_content
            if error_message is not None:
                job.error_message = error_message

            await session.commit()
            logger.info(f"Job {job_id} status updated to {status.value}")


@celery_app.task(bind=True, name="workers.tasks.process_video_task")
def process_video_task(self, job_id: str):
    video_path = None
    audio_path = None

    logger.info(f"Starting video processing for job: {job_id}")

    try:
        logger.info(f"[{job_id}] Step 1/6: Updating status to PROCESSING")
        run_async(update_job_status(job_id, JobStatus.PROCESSING))

        logger.info(f"[{job_id}] Step 2/6: Downloading video from Google Drive")
        job = run_async(get_job_from_db(job_id))
        if not job:
            raise ValueError(f"Job {job_id} not found in database")

        video_path, file_name = drive_service.download_file(job.drive_file_id)
        job.drive_file_name = file_name
        logger.info(f"[{job_id}] Video downloaded: {file_name}")

        logger.info(f"[{job_id}] Step 3/6: Extracting audio with FFmpeg")
        audio_path = extract_audio(video_path)
        logger.info(f"[{job_id}] Audio extracted: {audio_path}")

        logger.info(f"[{job_id}] Step 4/6: Transcribing with Whisper")
        transcription = run_async(transcribe_audio_with_retry(audio_path))
        logger.info(f"[{job_id}] Transcription completed: {len(transcription)} chars")

        logger.info(f"[{job_id}] Step 5/6: Generating content with Gemini")
        generated_content = run_async(generate_content_with_retry(transcription))
        logger.info(f"[{job_id}] Content generated successfully")

        logger.info(f"[{job_id}] Step 6/6: Saving to database and updating status")
        run_async(update_job_status(
            job_id,
            JobStatus.COMPLETED,
            transcription=transcription,
            generated_content=generated_content
        ))

        job = run_async(get_job_from_db(job_id))

        try:
            run_async(telegram_service.notify_admin_with_content(
                job_id=job_id,
                content=generated_content,
                file_name=job.drive_file_name if job else "Unknown",
                telegram_chat_id=job.telegram_chat_id if job else None
            ))
        except Exception as telegram_error:
            logger.error(f"Failed to send Telegram notification: {telegram_error}")

        logger.info(f"[{job_id}] Cleaning up temporary files")
        cleanup_temp_files(video_path, audio_path)

        logger.info(f"Job {job_id} completed successfully")
        return {"status": "completed", "job_id": job_id}

    except Exception as e:
        error_msg = str(e)
        logger.error(f"Job {job_id} failed: {error_msg}", exc_info=True)

        try:
            run_async(update_job_status(
                job_id,
                JobStatus.FAILED,
                error_message=error_msg
            ))
        except Exception as db_error:
            logger.error(f"Failed to update job status to FAILED: {db_error}")

        try:
            job = run_async(get_job_from_db(job_id))
            run_async(telegram_service.notify_admin_error(
                job_id=job_id,
                error_message=error_msg,
                file_name=job.drive_file_name if job else None
            ))
        except Exception as telegram_error:
            logger.error(f"Failed to send Telegram error notification: {telegram_error}")

        try:
            cleanup_temp_files(video_path, audio_path)
        except Exception as cleanup_error:
            logger.warning(f"Cleanup failed: {cleanup_error}")

        raise


@celery_app.task(name="workers.tasks.retry_failed_job")
def retry_failed_job(job_id: str):
    logger.info(f"Retrying failed job: {job_id}")
    return process_video_task.apply_async(args=[job_id])
