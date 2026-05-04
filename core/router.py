import os
import aiohttp
from dotenv import load_dotenv

load_dotenv()

class SemanticRouter:
    @staticmethod
    async def analyze_intent(text):
        """
        Analiza el texto de entrada y devuelve 'CHAT' si es conversacional/trivial,
        o 'PROBLEM' si es una tarea académica, técnica o matemática.
        """
        api_key = os.getenv("OPENROUTER_API_KEY")
        url = "https://openrouter.ai/api/v1/chat/completions"
        
        prompt = f"""
        Clasifica el siguiente mensaje del usuario. 
        Si es un saludo, una pregunta trivial, o una pregunta sobre tus capacidades (ej. "¿qué puedes hacer?"), responde SOLO con la palabra: CHAT.
        Si es un problema académico, matemático, técnico o una tarea compleja, responde SOLO con la palabra: PROBLEM.
        
        Mensaje: "{text}"
        """
        
        try:
            async with aiohttp.ClientSession() as session:
                model_name = os.getenv("PRIMARY_MODEL", "google/gemini-2.0-flash-001")
                async with session.post(url, headers={"Authorization": f"Bearer {api_key}"}, json={
                    "model": model_name,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.0
                }, timeout=5) as resp:
                    data = await resp.json()
                    result = data['choices'][0]['message']['content'].strip().upper()
                    return "PROBLEM" if "PROBLEM" in result else "CHAT"
        except Exception:
            # En caso de error, asumir PROBLEM por seguridad para usar el motor completo
            return "PROBLEM"

router = SemanticRouter()
