import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.environ.get('GEMINI_API_KEY') or os.getenv('GEMINI_API_KEY', '')
genai.configure(api_key=api_key)


def generate_reply(user_message: str, language: str = "uz") -> str:
    """Generate AI reply using Gemini 1.5 Flash"""
    try:
        api_key = os.environ.get('GEMINI_API_KEY') or os.getenv('GEMINI_API_KEY')
        if not api_key:
            return "⚠️ Gemini API key topilmadi. Iltimos, sozlamalarni tekshiring."

        model = genai.GenerativeModel("gemini-1.5-flash")

        prompt = f"Foydalanuvchi xabari: {user_message}\nIltimos, {language} tilida foydali, do'stona va qisqa javob yozing."

        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"❌ Gemini xatosi: {e}")
        return "Sizni qanday mahsulotlar qiziqtiradi 😊"
