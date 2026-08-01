from src.pipeline.file_loader import save_uploaded_file as file_loader
from src.core.pdf_reader import extract_text_from_pdf
from src.core.block_builder import assign_pages_to_blocks
from src.core.section_builder import extract_sections


def run_pipeline(file: str):

    # App is already saving file, so we don't need to save it again here. We can directly use the file path.
    # Loading the pdf
    # raw_file = file_loader(file)

    # Step 1: Extract text from PDF
    txt = extract_text_from_pdf(file)

    # Step 2: Assign page number to extracted text
    blocks = [b.strip() for b in txt.split("\n") if b.strip()]
    page_blocks = assign_pages_to_blocks(blocks)


    # step 3: Separate blocks into sections based on page numbers and section headers
    sections = extract_sections(page_blocks)


    return sections
