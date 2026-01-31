import os
from dotenv import load_dotenv
import google.generativeai as genai

# 🔑 LOAD .env (from project root)
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY not found in environment")

genai.configure(api_key=GEMINI_API_KEY)

# ✅ Correct model
model = genai.GenerativeModel("models/gemini-flash-lite-latest")


def generate(prompt: str) -> str | None:
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
        print("❌ Gemini error:", e)
        return None
