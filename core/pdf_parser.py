import fitz  # PyMuPDF
import base64
import os

class PDFParser:
    @staticmethod
    def extract_images_from_pdf(pdf_path, max_pages=10):
        """
        Convierte cada página del PDF en una imagen PNG codificada en Base64.
        Devuelve una lista de strings con formato data URL.
        """
        base64_images = []
        try:
            doc = fitz.open(pdf_path)
            # Limitamos para no saturar tokens
            num_pages = min(len(doc), max_pages)
            
            for page_num in range(num_pages):
                page = doc.load_page(page_num)
                # zoom x2 para mejor legibilidad de ecuaciones
                mat = fitz.Matrix(2, 2)
                pix = page.get_pixmap(matrix=mat)
                img_data = pix.tobytes("png")
                
                b64 = base64.b64encode(img_data).decode("utf-8")
                base64_images.append(f"data:image/png;base64,{b64}")
                
            doc.close()
        except Exception as e:
            print(f"[PDF_VISION] Error: {e}")
            
        return base64_images

