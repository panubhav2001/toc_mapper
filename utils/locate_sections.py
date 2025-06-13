from rapidfuzz import fuzz

def is_roman_numeral(s):
    return s.lower().strip().replace(" ", "").isalpha() and all(c in "ivxlcdm" for c in s.lower())

def locate_sections(toc_entries, pages, toc_page_index=None):
    result = {}
    total_pages = len(pages)

    # Start searching after TOC ends
    pdf_offset = (toc_page_index + 1) if toc_page_index is not None else 0

    for title, toc_page in toc_entries:
        normalized_title = title.strip().lower()
        best_score = -1
        best_page = -1

        # Decide where to begin the search
        if isinstance(toc_page, int):
            start_page = pdf_offset
        elif str(toc_page).isdigit():
            start_page = pdf_offset
        elif is_roman_numeral(str(toc_page)):
            start_page = 0
        else:
            start_page = 0

        for i in range(start_page, total_pages):
            page_text = pages[i]
            lines = page_text.splitlines()

            for line in lines:
                line_clean = line.strip().lower()

                if not line_clean:
                    continue

                score = fuzz.ratio(normalized_title, line_clean)

                # Prioritize perfect or high-confidence matches
                if score > best_score:
                    best_score = score
                    best_page = i

                    if score == 100:
                        break  # Perfect match, stop early

            if best_score == 100:
                break  # Stop page scanning early too

        result[title] = int(best_page) +1  # Already 0-based
    return result
