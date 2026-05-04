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

async def test_letras():
    pdf_path = r'c:\Users\Albert\Documents\opencode\TD - 5.° CAT - 8 - I BIM - 26.pdf'
    chat_id = 8888888
    
    await AsyncMemoryDB.init_db()
    
    # Extraer solo las páginas de Letras y Física (7 a 11)
    images, text = PDFParser.extract_full_content(pdf_path, max_pages=11)
    # Filtrar texto para solo enviar la parte final
    final_text = text[len(text)//2:] # Aproximación de la segunda mitad
    final_images = images[6:] # Páginas 7 a 11
    
    prompt = (
        "Resuelve ÚNICAMENTE las secciones de FÍSICA y LETRAS (Ortografía, Vocabulario y Lectura Crítica). "
        "Muestra análisis profundo en las lecturas y desarrollo técnico en Física. "
        "Usa el formato HTML académico premium."
    )
    
    print("--- INICIANDO MOTOR (PARTE LETRAS/FÍSICA) ---")
    html_path, pdf_path = await engine.solve_task(chat_id, prompt, image_urls=final_images)
    
    print(f"HTML generado en: {html_path}")
    print(f"PDF generado en: {pdf_path}")

if __name__ == "__main__":
    asyncio.run(test_letras())
