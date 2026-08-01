# Test cases for section header detection before running it into the gradio app UI

from src.pipeline.file_loader import save_uploaded_file as file_loader
from src.core.pdf_reader import extract_text_from_pdf
from src.core.block_builder import assign_pages_to_blocks
from src.core.section_builder import extract_sections
from src.pipeline.run_pipeline import run_pipeline

def run_test(file: str):

    # Loading the pdf
    raw_file = file_loader(file)

    # Step 1: Extract text from PDF
    print(f"Extracting text from PDF: {raw_file}")
    txt = extract_text_from_pdf(raw_file)
    print(f"Extracted {len(txt)} blocks of text from PDF.") 

    # Step 2: Assign page number to extracted text
    print("Assigning page numbers to blocks of text...")
    blocks = [b.strip() for b in txt.split("\n") if b.strip()]
    page_blocks = assign_pages_to_blocks(blocks)
    print(f"Assigned page numbers to {len(page_blocks)} blocks of text.")


    # step 3: Separate blocks into sections based on page numbers and section headers
    print("Extracting sections from blocks of text...")
    sections = extract_sections(page_blocks)
    print(f"Extracted {len(sections)} sections from blocks of text.")


    return sections


def check_pipeline(file: str):

    # Checkinf id pipeline is working as expected
    return run_pipeline(file)


    return sections
if __name__ == "__main__":
    # Test the pipeline with a sample PDF file
    test_file = r"D:\colab tests\sample.pdf"  # Replace with your test PDF file path
    sections = check_pipeline(test_file)
    for header, content in sections.items():
        print(f"Header: {header}")
        print(f"Pages: {content['pages']}")
        print(f"Content: {content['content'][:100]}...")  # Print first 100 characters of content
        print("=" * 40)
