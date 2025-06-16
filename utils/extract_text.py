import fitz  # PyMuPDF
from google.api_core.client_options import ClientOptions
from google.cloud import documentai_v1
import os

from PyPDF2 import PdfReader, PdfWriter
from tempfile import NamedTemporaryFile


def is_scanned_pdf(pdf_path, text_threshold=0.8, min_chars=20, image_threshold=0.6, sample_pages=5):
    """
    Detects if a PDF is likely scanned (image-based) or digital (text-based).
    """
    doc = fitz.open(pdf_path)
    total_pages = len(doc)

    if total_pages == 0:
        return True

    step = max(total_pages // sample_pages, 1)
    sampled_indices = sorted(set([0, total_pages // 2, total_pages - 1] + list(range(0, total_pages, step))[:sample_pages]))

    low_text_pages = 0
    high_image_pages = 0

    for idx in sampled_indices:
        page = doc[idx]
        text = page.get_text().strip()
        if len(text) < min_chars:
            low_text_pages += 1

        images = page.get_images(full=True)
        img_area = sum(int(w) * int(h) for _, _, w, h, *_ in images)  # width * height
        page_area = page.rect.width * page.rect.height
        if page_area > 0 and img_area / page_area > image_threshold:
            high_image_pages += 1

    total_sampled = len(sampled_indices)
    return (low_text_pages / total_sampled >= text_threshold) or (high_image_pages / total_sampled >= text_threshold)


def extract_pdf_text(pdf_path):
    """
    Extracts text from a PDF. Uses Document AI for scanned PDFs in chunks (max 15 pages).
    Returns:
        pages_text: dict mapping page index to text
        scanned: bool indicating whether OCR was used
    """
    scanned = is_scanned_pdf(pdf_path)
    pages_text = {}

    if not scanned:
        # Extract using PyMuPDF for digital PDFs
        doc = fitz.open(pdf_path)
        for i in range(len(doc)):
            pages_text[i] = doc[i].get_text()
        return pages_text, scanned

    # === OCR via Google Cloud Document AI ===
    print("🔍 Detected scanned PDF, using Document AI OCR...")

    project_id = os.getenv('PROJECT_ID')
    processor_id = os.getenv('PROCESSOR_ID')
    location = "us"

    opts = ClientOptions(api_endpoint=f"{location}-documentai.googleapis.com")
    client = documentai_v1.DocumentProcessorServiceClient(client_options=opts)
    processor_name = client.processor_path(project_id, location, processor_id)

    # Read full PDF and split into ≤15 page chunks
    reader = PdfReader(pdf_path)
    total_pages = len(reader.pages)
    chunk_size = 15

    page_map = {}
    for start in range(0, total_pages, chunk_size):
        end = min(start + chunk_size, total_pages)
        writer = PdfWriter()

        for i in range(start, end):
            writer.add_page(reader.pages[i])

        with NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
            writer.write(temp_pdf)
            temp_pdf_path = temp_pdf.name

        with open(temp_pdf_path, "rb") as f:
            raw_document = documentai_v1.RawDocument(
                content=f.read(),
                mime_type="application/pdf",
            )

        request = documentai_v1.ProcessRequest(
            name=processor_name,
            raw_document=raw_document
        )

        result = client.process_document(request=request)
        document = result.document

        for page in document.pages:
            text = ""
            for block in page.blocks:
                if block.layout.text_anchor.text_segments:
                    for segment in block.layout.text_anchor.text_segments:
                        start = segment.start_index or 0
                        end = segment.end_index
                        text += document.text[start:end]
            page_map[start + page.page_number - 1] = text

        os.remove(temp_pdf_path)

    return page_map, scanned


