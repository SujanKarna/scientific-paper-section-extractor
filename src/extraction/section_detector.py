import re
import unicodedata

def normalize_unicode_letters(text):
    return unicodedata.normalize("NFKD", text)



def is_section_header(text):
    
    print(f"{text}\n")
    text = normalize_unicode_letters(text)
    print(f"{text}\n")

    # Normalize unicode spaces
    text = re.sub(r"[\u00A0\u2000-\u200A]", " ", text)

   

    text = text.strip()

    # Remove markdown-style heading markers
    text = text.lstrip("#").strip()
    
    # Reject pure numbers
    if text.isdigit():
        return False

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

    
    if re.match(r"^\d+(?:\.\d+)*(?:\.)?\s+[A-Za-z0-9 ,\-()]*$", text):
        return True

    # Pattern: Abstract (single-word strong header)
    if text.lower() in ["abstract"]:
        return True

    return False
