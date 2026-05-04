"""
PDFParser — Academic-OS V5.1
Extrae contenido de PDFs académicos:
  - Imágenes de alta resolución (para visión de IA)
  - Texto extraído (como contexto adicional para los modelos)
"""
import fitz  # PyMuPDF
import base64
import os


class PDFParser:
    @staticmethod
    def extract_images_from_pdf(pdf_path: str, max_pages: int = 15, output_dir: str = "archivos") -> list[str]:
        """
        Convierte cada página del PDF en imagen PNG Base64 y guarda el archivo físico.
        Retorna lista de data-URLs.
        """
        base64_images = []
        os.makedirs(output_dir, exist_ok=True)
        try:
            doc = fitz.open(pdf_path)
            num_pages = min(len(doc), max_pages)
            print(f"[PDF_PARSER] 📄 Rasterizando {num_pages}/{len(doc)} páginas...")

            for page_num in range(num_pages):
                page = doc.load_page(page_num)
                mat = fitz.Matrix(2.5, 2.5)
                pix = page.get_pixmap(matrix=mat)
                
                # Guardar imagen física para el PDF
                img_name = f"ref_page_{page_num + 1}.png"
                img_path = os.path.join(output_dir, img_name)
                pix.save(img_path)

                img_data = pix.tobytes("png")
                b64 = base64.b64encode(img_data).decode("utf-8")
                base64_images.append(f"data:image/png;base64,{b64}")
                print(f"[PDF_PARSER] ✅ Página {page_num + 1} guardada como {img_name}")

            doc.close()
        except Exception as e:
            print(f"[PDF_PARSER] ❌ Error rasterizando: {e}")

        return base64_images

    @staticmethod
    def extract_text_from_pdf(pdf_path: str, max_pages: int = 15) -> str:
        """
        Extrae el texto digital del PDF (si no es imagen escaneada).
        Útil como contexto adicional para los modelos de lenguaje.
        """
        full_text = []
        try:
            doc = fitz.open(pdf_path)
            num_pages = min(len(doc), max_pages)

            for page_num in range(num_pages):
                page = doc.load_page(page_num)
                text = page.get_text("text").strip()
                if text:
                    full_text.append(f"[Página {page_num + 1}]\n{text}")

            doc.close()
            
            combined = "\n\n".join(full_text)
            if combined.strip():
                print(f"[PDF_PARSER] 📝 Texto extraído: {len(combined)} chars")
            else:
                print(f"[PDF_PARSER] ℹ️ PDF sin texto digital (probablemente escaneado)")
            return combined

        except Exception as e:
            print(f"[PDF_PARSER] ❌ Error extrayendo texto: {e}")
            return ""

    @staticmethod
    def extract_full_content(pdf_path: str, max_pages: int = 15) -> tuple[list[str], str]:
        """
        Extrae tanto imágenes como texto del PDF.
        Returns: (list_of_base64_images, extracted_text)
        """
        images = PDFParser.extract_images_from_pdf(pdf_path, max_pages)
        text = PDFParser.extract_text_from_pdf(pdf_path, max_pages)
        return images, text
