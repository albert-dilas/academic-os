"""
PDFExporter — Academic-OS V5.1
Estrategia de exportación en capas:
  1. xhtml2pdf (disponible, CSS básico + Unicode math)
  2. Fallback PyMuPDF si falla xhtml2pdf
Nota: WeasyPrint es la opción ideal pero requiere GTK en Windows.
Si se instala WeasyPrint correctamente, el sistema lo usará automáticamente.
"""
import os
import re
from datetime import datetime


# ─── CSS ACADÉMICO PREMIUM (Compatible con xhtml2pdf) ──────────────────────
# xhtml2pdf soporta CSS 2.1 + algunas extensiones propietarias
ACADEMIC_CSS_PDF = """
/* Reset básico */
* { margin: 0; padding: 0; box-sizing: border-box; }

/* Página A4 */
@page {
    size: A4 portrait;
    margin: 2.5cm 2cm 2.5cm 2cm;
    @frame footer_frame {
        -pdf-frame-content: footer;
        left: 2cm; right: 2cm; bottom: 1.5cm; height: 0.8cm;
    }
}

body {
    font-family: Helvetica, Arial, sans-serif;
    font-size: 10.5pt;
    line-height: 1.6;
    color: #1a1a2e;
}

/* Portada */
.cover-page {
    text-align: center;
    padding: 3cm 2cm;
    background-color: #1a237e;
    color: #ffffff;
    min-height: 26cm;
}

.cover-logo {
    font-size: 36pt;
    margin-bottom: 0.5cm;
    color: #ffffff;
}

.cover-system {
    font-size: 9pt;
    letter-spacing: 3px;
    color: #9fa8da;
    margin-bottom: 1cm;
}

.cover-title {
    font-size: 22pt;
    font-weight: bold;
    line-height: 1.3;
    margin: 1cm 0;
    color: #ffffff;
}

.cover-divider {
    border-top: 3px solid #f57f17;
    width: 60px;
    margin: 0.5cm auto;
}

.cover-meta {
    font-size: 9pt;
    color: #c5cae9;
    margin-top: 0.5cm;
}

/* Encabezados */
h1 {
    font-family: Georgia, serif;
    font-size: 16pt;
    color: #1a237e;
    border-bottom: 2pt solid #1565c0;
    padding-bottom: 4pt;
    margin-top: 1cm;
    margin-bottom: 0.4cm;
}

h2 {
    font-size: 13pt;
    font-weight: bold;
    color: #283593;
    margin-top: 0.8cm;
    margin-bottom: 0.3cm;
    padding-left: 6pt;
    border-left: 3pt solid #f57f17;
}

h3 {
    font-size: 11pt;
    font-weight: bold;
    color: #1565c0;
    margin-top: 0.5cm;
    margin-bottom: 0.2cm;
}

/* Bloques de pregunta */
.question-block {
    background-color: #f8f9ff;
    border: 1pt solid #c5cae9;
    border-left: 4pt solid #1565c0;
    padding: 0.5cm 0.6cm;
    margin-top: 0.7cm;
    margin-bottom: 0.2cm;
}

.question-number {
    font-size: 8pt;
    font-weight: bold;
    color: #1565c0;
    letter-spacing: 2px;
    margin-bottom: 3pt;
}

.question-text {
    font-size: 11pt;
    font-style: italic;
    color: #1a1a2e;
    line-height: 1.5;
}

/* Desarrollo de solución */
.solution-block {
    background-color: #ffffff;
    border: 1pt solid #e8eaf6;
    padding: 0.5cm 0.6cm;
    margin-bottom: 0.4cm;
}

/* Fórmulas matemáticas */
.math-block {
    background-color: #fafafa;
    border: 1pt solid #e0e0e0;
    border-left: 3pt solid #f57f17;
    padding: 0.3cm 0.5cm;
    margin: 0.3cm 0;
    font-family: "Courier New", Courier, monospace;
    font-size: 10pt;
    color: #1a1a2e;
}

/* Caja de respuesta final */
.answer-box {
    background-color: #e8f5e9;
    border: 2pt solid #2e7d32;
    padding: 0.4cm 0.6cm;
    margin-top: 0.3cm;
    margin-bottom: 0.7cm;
}

.answer-label {
    font-size: 8pt;
    font-weight: bold;
    color: #1b5e20;
    letter-spacing: 2px;
    margin-bottom: 3pt;
}

.answer-content {
    font-size: 12pt;
    font-weight: bold;
    color: #1b5e20;
    font-family: Georgia, serif;
}

/* Notas */
.note-box {
    background-color: #fff8e1;
    border-left: 3pt solid #f57f17;
    padding: 0.3cm 0.5cm;
    margin: 0.3cm 0;
    font-size: 9.5pt;
    color: #5d4037;
}

/* Tablas */
table {
    width: 100%;
    border-collapse: collapse;
    margin: 0.4cm 0;
    font-size: 9.5pt;
}

th {
    background-color: #1a237e;
    color: #ffffff;
    padding: 5pt 8pt;
    text-align: left;
}

td {
    padding: 4pt 8pt;
    border-bottom: 1pt solid #c5cae9;
}

/* Pie de página */
#footer {
    text-align: center;
    font-size: 7.5pt;
    color: #7986cb;
    border-top: 0.5pt solid #c5cae9;
    padding-top: 4pt;
}

p { margin: 0.15cm 0; }
strong { color: #1a237e; }
code {
    font-family: "Courier New", Courier, monospace;
    font-size: 9pt;
    background-color: #f5f5f5;
    padding: 1pt 3pt;
}
"""


