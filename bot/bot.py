import asyncio
from telebot.async_telebot import AsyncTeleBot
import os
import sys

# Forzar UTF-8 para evitar UnicodeEncodeError con emojis en Windows
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.engine import engine
from core.llm_provider import llm_provider
from core.memory import AsyncMemoryDB
from core.pdf_parser import PDFParser
from core.router import router

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")
bot = AsyncTeleBot(TOKEN)

def is_admin(chat_id):
    if not ADMIN_CHAT_ID:
        return True
    return str(chat_id) == str(ADMIN_CHAT_ID)

@bot.message_handler(commands=['start'])
async def welcome(message):
    if not is_admin(message.chat.id):
        await bot.reply_to(message, "Acceso denegado. No eres el administrador.")
        return
    await bot.reply_to(message, "🦾 *ACADEMIC-OS V5.1 ASYNC* 🦾\nMotor Multi-hilo, Memoria y Visión PDF.\nEnvíame texto, fotos, audios o documentos PDF.", parse_mode="Markdown")

@bot.message_handler(commands=['clear'])
async def clear_mem(message):
    if not is_admin(message.chat.id): return
    await AsyncMemoryDB.clear_history(message.chat.id)
    await bot.reply_to(message, "🧹 Memoria borrada. Nuevo contexto iniciado.")

@bot.message_handler(content_types=['photo', 'voice', 'text', 'document'])
async def handle_input(message):
    chat_id = message.chat.id
    if not is_admin(chat_id):
        return

    try:
        await bot.send_chat_action(chat_id, 'typing')
        status_msg = await bot.reply_to(message, "⚙️ _Procesando con Motor Asíncrono de Consenso..._", parse_mode="Markdown")
        
        output_html = None
        output_pdf = None
        prompt_text = ""
        image_urls = []

        if message.content_type == 'text':
            prompt_text = message.text
            intent = await router.analyze_intent(prompt_text)
            
            if intent == "CHAT":
                history = await AsyncMemoryDB.get_history(chat_id)
                response = await llm_provider.fast_chat(prompt_text, history)
                await bot.send_message(chat_id, response)
                await AsyncMemoryDB.add_message(chat_id, "user", prompt_text)
                await AsyncMemoryDB.add_message(chat_id, "assistant", response)
                await bot.delete_message(chat_id, status_msg.message_id)
                return
            else:
                output_html, output_pdf = await engine.solve_task(chat_id, prompt_text)
            
        elif message.content_type == 'photo':
            file_info = await bot.get_file(message.photo[-1].file_id)
            file_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}"
            image_urls.append(file_url)
            prompt_text = message.caption if message.caption else "Resuelve basándote en esta imagen."
            output_html, output_pdf = await engine.solve_task(chat_id, prompt_text, image_urls=image_urls)
            
        elif message.content_type == 'document':
            file_info = await bot.get_file(message.document.file_id)
            file_name = message.document.file_name.lower()
            downloaded_file = await bot.download_file(file_info.file_path)
            
            temp_path = f"temp_{chat_id}_{file_name}"
            with open(temp_path, 'wb') as f:
                f.write(downloaded_file)
                
            prompt_text = message.caption if message.caption else f"Analiza este documento: {file_name}"
            
            if file_name.endswith('.pdf'):
                await bot.edit_message_text("👁️ _Rasterizando PDF para visión artificial..._", chat_id, status_msg.message_id, parse_mode="Markdown")
                base64_images = await asyncio.to_thread(PDFParser.extract_images_from_pdf, temp_path)
                image_urls.extend(base64_images)
                
            output_html, output_pdf = await engine.solve_task(chat_id, prompt_text, image_urls=image_urls if image_urls else None)
            os.remove(temp_path)

        elif message.content_type == 'voice':
            file_info = await bot.get_file(message.voice.file_id)
            downloaded_file = await bot.download_file(file_info.file_path)
            audio_path = f"temp_voice_{chat_id}.ogg"
            with open(audio_path, 'wb') as f:
                f.write(downloaded_file)
            
            await bot.edit_message_text("🎧 _Transcribiendo audio..._", chat_id, status_msg.message_id, parse_mode="Markdown")
            prompt_text = await llm_provider.transcribe_audio(audio_path)
            os.remove(audio_path)
            
            await bot.send_message(chat_id, f"🎤 *Transcripción:* \"_{prompt_text}_\"\n", parse_mode="Markdown")
            
            intent = await router.analyze_intent(prompt_text)
            if intent == "CHAT":
                history = await AsyncMemoryDB.get_history(chat_id)
                response = await llm_provider.fast_chat(prompt_text, history)
                await bot.send_message(chat_id, response)
                await AsyncMemoryDB.add_message(chat_id, "user", prompt_text)
                await AsyncMemoryDB.add_message(chat_id, "assistant", response)
                return
            else:
                await bot.send_message(chat_id, "⚙️ Generando solucionario matemático...")
                output_html, output_pdf = await engine.solve_task(chat_id, prompt_text)
            
        # Envío final de archivos
        if output_pdf and os.path.exists(output_pdf):
            with open(output_pdf, "rb") as f:
                await bot.send_document(chat_id, f, caption="✅ Solucionario en formato PDF Premium.")
        elif output_html and os.path.exists(output_html):
            with open(output_html, "rb") as f:
                await bot.send_document(chat_id, f, caption="✅ Solucionario (HTML, fallo en conversión PDF).")
        else:
            await bot.send_message(chat_id, "⚠️ Error en la generación del solucionario.")
            
        # Limpiar estado
        try:
            await bot.delete_message(chat_id, status_msg.message_id)
        except:
            pass
            
    except Exception as e:
        await bot.reply_to(message, f"⚠️ Error Crítico: {e}")

async def main():
    await AsyncMemoryDB.init_db()
    print("🛡️ AGENTE @tdsoficialbot EN LÍNEA (ASYNC V5.1) 🛡️")
    await bot.infinity_polling()

if __name__ == "__main__":
    asyncio.run(main())

