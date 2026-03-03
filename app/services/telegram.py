import logging
import json
from typing import Optional

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

TELEGRAM_API_URL = "https://api.telegram.org"


class TelegramService:
    def __init__(self):
        self.bot_token = settings.telegram_bot_token
        self.admin_chat_id = settings.telegram_admin_chat_id
        self.base_url = f"{TELEGRAM_API_URL}/bot{self.bot_token}"

    async def send_message(
        self,
        chat_id: str,
        text: str,
        reply_markup: Optional[dict] = None
    ) -> dict:
        url = f"{self.base_url}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML"
        }

        if reply_markup:
            payload["reply_markup"] = reply_markup

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, timeout=30.0)
            response.raise_for_status()
            return response.json()

    async def edit_message_text(
        self,
        chat_id: str,
        message_id: int,
        text: str,
        reply_markup: Optional[dict] = None
    ) -> dict:
        url = f"{self.base_url}/editMessageText"
        payload = {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": text,
            "parse_mode": "HTML"
        }

        if reply_markup:
            payload["reply_markup"] = reply_markup

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, timeout=30.0)
            response.raise_for_status()
            return response.json()

    def format_content_for_telegram(self, content: dict, file_name: str) -> str:
        lines = []
        lines.append(f"📹 <b>Nuevo contenido generado</b>")
        lines.append(f"📁 Archivo: <code>{file_name}</code>")
        lines.append("")
        lines.append("<b>🐦 Hilo de Twitter:</b>")
        tweets = content.get("twitter_thread", {}).get("tweets", [])
        for i, tweet in enumerate(tweets, 1):
            lines.append(f"{i}/ {tweet[:275]}...")
        lines.append("")
        lines.append("<b>💼 LinkedIn:</b>")
        lines.append(content.get("linkedin_post", "")[:400] + "..." if len(content.get("linkedin_post", "")) > 400 else content.get("linkedin_post", ""))
        lines.append("")
        lines.append("<b>🎬 Scripts para Reels:</b>")
        reels = content.get("reels_scripts", [])
        for i, reel in enumerate(reels, 1):
            duration = reel.get("duration_estimate", 0)
            script = reel.get("script", "")[:150]
            lines.append(f"Reel {i} ({duration}s): {script}...")

        return "\n".join(lines)

    def get_approval_keyboard(self, job_id: str) -> dict:
        return {
            "inline_keyboard": [
                [
                    {"text": "✅ Aprobar", "callback_data": f"approve_{job_id}"},
                    {"text": "❌ Rechazar", "callback_data": f"reject_{job_id}"}
                ]
            ]
        }

    async def notify_admin_with_content(
        self,
        job_id: str,
        content: dict,
        file_name: str,
        telegram_chat_id: Optional[int] = None
    ) -> dict:
        text = self.format_content_for_telegram(content, file_name)
        keyboard = self.get_approval_keyboard(job_id)

        chat_id = telegram_chat_id or self.admin_chat_id

        logger.info(f"Sending content notification for job {job_id} to chat {chat_id}")

        return await self.send_message(chat_id, text, keyboard)

    async def notify_admin_error(
        self,
        job_id: str,
        error_message: str,
        file_name: Optional[str] = None
    ) -> dict:
        text = f"❌ <b>Error en job {job_id}</b>\n"
        if file_name:
            text += f"📁 Archivo: <code>{file_name}</code>\n"
        text += f"Error: {error_message}"

        keyboard = {
            "inline_keyboard": [
                [{"text": "🔄 Reintentar", "callback_data": f"retry_{job_id}"}]
            ]
        }

        logger.info(f"Sending error notification for job {job_id}")

        return await self.send_message(self.admin_chat_id, text, keyboard)


telegram_service = TelegramService()
