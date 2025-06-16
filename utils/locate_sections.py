from rapidfuzz import fuzz
from collections import Counter

def is_roman_numeral(s):
    s = s.lower().strip().replace(" ", "")
    return s.isalpha() and all(c in "ivxlcdm" for c in s)

def locate_sections(toc_entries, pages, toc_page_index=None):
    result = {}
    total_pages = len(pages)
    offset_candidates = []

    pdf_offset = (toc_page_index + 1) if toc_page_index is not None else 0

    raw_matches = []

    for title, toc_page in toc_entries:
        normalized_title = title.strip().lower()
        best_score = -1
        best_page_idx = -1

        try:
            toc_page_num = int(toc_page)
        except (ValueError, TypeError):
            continue  # Skip non-numeric entries

        # Start search a few pages after TOC ends
        search_start = max(pdf_offset, 0)

        for i in range(search_start, total_pages):
            lines = pages[i].splitlines()
            for line in lines:
                line_clean = line.strip().lower()
                if not line_clean:
                    continue
                score = fuzz.ratio(normalized_title, line_clean)
                if score > best_score:
                    best_score = score
                    best_page_idx = i
                    if score == 100:
                        break
            if best_score == 100:
                break

        if best_page_idx != -1:
            offset = best_page_idx - toc_page_num
            offset_candidates.append(offset)
            raw_matches.append((title, toc_page_num, best_page_idx))

    # Calculate modal offset
    modal_offset = Counter(offset_candidates).most_common(1)[0][0] if offset_candidates else 0

    # Final adjusted mapping
    for title, toc_page, _ in raw_matches:
        actual_page = toc_page + modal_offset
        result[title] = actual_page +1

    return result
