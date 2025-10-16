# gemini_service.py
import google.generativeai as genai
from config import GEMINI_API_KEY, LANGUAGE

genai.configure(api_key=GEMINI_API_KEY)

def generate_reply(user_message: str) -> str:
    """Gemini 1.5 Flash yordamida javob yaratadi"""
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = f"Foydalanuvchi xabari: {user_message}\nIltimos, {LANGUAGE} tilida foydali, do‘stona va qisqa javob yozing."
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Gemini xatosi: {e}")
        return "Salom! Hozircha javob bera olmayapman 😊"
