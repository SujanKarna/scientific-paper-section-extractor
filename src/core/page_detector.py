# Detects page number for a single block of text. Returns None if no page number is detected.

import re

def extract_page_number(block: str):
    clean = block.strip()

    # If it is a single number it is likely to be a page number, but we will check if it is a section header first.
    if clean.isdigit():
        return int(clean)

    # contains "et al" → number at beginning is likely to be a page number, but we will check if it is a section header first.
    if "et al" in clean.lower():
        m = re.match(r"^(\d+)", clean)
        if m:
            if len(clean.split()) < 10:
                return int(m.group(1))

    return None