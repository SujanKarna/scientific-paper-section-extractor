import os
import fitz
from src.extraction.section_detector import is_section_header
import re

def extract_pages_with_headers(file_path):

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File Not Found at {file_path}")

    results = []

    with fitz.open(file_path) as pdf:
        for page_number, page in enumerate(pdf, start=1):

            raw_text = page.get_text("text")
            lines = [line.strip() for line in raw_text.split("\n") if line.strip()]

            # ---- MERGE NUMERIC HEADER LINES ----
            merged_lines = []
            i = 0
            while i < len(lines):
                line = lines[i]

                # Case: line is only a number (e.g., "4")
                if re.match(r"^\d+(?:\.\d+)*$", line) and i + 1 < len(lines):
                    next_line = lines[i+1].strip()

                    # If next line starts with a letter → merge into "4 Results"
                    if re.match(r"^[A-Za-z]", next_line):
                        merged_lines.append(f"{line} {next_line}")
                        i += 2
                        continue

                # Otherwise keep line as-is
                merged_lines.append(line)
                i += 1

            #Debug sample
            print(f"\nMerged Lines Sample: {merged_lines[:50]}\n")
            

            # ---- HEADER DETECTION ----
            headers = [line for line in merged_lines if is_section_header(line)]

            results.append({
                "page": page_number,
                "raw_text": raw_text,
                "headers": headers
            })

    return results

