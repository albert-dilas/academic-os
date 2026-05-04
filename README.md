# Academic-OS V5.1 (Autonomous Multi-Agent System)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3110/)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://GitHub.com/albert-dilas/academic-os/graphs/commit-activity)
[![Render](https://img.shields.io/badge/Deploy%20to-Render-46E3B7?logo=render&logoColor=white)](https://render.com)

Academic-OS es un ecosistema robótico autónomo diseñado para operar 24/7 como tutor experto en Telegram. Utiliza una arquitectura de **consenso multi-modelo** para garantizar el máximo rigor en tareas de ciencias, matemáticas y letras.

---

## 🚀 Tabla de Contenidos
*   [Características Principales](#-características-principales)
*   [Arquitectura Técnica](#-arquitectura-técnica)
*   [Configuración de Modelos (Universalidad)](#-configuración-de-modelos-universalidad)
*   [Guía de Despliegue Cloud (24/7 Gratis)](#-guía-de-despliegue-cloud-247-gratis)
*   [Instalación Local](#-instalación-local)
*   [Seguridad](#-seguridad)
*   [Contribución](#-contribución)

---

## 🌟 Características Principales
*   **Enrutador Semántico:** Distingue inteligentemente entre charla trivial y problemas complejos para optimizar tokens y tiempos de respuesta.
*   **Consenso de LLMs Avanzado:** Usa un Juez Supremo para verificar, auditar y limpiar los resultados antes de entregarlos al usuario.
*   **Soporte Multimodal Asíncrono:** Extrae texto de imágenes, rasteriza páginas de archivos PDF de gran volumen y transcribe audio en paralelo sin bloquear el bot.
*   **Exportación Premium:** Genera hojas de respuesta compiladas en formato `.pdf` con soporte nativo para bloques de MathJax.

## Arquitectura de Componentes
*   `bot.py`: Punto de entrada asíncrono y gestor de eventos de Telegram.
*   `core/engine.py`: Motor de flujo lógico.
*   `core/llm_provider.py`: Proveedor unificado de inferencia de IA.
*   `core/consensus.py`: Motor de consenso y auditoría estructural múltiple.
*   `core/auditor.py`: Verificador de calidad de salidas HTML/LaTeX.
*   `core/pdf_parser.py`: Rasterizador visual de documentos.
*   `core/router.py`: Clasificador de intención.
*   `core/memory.py`: Gestor SQLite para contexto local.

## Guía Rápida de Despliegue en la Nube (Render.com / Railway)
Este repositorio está estructurado para despliegue instantáneo (True Serverless 24/7).

1. Crea una cuenta en [Render.com](https://render.com/).
2. Conecta este repositorio y crea un **Background Worker** (Trabajador en Segundo Plano).
3. En la sección *Build Command*, usa: `pip install -r requirements.txt`
4. Render detectará automáticamente el archivo `Procfile`.
5. **CRÍTICO:** En las variables de entorno de Render, debes añadir:
   * `TELEGRAM_TOKEN` (Tu token del Botfather).
   * `OPENROUTER_API_KEY` (Token para Gemini/Claude).
   * `GROQ_API_KEY` (Token para Groq Whisper Audio).
   * `ADMIN_CHAT_ID` (Tu ID de Telegram para uso exclusivo).
   * `PRIMARY_MODEL` (Opcional. Ej: `google/gemini-2.0-flash-001`).
   * `CONSENSUS_MODELS` (Opcional. Ej: `google/gemini-2.0-flash-001,anthropic/claude-3.5-sonnet`).

## Modelos AI Soportados (Universalidad)
Dado que el bot usa OpenRouter como proveedor, **no estás limitado a ningún modelo**. Puedes usar modelos gratuitos, de código abierto o premium simplemente cambiando las variables de entorno `PRIMARY_MODEL` y `CONSENSUS_MODELS`.
* **Para usar IA 100% gratuita:**
  - `PRIMARY_MODEL=google/gemini-2.0-flash-lite-preview-02-05:free`
  - `CONSENSUS_MODELS=google/gemini-2.0-flash-lite-preview-02-05:free,meta-llama/llama-3-8b-instruct:free`
* **Para usar Premium Extremo:**
  - `PRIMARY_MODEL=openai/gpt-4o`
  - `CONSENSUS_MODELS=openai/gpt-4o,anthropic/claude-3.5-sonnet`

## Instalación Local de Desarrollo
1. Clona el repositorio.
2. Instala dependencias: `pip install -r requirements.txt`.
3. Crea un archivo `.env` basado en la sección anterior.
4. Ejecuta `python bot/bot.py` o corre el script local de alta disponibilidad: `./scripts/watchdog.ps1`.

---

## 🛡️ Seguridad
*   **Variables de Entorno:** El archivo `.env` está explícitamente excluido vía `.gitignore` para prevenir fugas de API Keys.
*   **Sanitización:** Los procesos de auditoría internos verifican la calidad de las respuestas antes de la entrega final.

## 🤝 Contribución
¡Las contribuciones son lo que hacen que la comunidad de código abierto sea un lugar increíble para aprender, inspirar y crear! Cualquier contribución que hagas será **muy apreciada**. Por favor, revisa `CONTRIBUTING.md` para más detalles.

---
*Desarrollado para la resolución de tareas académicas complejas sin intervención humana.*
