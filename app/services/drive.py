import os
import json
import logging
from io import BytesIO
from pathlib import Path
from typing import Tuple, Optional

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

from app.config import settings

logger = logging.getLogger(__name__)


class DriveService:
    def __init__(self):
        self.credentials = None
        self.service = None
        self._initialize()

    def _initialize(self):
        try:
            credentials_dict = json.loads(settings.google_drive_credentials_json)
            self.credentials = service_account.Credentials.from_service_account_info(
                credentials_dict,
                scopes=[
                    "https://www.googleapis.com/auth/drive.readonly",
                    "https://www.googleapis.com/auth/drive.file"
                ]
            )
            self.service = build("drive", "v3", credentials=self.credentials, cache_discovery=False)
            logger.info("Google Drive service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Google Drive service: {e}")
            raise

    def get_file_metadata(self, file_id: str) -> dict:
        try:
            file_metadata = self.service.files().get(
                fileId=file_id,
                fields="id, name, mimeType, size"
            ).execute()
            logger.info(f"Retrieved metadata for file: {file_id}")
            return file_metadata
        except Exception as e:
            logger.error(f"Failed to get file metadata for {file_id}: {e}")
            raise

    def download_file(self, file_id: str, output_dir: str = None) -> Tuple[str, str]:
        if output_dir is None:
            output_dir = settings.temp_files_dir

        Path(output_dir).mkdir(parents=True, exist_ok=True)

        file_metadata = self.get_file_metadata(file_id)
        file_name = file_metadata.get("name", f"{file_id}.mp4")
        
        if not file_name.lower().endswith(('.mp4', '.mov', '.avi')):
            logger.warning(f"File {file_name} may not be a video file")

        file_path = os.path.join(output_dir, file_name)

        try:
            request = self.service.files().get_media(fileId=file_id)
            with open(file_path, "wb") as f:
                downloader = MediaIoBaseDownload(f, request)
                done = False
                while not done:
                    status, done = downloader.next_chunk()
                    if status:
                        logger.info(f"Download {int(status.progress() * 100)}%")

            logger.info(f"File downloaded successfully to: {file_path}")
            return file_path, file_name

        except Exception as e:
            logger.error(f"Failed to download file {file_id}: {e}")
            if os.path.exists(file_path):
                os.remove(file_path)
            raise

    def check_file_exists(self, file_id: str) -> bool:
        try:
            self.service.files().get(fileId=file_id).execute()
            return True
        except Exception:
            return False


drive_service = DriveService()
