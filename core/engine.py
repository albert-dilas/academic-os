from core.consensus import consensus_engine
from core.auditor import auditor
from core.exporter import PDFExporter
import os

class AcademicEngine:
    def __init__(self):
        self.output_dir = "archivos"
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    async def solve_task(self, chat_id, raw_text, image_urls=None, attempt=1, max_retries=3):
        print(f"🧠 INICIANDO CONSENSO SUPREMO (Intento {attempt}/{max_retries})...")
        
        prompt = f"Resuelve con máximo rigor académico. Si es matemáticas/ciencias: usa desarrollo matemático directo en bloques, sin narrativa paso a paso. Si es letras/comprensión: redacción analítica experta y argumentada. Requerimiento HTML estricto. Petición: {raw_text}"
        final_solution = await consensus_engine.resolve(prompt, chat_id, image_urls=image_urls)
        
        # Auditoría de Calidad
        is_perfect, report = auditor.audit_html(final_solution, is_path=False)
        
        if is_perfect or attempt >= max_retries:
            html_path = os.path.join(self.output_dir, f"SOLUCIONARIO_{chat_id}.html")
            pdf_path = os.path.join(self.output_dir, f"SOLUCIONARIO_{chat_id}.pdf")
            
            # Forzar empaquetado HTML si el LLM falló repetidamente en generarlo
            if "<html>" not in final_solution.lower():
                final_solution = f"<html><head><meta charset='utf-8'></head><body>{final_solution}</body></html>"

            with open(html_path, "w", encoding="utf-8") as f:
                f.write(final_solution)
            
            # Exportar a PDF (Sin bloquear el Event Loop)
            import asyncio
            success_pdf = await asyncio.to_thread(PDFExporter.convert_html_to_pdf, html_path, pdf_path)
            
            if not is_perfect:
                print("⚠️ Se alcanzó el límite de reintentos. Guardando mejor esfuerzo.")
            else:
                print(f"✅ Tarea resuelta y auditada.")
                
            return html_path, (pdf_path if success_pdf else None)
        else:
            print(f"⚠️ Calidad insuficiente: {report}. Reintentando...")
            return await self.solve_task(chat_id, raw_text, image_urls, attempt + 1, max_retries)

engine = AcademicEngine()

