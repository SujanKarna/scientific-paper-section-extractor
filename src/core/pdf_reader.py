# Using pymupdf4llm to extract text from PDF files. This library is a wrapper around PyMuPDF (fitz) and is optimized for LLMs.

import os
import pymupdf4llm

def extract_text_from_pdf(file_path):

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File Not Found at {file_path}")

    txt = pymupdf4llm.to_text(file_path)

    
    return txt

