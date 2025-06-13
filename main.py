import sys
import os
from utils.extract_text import extract_pdf_text
from utils.detect_toc import find_toc_page
from utils.parse_toc import parse_toc_entries
from utils.locate_sections import locate_sections
from utils.save_output import save_mapping

def main(pdf_path):
    print("\n[1] Extracting text from PDF...")
    pages, _ = extract_pdf_text(pdf_path)

    print("[2] Detecting TOC page...")
    toc_page, end_page = find_toc_page(pages)
    if toc_page is None:
        print("TOC not found.")
        return

    print(f"TOC detected from page {int(toc_page) + 1} to {int(end_page) + 1}")

    # Combine TOC text across the range
    toc_text = ""
    for page_num in range(toc_page, end_page + 1):
        toc_text += pages.get(page_num, "") + "\n"

    print("[3] Parsing TOC entries...")
    toc_entries = parse_toc_entries(toc_text)
    if not toc_entries:
        print("No TOC entries found.")
        return

    print("[4] Locating actual section start pages...")
    mapping = locate_sections(toc_entries, pages, toc_page_index=end_page)

    print("[5] Saving output...")
    save_mapping(mapping)
    print("\n✅ Done. Output saved to mapping.json.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python main.py <path_to_pdf>")
        sys.exit(1)

    pdf_path = sys.argv[1]
    if not os.path.exists(pdf_path):
        print("Error: PDF file not found.")
        sys.exit(1)

    main(pdf_path)
