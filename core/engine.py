"""
AcademicEngine — Academic-OS V5.1
Orquesta el pipeline completo: consenso → auditoría → exportación premium.
"""
import asyncio
import os
import re

from core.consensus import consensus_engine
from core.auditor import auditor
from core.exporter import PDFExporter


def extract_title_from_prompt(prompt: str) -> str:
    """Infiere un título académico del prompt."""
    # Patrones comunes en tareas escolares
    patterns = [
        r'(examen|prueba|tarea|práctica|trabajo|guía|solucionario)\s+(?:de\s+)?(.{5,50}?)(?:\.|,|$)',
        r'(matemáticas?|física|química|biología|historia|lenguaje|comunicación)\s+.{0,30}',
    ]
    for pattern in patterns:
        match = re.search(pattern, prompt.lower())
        if match:
            return match.group(0).title().strip()[:80]
    
    # Truncar el prompt como título si es corto
    clean = re.sub(r'<[^>]+>', '', prompt).strip()
    if len(clean) <= 80:
        return clean.title()
    return clean[:77] + "..."


class AcademicEngine:
    def __init__(self):
        self.output_dir = "archivos"
        os.makedirs(self.output_dir, exist_ok=True)

    async def solve_task(
        self,
        chat_id: int,
        raw_text: str,
        image_urls: list = None,
        attempt: int = 1,
        max_retries: int = 2
    ) -> tuple[str | None, str | None]:
        """
        Pipeline principal de resolución académica.
        Returns: (html_path, pdf_path) — pdf_path puede ser None si falla la conversión.
        """
        print(f"[ENGINE] 🧠 Iniciando motor de consenso (intento {attempt}/{max_retries})...")

        # ── PASO 1: Construir prompt enriquecido ─────────────────────────────
        enriched_prompt = (
            f"TAREA ACADÉMICA A RESOLVER CON MÁXIMO RIGOR:\n\n"
            f"{raw_text}\n\n"
            f"INSTRUCCIONES: Resuelve TODOS los ítems/preguntas. "
            f"Muestra desarrollo completo paso a paso. "
            f"No omitas ningún ejercicio. "
            f"Usa formato HTML académico con las clases CSS especificadas."
        )

        # ── PASO 2: Motor de consenso ────────────────────────────────────────
        final_html_content = await consensus_engine.resolve(
            enriched_prompt,
            chat_id,
            image_urls=image_urls
        )

        # ── PASO 3: Limpiar markdown residual del LLM ─────────────────────────
        # Gemini a veces envuelve su respuesta en ```html ... ``` aunque se le pida HTML puro
        final_html_content = auditor.strip_markdown(final_html_content)

        # ── PASO 4: Auditoría de calidad ─────────────────────────────────────
        is_acceptable, report = auditor.audit_content(final_html_content)
        print(f"[ENGINE] 📋 Auditoría: {report}")

        if not is_acceptable and attempt < max_retries:
            print(f"[ENGINE] 🔄 Calidad insuficiente. Reintentando ({attempt + 1}/{max_retries})...")
            return await self.solve_task(chat_id, raw_text, image_urls, attempt + 1, max_retries)

        # ── PASO 4: Empaquetar en plantilla académica premium ────────────────
        title = extract_title_from_prompt(raw_text)
        full_html = PDFExporter.wrap_content(final_html_content, title=title)

        # ── PASO 5: Guardar HTML ─────────────────────────────────────────────
        html_path = os.path.join(self.output_dir, f"SOLUCIONARIO_{chat_id}.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(full_html)

        # ── PASO 6: Convertir a PDF premium ──────────────────────────────────
        pdf_path = os.path.join(self.output_dir, f"SOLUCIONARIO_{chat_id}.pdf")
        success_pdf = await asyncio.to_thread(
            PDFExporter.convert_html_to_pdf, html_path, pdf_path
        )

        if success_pdf:
            print(f"[ENGINE] ✅ Solucionario PDF premium listo: {pdf_path}")
        else:
            print(f"[ENGINE] ⚠️ PDF falló, entregando HTML como respaldo: {html_path}")

        return html_path, (pdf_path if success_pdf else None)


engine = AcademicEngine()
