"""
ConsensusEngine — Academic-OS V5.1
Motor de consenso multi-modelo con prompts académicos de alta fidelidad.
"""
import aiohttp
import asyncio
import os
from dotenv import load_dotenv
from core.memory import AsyncMemoryDB

load_dotenv()

# ─── PROMPTS DE SISTEMA ─────────────────────────────────────────────────────

SOLVER_SYSTEM_PROMPT = """Eres un EXPERTO ACADÉMICO de nivel postgrado.
MISIÓN: Generar soluciones académicas perfectas y estructuradas.

REGLAS DE FORMATO (CRÍTICAS PARA PDF):
1. NO uses Markdown (evita #, *, **).
2. Usa etiquetas HTML estándar: <b> para negrita, <i> para cursiva.
3. MATEMÁTICAS: Usa notación clara y legible. 
   - Para potencias usa <sup> (ej: x<sup>2</sup>)
   - Para subíndices usa <sub> (ej: a<sub>1</sub>)
   - Para fracciones usa texto claro o tablas (ej: 3/4)
   - EVITA LaTeX complejo como \\frac o \\begin{equation} ya que el exportador PDF no lo soporta.
   - Usa símbolos Unicode: √, ∞, π, ±, ≤, ≥, ≠, ≈, ×, ÷.

4. ESTRUCTURA OBLIGATORIA:
   - <div class="question-block">...</div> para el enunciado.
   - <div class="solution-block">...</div> para el desarrollo detallado.
   - <div class="answer-box">...</div> para la respuesta final.
   - <div class="math-block">...</div> para fórmulas destacadas.

5. Sé EXTREMADAMENTE detallado en el desarrollo paso a paso."""

JUDGE_SYSTEM_PROMPT = """Eres el JUEZ SUPREMO ACADÉMICO. Tu misión es fusionar las respuestas de múltiples IAs en un SOLUCIONARIO MAESTRO.

REGLAS DE ORO:
1. SOLO HTML PURO. Nada de bloques de código (```), nada de markdown.
2. Formatea las matemáticas usando HTML (<sup>, <sub>, símbolos Unicode).
3. Asegura que CADA pregunta tenga:
   - <div class="question-block"><div class="question-number">Pregunta N°X</div><div class="question-text">ENUNCIADO</div></div>
   - <div class="solution-block">DESARROLLO PASO A PASO</div>
   - <div class="answer-box"><div class="answer-label">✅ Respuesta Final</div><div class="answer-content">RESULTADO</div></div>
4. El PDF se genera desde este HTML, así que usa un estilo limpio y profesional."""

# ─── DETECCIÓN DE MATERIA ───────────────────────────────────────────────────

def detect_subject(prompt: str) -> str:
    """Detecta el tipo de materia para personalizar el prompt."""
    text = prompt.lower()
    if any(k in text for k in ['ecuación', 'derivada', 'integral', 'algebra', 'cálculo', 'trigon',
                                'geometría', 'función', 'límite', 'matriz', 'vector', 'probabilidad']):
        return "MATEMÁTICAS"
    if any(k in text for k in ['física', 'fuerza', 'velocidad', 'aceleración', 'energía', 'momentum',
                                'ley de newton', 'circuito', 'campo', 'óptica', 'termodinámica']):
        return "FÍSICA"
    if any(k in text for k in ['química', 'mol', 'estequiometría', 'reacción', 'átomo', 'enlace',
                                'solución', 'concentración', 'ph', 'oxidación']):
        return "QUÍMICA"
    if any(k in text for k in ['historia', 'guerra', 'civilización', 'revolución', 'cultura', 'sociedad',
                                'política', 'economía', 'filosofía']):
        return "CIENCIAS SOCIALES"
    if any(k in text for k in ['lenguaje', 'comprensión', 'texto', 'redacción', 'gramática', 'ortografía',
                                'literatura', 'poema', 'análisis literario', 'resumen']):
        return "LENGUAJE"
    if any(k in text for k in ['biología', 'célula', 'adn', 'gen', 'ecosistema', 'evolución',
                                'metabolismo', 'anatomía', 'fotosíntesis']):
        return "BIOLOGÍA"
    return "ACADÉMICO GENERAL"


