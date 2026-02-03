import os
from dotenv import load_dotenv
import logging
import google.generativeai as genai

# 🔑 LOAD .env (from project root)
load_dotenv()
logger = logging.getLogger(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
model = None

if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("models/gemini-flash-lite-latest")
        logger.info("✅ Gemini configured")
    except Exception as e:
        logger.warning(f"⚠️ Failed to configure Gemini model: {e}")
        model = None
else:
    logger.warning("⚠️ GEMINI_API_KEY not set; Gemini will be disabled")


def generate(prompt: str) -> str | None:
    if model is None:
        logger.warning("⚠️ Gemini not configured; generate() returning None")
        return None

    try:
        response = model.generate_content(prompt)

        if not response:
            return None

        if hasattr(response, "text") and response.text:
            return response.text.strip()

        if hasattr(response, "candidates") and response.candidates:
            parts = response.candidates[0].content.parts
            return "".join(
                p.text for p in parts if hasattr(p, "text")
            ).strip()

        return None

    except Exception as e:
        logger.error("❌ Gemini error:", exc_info=e)
        return None
