import asyncio
import logging
from openai import AsyncOpenAI

from app.config import settings

logger = logging.getLogger(__name__)

client = None


def get_openai_client() -> AsyncOpenAI:
    global client
    if client is None:
        client = AsyncOpenAI(api_key=settings.openai_api_key)
    return client


async def transcribe_audio(audio_path: str) -> str:
    logger.info(f"Starting transcription for: {audio_path}")

    openai_client = get_openai_client()

    try:
        with open(audio_path, "rb") as audio_file:
            response = await openai_client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="text",
                language="es"
            )

        transcription = response.strip()
        logger.info(f"Transcription completed: {len(transcription)} characters")

        if not transcription:
            raise ValueError("Whisper returned empty transcription")

        return transcription

    except Exception as e:
        logger.error(f"Whisper transcription failed: {e}")
        raise


async def transcribe_audio_with_retry(audio_path: str, max_retries: int = 3) -> str:
    for attempt in range(max_retries):
        try:
            return await transcribe_audio(audio_path)
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            wait_time = 2 ** attempt
            logger.warning(f"Transcription attempt {attempt + 1} failed, retrying in {wait_time}s: {e}")
            await asyncio.sleep(wait_time)
