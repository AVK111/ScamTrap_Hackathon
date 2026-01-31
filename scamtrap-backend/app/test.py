from dotenv import load_dotenv
import os

load_dotenv()

print("Gemini key loaded:", bool(os.getenv("GEMINI_API_KEY")))
import google.generativeai as genai
for m in genai.list_models():
    print(m.name, m.supported_generation_methods)

