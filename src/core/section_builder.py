# Builds sections from blocks of text extracted from a PDF, based on section headers and page numbers.

import re
from src.core.section_detector import is_section_header


def extract_sections(page_blocks):
    sections = {}
    current_header = None
    current_pages = set()
    current_content = []

    for block, page in page_blocks:
        clean = block.strip()

        # ---------- SPECIAL CASE: ABSTRACT ----------
        if clean.lower().startswith("abstract"):
            # Save previous section if exists
            if current_header:
                sections[current_header] = {
                    "pages": sorted(current_pages),
                    "content": "\n\n".join(current_content).strip()
                }

            # Start new Abstract section
            current_header = "Abstract"
            current_pages = {page}

            # Extract content after "Abstract." or "Abstract:"
            after = re.sub(r"^abstract[:\.]?\s*", "", clean, flags=re.I)
            current_content = [after] if after else []
            continue

        # ---------- NORMAL SECTION HEADERS ----------
        if is_section_header(clean):
            # Save previous section
            if current_header:
                sections[current_header] = {
                    "pages": sorted(current_pages),
                    "content": "\n\n".join(current_content).strip()
                }

            # Start new section
            current_header = clean
            current_pages = {page}
            current_content = []
            continue

        # ---------- REGULAR CONTENT ----------
        if current_header:
            current_pages.add(page)
            current_content.append(clean)

    # ---------- SAVE LAST SECTION ----------
    if current_header:
        sections[current_header] = {
            "pages": sorted(current_pages),
            "content": "\n\n".join(current_content).strip()
        }

    return sections