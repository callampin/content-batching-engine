import uuid
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.content import ContentJob, JobStatus
from app.schemas.content import (
    ContentJobCreate,
    ContentJobResponse,
    ContentJobListResponse
)
from workers.tasks import process_video_task

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/jobs", tags=["jobs"])


@router.post("", response_model=ContentJobResponse, status_code=status.HTTP_201_CREATED)
async def create_job(
    job_data: ContentJobCreate,
    db: AsyncSession = Depends(get_db)
):
    job = ContentJob(
        id=uuid.uuid4(),
        drive_file_id=job_data.drive_file_id,
        telegram_chat_id=job_data.telegram_chat_id,
        status=JobStatus.PENDING
    )

    db.add(job)
    await db.commit()
    await db.refresh(job)

    logger.info(f"Created job {job.id} with drive_file_id: {job.drive_file_id}")

    process_video_task.delay(str(job.id))

    logger.info(f"Task enqueued for job {job.id}")

    return job


@router.get("/{job_id}", response_model=ContentJobResponse)
async def get_job(
    job_id: str,
    db: AsyncSession = Depends(get_db)
):
    try:
        job_uuid = uuid.UUID(job_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid job ID format"
        )

    result = await db.execute(
        select(ContentJob).where(ContentJob.id == job_uuid)
    )
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )

    return job


@router.get("", response_model=ContentJobListResponse)
async def list_jobs(
    skip: int = 0,
    limit: int = 20,
    status_filter: Optional[JobStatus] = None,
    db: AsyncSession = Depends(get_db)
):
    query = select(ContentJob)

    if status_filter:
        query = query.where(ContentJob.status == status_filter)

    query = query.order_by(ContentJob.created_at.desc()).offset(skip).limit(limit)

    result = await db.execute(query)
    jobs = result.scalars().all()

    count_query = select(ContentJob)
    if status_filter:
        count_query = count_query.where(ContentJob.status == status_filter)

    total_result = await db.execute(count_query)
    total = len(total_result.scalars().all())

    return ContentJobListResponse(jobs=jobs, total=total)


@router.post("/{job_id}/retry", response_model=ContentJobResponse)
async def retry_job(
    job_id: str,
    db: AsyncSession = Depends(get_db)
):
    try:
        job_uuid = uuid.UUID(job_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid job ID format"
        )

    result = await db.execute(
        select(ContentJob).where(ContentJob.id == job_uuid)
    )
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )

    if job.status != JobStatus.FAILED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot retry job with status {job.status.value}"
        )

    job.status = JobStatus.PENDING
    job.error_message = None
    await db.commit()
    await db.refresh(job)

    process_video_task.delay(str(job.id))

    logger.info(f"Retry task enqueued for job {job.id}")

    return job
