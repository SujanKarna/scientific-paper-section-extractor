from src.extraction.section_detector import is_section_header


def build_sections(pages):
    all_sections = []
    last_section = None

    for p in pages:
        page = p["page"]
        text = p["raw_text"]
        headers = p["headers"]  # already filtered by is_section_header()

        # If page has headers → split into multiple sections
        if headers:
            lines = text.split("\n")
            current_header = None
            current_text = []

            for line in lines:
                stripped = line.strip()

                if stripped in headers:
                    # Save previous section
                    if current_header is not None:
                        all_sections.append({
                            "section": current_header,
                            "page_start": page,
                            "page_end": page,
                            "text": "\n".join(current_text)
                        })
                        current_text = []

                    current_header = stripped

                else:
                    current_text.append(stripped)

            # Save last section on this page
            if current_header is not None:
                all_sections.append({
                    "section": current_header,
                    "page_start": page,
                    "page_end": page,
                    "text": "\n".join(current_text)
                })
                last_section = current_header

        else:
            # No header → append to last section
            if last_section is not None:
                all_sections[-1]["text"] += "\n" + text
                all_sections[-1]["page_end"] = page
            else:
                # First pages with no header
                all_sections.append({
                    "section": "Unknown",
                    "page_start": page,
                    "page_end": page,
                    "text": text
                })
                last_section = "Unknown"

    return all_sections

