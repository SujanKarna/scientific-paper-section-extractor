# Detects section headers in a list of text blocks.


import re

COMMON_HEADERS = {
    "abstract", "abstract.", "introduction", "related work", "background",
    "method", "methods", "methodology",
    "experiments", "results", "discussion",
    "conclusion", "conclusions",
    "acknowledgments", "acknowledgements",
    "references", "bibliography"
}

NUMERIC_HEADER = r"^\d+(?:\.\d+)*(?:\.)?\s+[A-Za-z].+$"

ROMAN_HEADER = r"^[IVXLCDM]+\.\s+[A-Za-z].+$"

APPENDIX_HEADER = r"^(appendix\b|[A-Z]\.\s+[A-Za-z]).+$"

HTTP_LINKS = r"^\d+\s+https?://"




def is_section_header(block: str) -> bool:
    clean = block.strip()

    # Abstract detection: if any block starts with "Abstract" (case-insensitive), we consider it a section header.
    if clean.lower().startswith("abstract"):
        return True

    # Some headers may contain "et al" that begins with a number, which is not a section header. For example, "1. Smith et al." is not a section header.
    if "et al" in clean:
        return False

    # Block that contains more than 4 commas is unlikely to be a section header, as section headers are usually short and concise.
    if clean.count(",") > 4:
        return False

    # Block that contains more than 10 words is unlikely to be a section header, as section headers are usually short and concise.
    if len(clean.split()) > 10:
        return False

    # Block that contains a URL is unlikely to be a section header.
    if re.match(HTTP_LINKS,clean):
        return False

    # Common headers
    normalized = re.sub(r"[^\w\s]", "", clean).lower()
    if normalized in COMMON_HEADERS:
        return True

    # Numeric headers
    if re.match(NUMERIC_HEADER, clean):
        return True

    # Roman headers
    if re.match(ROMAN_HEADER, clean):
        return True

    # Appendix headers
    if re.match(APPENDIX_HEADER, clean, re.IGNORECASE):
        return True

    

    return False
