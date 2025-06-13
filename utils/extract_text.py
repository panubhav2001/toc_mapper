import fitz  # PyMuPDF
from pdf2image import convert_from_path
import pytesseract

def is_scanned_pdf(pdf_path):
    try:
        img = convert_from_path(pdf_path, first_page=1, last_page=1)[0]
        text = pytesseract.image_to_string(img)
        return len(text.strip()) < 20
    except Exception as e:
        print("Error detecting scan status:", e)
        return False

def extract_pdf_text(pdf_path):
    scanned = is_scanned_pdf(pdf_path)
    pages_text = {}

    if not scanned:
        doc = fitz.open(pdf_path)
        for i in range(len(doc)):
            pages_text[i] = doc[i].get_text()
    else:
        images = convert_from_path(pdf_path)
        for i, img in enumerate(images):
            pages_text[i] = pytesseract.image_to_string(img)

    return pages_text, scanned