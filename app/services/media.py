import os
import subprocess
import logging
from pathlib import Path

from app.config import settings

logger = logging.getLogger(__name__)


def extract_audio(video_path: str) -> str:
    Path(settings.temp_files_dir).mkdir(parents=True, exist_ok=True)

    base_name = os.path.splitext(os.path.basename(video_path))[0]
    audio_path = os.path.join(settings.temp_files_dir, f"{base_name}.m4a")

    command = [
        "ffmpeg",
        "-y",
        "-i", video_path,
        "-vn",
        "-acodec", "aac",
        "-ab", "128k",
        "-ar", "44100",
        audio_path
    ]

    logger.info(f"Extracting audio from {video_path}")
    logger.info(f"Running command: {' '.join(command)}")

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        timeout=300
    )

    if result.returncode != 0:
        logger.error(f"FFmpeg error: {result.stderr}")
        raise RuntimeError(f"FFmpeg failed to extract audio: {result.stderr}")

    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file was not created at {audio_path}")

    audio_size_mb = os.path.getsize(audio_path) / (1024 * 1024)
    logger.info(f"Audio extracted successfully: {audio_path} ({audio_size_mb:.2f} MB)")

    if audio_size_mb > 25:
        logger.warning(f"Audio file exceeds 25MB limit ({audio_size_mb:.2f} MB)")
        raise ValueError(f"Audio file too large: {audio_size_mb:.2f} MB (max 25MB)")

    return audio_path


def cleanup_temp_files(*file_paths: str) -> None:
    for file_path in file_paths:
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.info(f"Deleted temporary file: {file_path}")
            except Exception as e:
                logger.warning(f"Failed to delete temp file {file_path}: {e}")
