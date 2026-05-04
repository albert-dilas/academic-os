import asyncio
import os
import sys
import io

# Forzar UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from dotenv import load_dotenv
load_dotenv()

from core.pdf_parser import PDFParser
from core.engine import engine
from core.memory import AsyncMemoryDB

async def test():
    pdf_path = r'c:\Users\Albert\Documents\opencode\TD - 5.° CAT - 8 - I BIM - 26.pdf'
    chat_id = 7777777
    
    await AsyncMemoryDB.init_db()
    
    print("--- EXTRAYENDO CONTENIDO ---")
    images, text = PDFParser.extract_full_content(pdf_path, max_pages=11)
    print(f"Texto extraído ({len(text)} chars)")
    print(f"Imágenes extraídas ({len(images)})")
    
    prompt = "Resuelve todos los ejercicios de este examen. Desarrollo completo. Usa el formato HTML académico."
    if text:
        prompt += f"\n\nCONTENIDO:\n{text}"
    
    print("--- INICIANDO MOTOR ---")
    html_path, pdf_path = await engine.solve_task(chat_id, prompt, image_urls=images)
    
    print(f"HTML generado en: {html_path}")
    print(f"PDF generado en: {pdf_path}")
    
    if pdf_path and os.path.exists(pdf_path):
        print(f"TAMAÑO PDF: {os.path.getsize(pdf_path)} bytes")

if __name__ == "__main__":
    asyncio.run(test())
