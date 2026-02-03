from dotenv import load_dotenv
import os

load_dotenv()

print("Gemini key loaded:", bool(os.getenv("GEMINI_API_KEY")))

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("GEMINI_API_KEY not set - skipping model list")
else:
    import google.generativeai as genai
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        for m in genai.list_models():
            print(m.name, m.supported_generation_methods)
    except Exception as e:
        print("Failed to list Gemini models:", e)

