import asyncio
import json
import logging
import google.generativeai as genai

from app.config import settings

logger = logging.getLogger(__name__)

GEMINI_SYSTEM_PROMPT = """Eres un experto creador de contenido para redes sociales. Tu tarea es transformar transcripciones de videos en contenido optimizado para múltiples plataformas.

INPUT: Recibirás una transcripción de un video (podcast, entrevista, tutorial, etc.).

OUTPUT: Debes generar EXACTAMENTE un objeto JSON con esta estructura exacta:

{
  "twitter_thread": {
    "tweets": ["tweet 1...", "tweet 2...", "tweet 3..."]
  },
  "linkedin_post": "post completo para LinkedIn...",
  "reels_scripts": [
    {"script": "script para Reel 1...", "duration_estimate": 30},
    {"script": "script para Reel 2...", "duration_estimate": 45},
    {"script": "script para Reel 3...", "duration_estimate": 60}
  ]
}

REGLAS OBLIGATORIAS:
1. Twitter: Genera exactamente 3 tweets que formen un hilo coherente. Cada tweet debe ser conciso (máx 280 caracteres). El primer tweet debe ser un gancho atractivo.
2. LinkedIn: Genera un post profesional y engagement-ready. Incluye una pregunta para fomentar comentarios.
3. Reels: Genera exactamente 3 scripts. Cada script debe ser accionable y apropiado para formato corto (15-60 segundos). Incluye ganchos en los primeros 3 segundos.
4. El JSON debe ser válido y parseable. No incluyas markdown, no incluyas texto adicional.
5. El idioma del contenido debe coincidir con el idioma de la transcripción.
6. Adapta el tono al contenido: profesional para LinkedIn, conversacional para Twitter y Reels.
7. No inventes información que no esté en la transcripción."""


def configure_gemini():
    genai.configure(api_key=settings.gemini_api_key)


async def generate_content(transcription: str) -> dict:
    logger.info("Starting content generation with Gemini 1.5 Flash")

    configure_gemini()

    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=GEMINI_SYSTEM_PROMPT,
        generation_config={
            "response_mime_type": "application/json"
        }
    )

    try:
        response = await asyncio.to_thread(
            model.generate_content,
            transcription
        )

        raw_text = response.text
        logger.debug(f"Gemini raw response: {raw_text}")

        try:
            generated_content = json.loads(raw_text)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini JSON: {e}")
            logger.error(f"Raw response: {raw_text}")
            raise ValueError("Gemini returned invalid JSON")

        validate_content_structure(generated_content)

        logger.info("Content generation completed successfully")
        return generated_content

    except Exception as e:
        logger.error(f"Gemini content generation failed: {e}")
        raise


def validate_content_structure(content: dict) -> None:
    required_keys = ["twitter_thread", "linkedin_post", "reels_scripts"]
    for key in required_keys:
        if key not in content:
            raise ValueError(f"Missing required key: {key}")

    if "tweets" not in content["twitter_thread"]:
        raise ValueError("Missing tweets in twitter_thread")

    if len(content["twitter_thread"]["tweets"]) != 3:
        raise ValueError("Twitter thread must have exactly 3 tweets")

    if len(content["reels_scripts"]) != 3:
        raise ValueError("Must have exactly 3 reels scripts")

    for reel in content["reels_scripts"]:
        if "script" not in reel or "duration_estimate" not in reel:
            raise ValueError("Each reel script must have script and duration_estimate")

    logger.info("Content structure validated successfully")


async def generate_content_with_retry(transcription: str, max_retries: int = 3) -> dict:
    for attempt in range(max_retries):
        try:
            return await generate_content(transcription)
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            wait_time = 2 ** attempt
            logger.warning(f"Generation attempt {attempt + 1} failed, retrying in {wait_time}s: {e}")
            await asyncio.sleep(wait_time)
