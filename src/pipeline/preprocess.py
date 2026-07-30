from src.extraction.pdf_reader import extract_pages_with_headers
from src.extraction.section_builder import build_sections



def run_preprocessing(file_path: str):

    print("\n === Step 2: Extracting Pages ===")
    pages = extract_pages_with_headers(file_path)
    print(f"Extracted {len(pages)} pages from {file_path}")


    # print("\n=== Sample of Few Original Pages ===")
    # for p in pages[:3]:
    #     print(f"\nPage {p['page']}:")
    #     print(f"Headers: {p['headers']}")
    #     print(f"Raw text snippet: {p['raw_text']}")



    print("\n=== Step 3: Building Sections ===")
    sections = build_sections(pages)
    print(f"Built {len(sections)} sections")

    # print("\n=== Sample of Built Sections ===")
    # for p in sections[:]:
    #     print(f"\nSection {p['section']}, Pages {p['page_start']}-{p['page_end']}:")
    #     for para in p['paragraphs']:
    #         print(f"- {para}")


    return sections