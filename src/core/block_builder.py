# Assign page numbers to each block of text based on the extracted text from the PDF.

from src.core.page_detector import extract_page_number

def assign_pages_to_blocks(blocks):
    page = 1
    page_blocks = []

    for block in blocks:
        pn = extract_page_number(block)

        if pn is not None:
            page = pn
            continue  # skip page number block itself

        page_blocks.append((block, page))

    return page_blocks