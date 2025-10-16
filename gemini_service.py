import google.generativeai as genai
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

api_key = os.environ.get('GEMINI_API_KEY') or os.getenv('GEMINI_API_KEY', '')
genai.configure(api_key=api_key)


def load_knowledge_base() -> str:
    """Load company knowledge base from file"""
    try:
        kb_file = Path("knowledge_base.txt")
        if kb_file.exists():
            with open(kb_file, 'r', encoding='utf-8') as f:
                return f.read()
        return ""
    except Exception as e:
        print(f"Knowledge base yuklash xatosi: {e}")
        return ""


def generate_reply(user_message: str, language: str = "uz") -> str:
    """Generate AI reply using Gemini 1.5 Flash with knowledge base"""
    try:
        api_key = os.environ.get('GEMINI_API_KEY') or os.getenv('GEMINI_API_KEY')
        if not api_key:
            return "⚠️ Gemini API key topilmadi. Iltimos, sozlamalarni tekshiring."

        knowledge_base = load_knowledge_base()
        
        model = genai.GenerativeModel("gemini-1.5-flash")

        if knowledge_base:
            prompt = f"""Siz kompaniya AI yordamchisisiz. Mijozlarga professional va do'stona javob bering.

KOMPANIYA MA'LUMOTLARI:
{knowledge_base}

FOYDALANUVCHI XABARI: {user_message}

Iltimos, {language} tilida qisqa, foydali va professional javob yozing. Kompaniya ma'lumotlaridan foydalaning."""
        else:
            prompt = f"Foydalanuvchi xabari: {user_message}\nIltimos, {language} tilida foydali, do'stona va qisqa javob yozing."

        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"❌ Gemini xatosi: {e}")
        return "Sizni qanday mahsulotlar qiziqtiradi 😊"
