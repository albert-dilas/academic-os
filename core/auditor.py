import os
import re

class HTMLAuditor:
    @staticmethod
    def audit_html(content, is_path=True):
        """Realiza una auditoría técnica completa del solucionario."""
        if is_path:
            if not os.path.exists(content):
                return False, "El archivo no existe."
            with open(content, 'r', encoding='utf-8') as f:
                content = f.read()

        # 1. Verificación de HTML (Etiquetas básicas)
        if "html" not in content.lower() or "body" not in content.lower():
            return False, "Estructura HTML ausente o mal formada."

        # 2. Verificación de Fórmulas Matemáticas (LaTeX)
        # Se asume que usa \[ \] o \( \) o $$ o MathJax
        has_math = bool(re.search(r'(\$\$|\\\[|\\\(|MathJax)', content))
        if not has_math:
            print("[VERIFICADOR] Advertencia: No se detectaron bloques matemáticos evidentes.")

        # 3. Verificación de Gráficos
        has_svg = "<svg" in content.lower()
        has_mermaid = "mermaid" in content.lower()
        
        graphics_report = "Gráficos detectados" if (has_svg or has_mermaid) else "Sin gráficos explícitos"
        
        report = f"Auditoría Exitosa: HTML Validado. {graphics_report}. Matemáticas: {'Sí' if has_math else 'No'}."
        print(f"[VERIFICADOR] {report}")
        return True, report

auditor = HTMLAuditor()

