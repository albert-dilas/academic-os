import aiohttp
import json
import os
from dotenv import load_dotenv

load_dotenv()

class LLMProvider:
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.groq_key = os.getenv("GROQ_API_KEY")
        self.url = "https://openrouter.ai/api/v1/chat/completions"

    async def transcribe_audio(self, audio_path):
        """Usa Groq Whisper para transcribir audios asíncronamente."""
        url = "https://api.groq.com/openai/v1/audio/transcriptions"
        headers = {"Authorization": f"Bearer {self.groq_key}"}
        
        async with aiohttp.ClientSession() as session:
            with open(audio_path, "rb") as f:
                data = aiohttp.FormData()
                data.add_field('file', f, filename=os.path.basename(audio_path))
                data.add_field('model', 'whisper-large-v3')
                
                async with session.post(url, headers=headers, data=data) as resp:
                    result = await resp.json()
                    return result.get("text", "")

    async def chat(self, prompt, image_urls=None):
        system_prompt = (
            "Eres el Núcleo de Razonamiento Experto del ACADEMIC-OS. "
            "Resuelve problemas paso a paso. "
            "Usa sintaxis LaTeX para matemáticas y SVG/Mermaid para diagramas."
        )
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        
        messages = [{"role": "system", "content": system_prompt}]
        
        content = [{"type": "text", "text": prompt}]
        if image_urls:
            # Soporta múltiples imágenes (array de Base64 o URLs)
            for img in image_urls:
                content.append({"type": "image_url", "image_url": {"url": img}})
                
        messages.append({"role": "user", "content": content})

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.url, headers=headers, json={"model": "google/gemini-2.0-flash-001", "messages": messages}, timeout=30) as resp:
                    data = await resp.json()
                    return data['choices'][0]['message']['content']
        except Exception as e:
            return f"Error en procesamiento: {e}"

    async def fast_chat(self, prompt, history=None):
        """Chat conversacional rápido (sin LaTeX forzado ni diagramas)."""
        system_prompt = "Eres el asistente conversacional de ACADEMIC-OS. Responde de forma natural, concisa y directa sin formato complejo."
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        
        messages = [{"role": "system", "content": system_prompt}]
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": prompt})

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.url, headers=headers, json={"model": "google/gemini-2.0-flash-001", "messages": messages}, timeout=10) as resp:
                    data = await resp.json()
                    return data['choices'][0]['message']['content']
        except Exception as e:
            return f"Lo siento, ocurrió un error rápido: {e}"

llm_provider = LLMProvider()

