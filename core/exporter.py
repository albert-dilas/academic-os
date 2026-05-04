from xhtml2pdf import pisa
import os

class PDFExporter:
    @staticmethod
    def convert_html_to_pdf(source_html_path, output_pdf_path):
        """Convierte archivo HTML a PDF usando xhtml2pdf."""
        try:
            with open(source_html_path, "r", encoding="utf-8") as f:
                source_html = f.read()

            with open(output_pdf_path, "wb") as output_file:
                # pisa.CreatePDF compila el HTML
                pisa_status = pisa.CreatePDF(
                    src=source_html,
                    dest=output_file
                )

            return not pisa_status.err
        except Exception as e:
            print(f"[EXPORTER] Error compilando PDF: {e}")
            return False