def clean_for_pdf(html_content: str) -> str:
    """
    Limpia el HTML para compatibilidad máxima con xhtml2pdf.
    """
    # Eliminar bloques markdown y scripts
    html_content = re.sub(r'```(?:html)?', '', html_content)
    html_content = re.sub(r'```', '', html_content)
    html_content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
    
    # Mapeo agresivo de LaTeX a Unicode para xhtml2pdf
    replacements = [
        (r'\\frac\{(.*?)\}\{(.*?)\}', r'(\1)/(\2)'),
        (r'\\sqrt\{(.*?)\}', r'√(\1)'),
        (r'\\text\{(.*?)\}', r'\1'),
        (r'\\left\(', '('), (r'\\right\)', ')'),
        (r'\\left\[', '['), (r'\\right\]', ']'),
        (r'\\alpha', 'α'), (r'\\beta', 'β'), (r'\\gamma', 'γ'), (r'\\pi', 'π'),
        (r'\\theta', 'θ'), (r'\\lambda', 'λ'), (r'\\delta', 'δ'), (r'\\Delta', 'Δ'),
        (r'\\sigma', 'σ'), (r'\\omega', 'ω'), (r'\\infty', '∞'), (r'\\pm', '±'),
        (r'\\neq', '≠'), (r'\\approx', '≈'), (r'\\leq', '≤'), (r'\\geq', '≥'),
        (r'\\times', '×'), (r'\\cdot', '·'), (r'\\div', '÷'),
        (r'\\rightarrow', '→'), (r'\\forall', '∀'), (r'\\exists', '∃'),
        (r'\\\{', '{'), (r'\\\}', '}'),
        (r'\\\[', ''), (r'\\\]', ''), (r'\\\(', ''), (r'\\\)', ''),
        (r'\^\{(.*?)\}', r'<sup>\1</sup>'),
        (r'\_\{(.*?)\}', r'<sub>\1</sub>'),
        (r'\^(\d)', r'<sup>\1</sup>'),
        (r'\_(\d)', r'<sub>\1</sub>'),
    ]
    
    for pattern, repl in replacements:
        html_content = re.sub(pattern, repl, html_content)

    # Limpiar delimitadores de dólares residuales
    html_content = html_content.replace('$$', '').replace('$', '')
    
    return html_content.strip()


def wrap_in_academic_template(content: str, title: str = "Solucionario Académico") -> str:
    """Envuelve el contenido en plantilla HTML académica premium."""
    date_str = datetime.now().strftime("%d/%m/%Y - %H:%M")
    cleaned_content = clean_for_pdf(content)
    
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8"/>
    <title>{title}</title>
    <style>{ACADEMIC_CSS_PDF}</style>
