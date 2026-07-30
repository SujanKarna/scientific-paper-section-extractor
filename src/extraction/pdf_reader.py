import os
import fitz
from src.extraction.section_detector import is_section_header

def extract_pages_with_headers(file_path):

    # Check if file_dir exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File Not Found at {file_path}")

    results = []
    with fitz.open(file_path) as pdf:
        for page_number, page in enumerate(pdf, start=1):

            raw_text = page.get_text("text")
            lines = [line.strip() for line in raw_text.split("\n") if line.strip()]

            headers = [line for line in lines if is_section_header(line)]

            results.append({
                "page": page_number,
                "raw_text": raw_text,
                "headers": headers
            })

    return results
