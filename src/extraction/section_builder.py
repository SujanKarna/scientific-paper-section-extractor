from src.extraction.section_detector import is_section_header


def build_sections(pages):
    # Step 1: Collect all headers with page + line index
    header_positions = []

    for p in pages:
        page_num = p["page"]
        lines = p["raw_text"].split("\n")

        for idx, line in enumerate(lines):
            stripped = line.strip()
            if stripped in p["headers"]:
                header_positions.append({
                    "title": stripped,
                    "page": page_num,
                    "line": idx
                })

    # Sort headers globally
    header_positions.sort(key=lambda h: (h["page"], h["line"]))

    sections = []

    # Step 2: Extract content between headers
    for i, header in enumerate(header_positions):
        start_page = header["page"]
        start_line = header["line"]

        # Determine end boundary
        if i + 1 < len(header_positions):
            next_header = header_positions[i + 1]
            end_page = next_header["page"]
            end_line = next_header["line"]
        else:
            # Last header → until end of document
            end_page = pages[-1]["page"]
            end_line = len(pages[-1]["raw_text"].split("\n"))

        # Step 3: Collect content across pages
        content_lines = []

        for p in pages:
            pnum = p["page"]
            lines = p["raw_text"].split("\n")

            if pnum < start_page or pnum > end_page:
                continue

            # Starting page
            if pnum == start_page:
                s_idx = start_line + 1
            else:
                s_idx = 0

            # Ending page
            if pnum == end_page:
                e_idx = end_line
            else:
                e_idx = len(lines)

            content_lines.extend(lines[s_idx:e_idx])

        # Step 4: Remove empty parent sections
        has_real_text = any(line.strip() for line in content_lines)

        if not has_real_text:
            continue

        # Step 5: Clean paragraphs
        paragraphs = []
        current = []

        for line in content_lines:
            if line.strip():
                current.append(line.strip())
            else:
                if current:
                    paragraphs.append(" ".join(current))
                    current = []

        if current:
            paragraphs.append(" ".join(current))

        sections.append({
            "section": header["title"],
            "page_start": start_page,
            "page_end": end_page,
            "paragraphs": paragraphs
        })

    return sections