</head>
<body>
    <!-- PORTADA -->
    <div class="cover-page">
        <div class="cover-logo">&#128218;</div>
        <div class="cover-system">ACADEMIC-OS - SISTEMA AUTONOMO DE IA</div>
        <br/><br/>
        <div class="cover-title">{title}</div>
        <br/>
        <div class="cover-meta">Generado: {date_str} | Motor de Consenso Multi-Modelo - V5.1 Professional</div>
    </div>
    
    <!-- SALTO DE PAGINA DESPUES DE PORTADA -->
    <pdf:nextpage/>
    
    <!-- CONTENIDO ACADEMICO -->
    {cleaned_content}

    <!-- PIE DE PAGINA -->
    <div id="footer">
        Academic-OS V5.1 - Generado automaticamente con IA - {date_str}
    </div>
</body>
</html>"""


class PDFExporter:
    @staticmethod
    def convert_html_to_pdf(source_html_path: str, output_pdf_path: str) -> bool:
        """
        Convierte HTML académico a PDF.
        Prioridad: WeasyPrint → xhtml2pdf → PyMuPDF fallback
        """
        # Intentar WeasyPrint primero (mejor calidad)
        try:
            from weasyprint import HTML
            with open(source_html_path, "r", encoding="utf-8") as f:
                html_content = f.read()
            HTML(string=html_content).write_pdf(output_pdf_path)
            print(f"[EXPORTER] ✅ PDF WeasyPrint: {output_pdf_path}")
            return True
        except ImportError:
            pass  # WeasyPrint no disponible, continuar
        except Exception as e:
            print(f"[EXPORTER] ⚠️ WeasyPrint falló: {e}")

        # xhtml2pdf (disponible en el entorno)
        try:
            from xhtml2pdf import pisa
            with open(source_html_path, "r", encoding="utf-8") as f:
                source_html = f.read()
            with open(output_pdf_path, "wb") as output_file:
                pisa_status = pisa.CreatePDF(
                    src=source_html,
                    dest=output_file,
                    encoding='utf-8'
                )
            if not pisa_status.err:
                print(f"[EXPORTER] ✅ PDF xhtml2pdf: {output_pdf_path}")
                return True
            else:
                print(f"[EXPORTER] ⚠️ xhtml2pdf reportó {pisa_status.err} errores")
                return True  # Aún generar el PDF aunque haya advertencias menores
        except Exception as e:
            print(f"[EXPORTER] ❌ xhtml2pdf falló: {e}")

        # Fallback final: PyMuPDF texto plano
        return PDFExporter._fallback_fitz(source_html_path, output_pdf_path)

    @staticmethod
    def _fallback_fitz(source_html_path: str, output_pdf_path: str) -> bool:
        """Fallback de emergencia: PDF de texto plano con PyMuPDF."""
        try:
            import fitz
            with open(source_html_path, "r", encoding="utf-8") as f:
                html_content = f.read()

            # Extraer texto limpio del HTML
            text = re.sub(r'<[^>]+>', '\n', html_content)
            text = re.sub(r'\n{3,}', '\n\n', text).strip()

            doc = fitz.open()
            page = doc.new_page(width=595, height=842)  # A4

            # Insertar texto en el PDF
            lines = text.split('\n')
            y = 72
            for line in lines:
                line = line.strip()
                if not line:
                    y += 8
                    continue
                if y > 770:
                    page = doc.new_page(width=595, height=842)
                    y = 72
                page.insert_text((50, y), line[:100], fontsize=9, color=(0.1, 0.1, 0.2))
                y += 13

            doc.save(output_pdf_path)
            doc.close()
            print(f"[EXPORTER] ✅ PDF fallback (texto): {output_pdf_path}")
            return True
        except Exception as e:
            print(f"[EXPORTER] ❌ Fallback también falló: {e}")
            return False

    @staticmethod
    def wrap_content(raw_content: str, title: str = "Solucionario Académico") -> str:
        """Empaqueta contenido crudo en plantilla académica completa."""
        return wrap_in_academic_template(raw_content, title)
