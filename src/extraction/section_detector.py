import re



def is_section_header(text):
    text = text.strip()

    # Must be alone on its line
    if "\n" in text:
        return False

    # Must not contain commas
    if "," in text:
        return False

    # Must not exceed more than 6 words
    if len(text.split()) > 6:
        return False

    # Pattern: 1. Introduction
    #          2. Related Work
    #          3. Shallow ReLU Networks
    if re.match(r"^\d+(?:\.\d+)*(?:\.)?\s+[A-Z][A-Za-z0-9 ,\-()]*$", text):
        return True

    # Pattern: Abstract (single-word strong header)
    # if text.lower() in ["abstract", "introduction", "conclusion", "related work", "background", "method",
    #         "methods", "experiments", "results",
    #         "discussion", "references", "acknowledgements"]:
    #     return True

    return False