class ConsensusEngine:
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.url = "https://openrouter.ai/api/v1/chat/completions"

    def _get_models(self):
        models_env = os.getenv(
            "CONSENSUS_MODELS",
            "google/gemini-2.0-flash-001,anthropic/claude-sonnet-4-5"
        )
        return [m.strip() for m in models_env.split(",") if m.strip()]

    def _get_primary_model(self):
        return os.getenv("PRIMARY_MODEL", "google/gemini-2.0-flash-001")

    async def _fetch_model(self, model: str, messages: list, session: aiohttp.ClientSession, timeout: int = 90) -> str | None:
        """Consulta un modelo y retorna su respuesta."""
        try:
            async with session.post(
                self.url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://github.com/albert-dilas/academic-os",
                    "X-Title": "Academic-OS V5.1"
                },
                json={
                    "model": model,
                    "messages": messages,
                    "temperature": 0.15,
                    "max_tokens": 4096
                },
                timeout=aiohttp.ClientTimeout(total=timeout)
            ) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    print(f"[CONSENSUS] ⚠️ Modelo {model} — HTTP {resp.status}: {text[:200]}")
                    return None
                data = await resp.json()
                content = data['choices'][0]['message']['content']
                print(f"[CONSENSUS] ✅ Respuesta de {model} ({len(content)} chars)")
                return content
        except asyncio.TimeoutError:
            print(f"[CONSENSUS] ⏱️ Timeout en {model}")
            return None
        except Exception as e:
            print(f"[CONSENSUS] ❌ Error con {model}: {e}")
            return None

    async def resolve(self, user_prompt: str, chat_id: int, image_urls: list = None) -> str:
        """
        Pipeline completo: Múltiples solvers → Juez Supremo → HTML final.
        """
        models = self._get_models()
        subject = detect_subject(user_prompt)
        history = await AsyncMemoryDB.get_history(chat_id)
        
        print(f"[CONSENSUS] 🎓 Materia detectada: {subject}")
        print(f"[CONSENSUS] 🤖 Modelos a consultar: {models}")

        # ── FASE 1: Consultar todos los modelos en paralelo ──────────────────
        def build_solver_messages(model_idx: int):
            messages = [{"role": "system", "content": SOLVER_SYSTEM_PROMPT}]
            for h in history[-6:]:  # Últimos 6 mensajes de contexto
                messages.append(h)
            
            content = [{"type": "text", "text": f"[MATERIA: {subject}]\n\n{user_prompt}"}]
            if image_urls:
                for img_url in image_urls:
                    content.append({"type": "image_url", "image_url": {"url": img_url}})
            
            messages.append({"role": "user", "content": content})
            return messages

        async with aiohttp.ClientSession() as session:
            solver_tasks = [
                self._fetch_model(model, build_solver_messages(i), session, timeout=90)
                for i, model in enumerate(models)
            ]
            solver_responses = await asyncio.gather(*solver_tasks)

        valid_responses = [(models[i], r) for i, r in enumerate(solver_responses) if r]
        
        if not valid_responses:
            print("[CONSENSUS] ❌ TODOS los modelos fallaron. Usando respuesta de emergencia.")
            return self._emergency_response(user_prompt)

        print(f"[CONSENSUS] 📊 {len(valid_responses)}/{len(models)} modelos respondieron exitosamente")

        # ── FASE 2: Juez Supremo sintetiza el solucionario definitivo ────────
        solutions_block = ""
        for idx, (model_name, response) in enumerate(valid_responses, 1):
            solutions_block += f"\n\n=== SOLUCIÓN DEL AGENTE {idx} ({model_name}) ===\n{response}\n"

        judge_prompt = f"""Eres el JUEZ SUPREMO. Debes generar un SOLUCIONARIO ACADEMICO COMPLETO en HTML.

MATÉRIA: {subject}
PROBLEMA ORIGINAL:
{user_prompt[:1000]}

{solutions_block}

INSTRUCCIONES ABSOLUTAS:
1. Genera SOLO HTML puro. CERO markdown. CERO bloques ```html. CERO backticks.
2. Empieza directamente con <h1> o <div>, NUNCA con ``` ni con texto narrativo.
3. USA OBLIGATORIAMENTE estas clases CSS:
   - <div class="question-block"><div class="question-number">Pregunta N°X</div><div class="question-text">ENUNCIADO</div></div>
   - <div class="solution-block">DESARROLLO COMPLETO PASO A PASO</div>
   - <div class="math-block">FORMULA MATEMATICA</div>
   - <div class="answer-box"><div class="answer-label">Respuesta Final</div><div class="answer-content">RESULTADO</div></div>
4. INCLUYE TODOS los ejercicios/preguntas del examen sin excepción.
5. Para cada ejercicio: DESARROLLO COMPLETO, no resumido.
6. Las formulas matematicas van en <div class="math-block"> con notacion clara.

El HTML debe empezar AHORA, sin preambulo ni explicación:"""

        judge_messages = [
            {"role": "system", "content": JUDGE_SYSTEM_PROMPT},
            {"role": "user", "content": judge_prompt}
        ]

        async with aiohttp.ClientSession() as session:
            final_html = await self._fetch_model(
                self._get_primary_model(),
                judge_messages,
                session,
                timeout=120
            )

        if not final_html:
            # Si el juez falla, usar la mejor solución individual
            final_html = valid_responses[0][1]
            print("[CONSENSUS] ⚠️ Juez falló, usando mejor solución individual")

        # ── FASE 3: Guardar en memoria ────────────────────────────────────────
        await AsyncMemoryDB.add_message(chat_id, "user", user_prompt[:500])
        await AsyncMemoryDB.add_message(chat_id, "assistant", "[Solucionario académico generado]")

        return final_html

    def _emergency_response(self, prompt: str) -> str:
        """Respuesta de emergencia cuando todos los modelos fallan."""
        return f"""<div class="question-block">
    <div class="question-number">⚠️ Error del Sistema</div>
    <div class="question-text">{prompt[:300]}</div>
</div>
<div class="solution-block">
    <div class="note-box">⚠️ El motor de consenso no pudo obtener respuesta de ningún modelo. 
    Esto puede deberse a: API key inválida, límite de rate excedido, o problema de conectividad.
    Por favor verifica la variable OPENROUTER_API_KEY en el archivo .env y vuelve a intentarlo.</div>
</div>"""


consensus_engine = ConsensusEngine()
