import aiohttp
import asyncio
import os
from dotenv import load_dotenv
from core.memory import AsyncMemoryDB

load_dotenv()

class ConsensusEngine:
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.url = "https://openrouter.ai/api/v1/chat/completions"

    async def resolve(self, prompt, chat_id, image_urls=None):
        models = [
            "google/gemini-2.0-flash-001",
            "anthropic/claude-3.5-sonnet"
        ]
        
        # Cargar memoria de corto plazo
        history = await AsyncMemoryDB.get_history(chat_id)
        
        async def fetch_model(model, session):
            sys_prompt = """Eres un estudiante brillante de nivel postgrado resolviendo un examen.
Si es CIENCIAS/MATEMÁTICAS: Muestra solo el desarrollo directo en bloques matemáticos. Cero explicaciones narrativas de tu proceso mental.
Si es LETRAS/COMPRENSIÓN/ACTUALIDAD: Redacta un análisis profundo, bien estructurado en párrafos, con argumentos sólidos y ortografía impecable."""
            messages = [{"role": "system", "content": sys_prompt}]
            
            # Inyectar historial si existe
            for msg in history:
                messages.append(msg)
                
            content = [{"type": "text", "text": prompt}]
            if image_urls:
                for img in image_urls:
                    content.append({"type": "image_url", "image_url": {"url": img}})
                    
            messages.append({"role": "user", "content": content})

            try:
                async with session.post(self.url, headers={"Authorization": f"Bearer {self.api_key}"}, json={
                    "model": model,
                    "messages": messages,
                    "temperature": 0.2
                }, timeout=45) as resp:
                    data = await resp.json()
                    return data['choices'][0]['message']['content']
            except Exception as e:
                print(f"Error con modelo {model}: {e}")
                return None

        async with aiohttp.ClientSession() as session:
            tasks = [fetch_model(model, session) for model in models]
            responses = await asyncio.gather(*tasks)

        valid_responses = [r for r in responses if r]

        # EL VERIFICADOR ELIGE O COMBINA
        verification_prompt = f"""
        Como Juez Supremo, analiza estas soluciones y genera el DOCUMENTO FINAL con estas REGLAS ESTRICTAS:
        1. MATEMÁTICAS/CIENCIAS: Cero soluciones lineales largas. Usa display math. Cero explicaciones narrativas (nada de "Para resolver esto..."). Muestra solo desarrollo matemático directo.
        2. LETRAS/COMPRENSIÓN/ACTUALIDAD: Genera un ensayo/respuesta impecable, estructurado en bloques de lectura clara, profundo y riguroso.
        3. OBLIGATORIO: Devuelve código HTML limpio (<html><body>...</body></html>) para exportar a PDF. Usa MathJax nativo para fórmulas y SVG/Mermaid para visuales.
        
        SOLUCIÓN 1: {valid_responses[0] if len(valid_responses) > 0 else 'N/A'}
        SOLUCIÓN 2: {valid_responses[1] if len(valid_responses) > 1 else 'N/A'}
        """
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(self.url, headers={"Authorization": f"Bearer {self.api_key}"}, json={
                    "model": "google/gemini-2.0-flash-001",
                    "messages": [{"role": "user", "content": verification_prompt}]
                }, timeout=30) as resp:
                    data = await resp.json()
                    final_text = data['choices'][0]['message']['content']
                    # Guardar en memoria la interacción exitosa
                    await AsyncMemoryDB.add_message(chat_id, "user", prompt)
                    await AsyncMemoryDB.add_message(chat_id, "assistant", "Solucionario Generado en HTML.")
                    return final_text
            except Exception as e:
                return f"<html><body><h1>Error en Consenso</h1><p>{e}</p></body></html>"

consensus_engine = ConsensusEngine()

