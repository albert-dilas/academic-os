"""
HTMLAuditor -- Academic-OS V5.1
Verificador de calidad real para solucionarios academicos.
Evalua longitud, estructura HTML y detecta errores comunes del LLM.
"""
import re
import os


class HTMLAuditor:
    MIN_CONTENT_LENGTH = 800

    @staticmethod
    def strip_markdown(content: str) -> str:
        """
        Extrae HTML puro de respuestas envueltas en bloques markdown.
        Ejemplo: ```html\\n<div>...</div>\\n``` -> <div>...</div>
        """
        stripped = content.strip()

        # Patron completo: ```html ... ``` o ``` ... ```
        md_match = re.match(r'^```(?:html)?\s*\n?(.*?)\n?```\s*$', stripped, re.DOTALL)
        if md_match:
            return md_match.group(1).strip()

        # Solo marcador de apertura
        if stripped.startswith('```html'):
            stripped = stripped[7:].lstrip()
        elif stripped.startswith('```'):
            stripped = stripped[3:].lstrip()

        # Solo marcador de cierre
        if stripped.endswith('```'):
            stripped = stripped[:-3].rstrip()

        return stripped

    @staticmethod
    def audit_content(content: str) -> tuple:
        """
        Audita el contenido generado.
        Returns: (is_acceptable: bool, report: str)
        """
        issues = []

        # Texto limpio para medir longitud
        clean_text = re.sub(r'<[^>]+>', ' ', content)
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        content_length = len(clean_text)
        content_lower = content.lower()

        # 1. Longitud minima
        if content_length < HTMLAuditor.MIN_CONTENT_LENGTH:
            issues.append(
                "Contenido demasiado corto ({} chars, minimo {})".format(
                    content_length, HTMLAuditor.MIN_CONTENT_LENGTH
                )
            )

        # 2. Detectar errores de API embebidos en la respuesta
        if content_length < 500:
            for kw in ['api key', 'unauthorized', 'rate limit', 'invalid model']:
                if kw in content_lower:
                    issues.append("Error de API detectado: '{}'".format(kw))
                    break

        # 3. Markdown residual no limpiado
        if content.strip().startswith('```'):
            issues.append("Markdown residual no limpiado correctamente")

        # 4. Estructura HTML minima obligatoria
        has_html_tags = bool(
            re.search(r'<(div|p|h[1-6]|ul|ol|table|section)', content, re.IGNORECASE)
        )
        if not has_html_tags:
            issues.append("Sin estructura HTML (contenido es texto plano)")

        # 5. Deteccion de rechazo del modelo
        if content_length < 600:
            refusal_phrases = [
                "no puedo", "no me es posible",
                "i cannot", "i'm unable", "as an ai"
            ]
            for phrase in refusal_phrases:
                if phrase in content_lower:
                    issues.append("Modelo rechazo la peticion: '{}'".format(phrase))
                    break

        # -- Fallo
        if issues:
            report = "Calidad insuficiente: " + " | ".join(issues)
            print("[AUDITOR] WARN: " + report)
            return False, report

        # -- Exito: generar metricas
        has_math = bool(
            re.search(r'(\$\$|\\\[|\\\(|MathJax|\\sqrt|\\frac|\\times|[\u2200-\u22FF])', content, re.IGNORECASE) or
            re.search(r'math-block', content, re.IGNORECASE)
        )
        has_answers = bool(
            re.search(r'(answer-box|respuesta.final|✅ respuesta)', content, re.IGNORECASE)
        )

        report = "OK | {} chars | Math: {} | Respuestas: {}".format(
            content_length,
            "Si" if has_math else "No",
            "Si" if has_answers else "No"
        )
        print("[AUDITOR] " + report)
        return True, report

    @staticmethod
    def audit_html(content: str, is_path: bool = False) -> tuple:
        """Compatibilidad con llamadas antiguas que usaban audit_html."""
        if is_path:
            if not os.path.exists(content):
                return False, "El archivo no existe."
            with open(content, 'r', encoding='utf-8') as f:
                content = f.read()
        return HTMLAuditor.audit_content(content)


auditor = HTMLAuditor()
