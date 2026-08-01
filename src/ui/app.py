# app.py
import json
import logging
from pathlib import Path
import gradio as gr

from src.pipeline.file_loader import save_uploaded_file
from src.pipeline.run_pipeline import run_pipeline

LOG = logging.getLogger("paper_section_extractor")
LOG.setLevel(logging.INFO)
LOG.addHandler(logging.StreamHandler())

OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

CUSTOM_CSS = """
#hero {text-align: center; padding: 12px 0 8px 0;}
#hero h1 {margin-bottom: 4px; font-size: 1.8rem;}
footer {visibility: hidden}
"""

# ---------------- Helpers ----------------

def convert_pipeline_output(raw_sections):
    """Convert your dict-based pipeline output into UI-friendly list."""
    if isinstance(raw_sections, dict):
        return [
            {
                "section": key,
                "page_start": raw_sections[key]["pages"][0] if raw_sections[key]["pages"] else None,
                "page_end": raw_sections[key]["pages"][-1] if raw_sections[key]["pages"] else None,
                "paragraphs": [
                    p.strip() for p in raw_sections[key]["content"].split("\n\n") if p.strip()
                ]
            }
            for key in raw_sections
        ]
    return raw_sections


def sections_to_markdown(sections):
    lines = []
    for s in sections:
        lines.append(f"## {s['section']}\n**Pages:** {s['page_start']}–{s['page_end']}\n")
        lines.append("\n\n".join(s["paragraphs"]))
        lines.append("\n\n---\n")
    return "\n".join(lines)


def save_markdown(sections):
    out_path = OUTPUT_DIR / "extracted_sections.md"
    out_path.write_text(sections_to_markdown(sections), encoding="utf-8")
    return str(out_path)


def save_json(sections):
    out_path = OUTPUT_DIR / "extracted_sections.json"
    out_path.write_text(json.dumps(sections, indent=2, ensure_ascii=False), encoding="utf-8")
    return str(out_path)


# ---------------- Core extraction ----------------

def on_extract(file, search_query, debug=False, progress=gr.Progress()):
    if file is None:
        return [], "⚠️ Upload a PDF first.", "", None, None

    progress(0.1, desc="Saving file...")
    saved_path = save_uploaded_file(file)

    progress(0.4, desc="Running pipeline...")
    raw_sections = run_pipeline(saved_path)

    sections = convert_pipeline_output(raw_sections)

    if not sections:
        return [], "⚠️ No sections detected.", "", None, None

    # Apply search filter
    if search_query:
        q = search_query.lower().strip()
        sections = [
            s for s in sections
            if q in s["section"].lower() or any(q in p.lower() for p in s["paragraphs"])
        ]

    # Render HTML manually
    html = ""
    for s in sections:
        title = f"{s['section']} · pages {s['page_start']}–{s['page_end']}"
        content = "<br><br>".join(s["paragraphs"])
        html += f"""
        <details>
            <summary style='font-size:16px; padding:6px 0;'>{title}</summary>
            <div style='padding:8px 0;'>{content}</div>
        </details>
        <hr>
        """
    # Build compact HTML
    html = "<div style='font-size:14px;'>"

    for s in sections:
        title = f"{s['section']} · pages {s['page_start']}–{s['page_end']}"
        content = "<br><br>".join(s["paragraphs"])

        html += f"""
        <details style='margin-bottom:8px;'>
            <summary style='cursor:pointer; font-size:15px; padding:4px 0;'>
                📘 {title}
            </summary>
            <div style='padding:6px 0 0 12px; font-size:14px;'>
                {content}
            </div>
        </details>
        """

    html += "</div>"
    
    progress(0.9, desc="Preparing downloads...")
    md_path = save_markdown(sections)
    json_path = save_json(sections)

    status = f"✅ Extracted {len(sections)} sections."

    debug_text = repr(raw_sections)[:4000] if debug else ""

    return sections, status, html, md_path, json_path, debug_text


# ---------------- UI ----------------

def build_ui():
    with gr.Blocks(theme=gr.themes.Soft(primary_hue="indigo"), css=CUSTOM_CSS) as demo:

        with gr.Column(elem_id="hero"):
            gr.Markdown("# 📄 Paper Section Extractor")
            gr.Markdown("Extract clean sections + page ranges from scientific PDFs.")

        with gr.Row():
            # ---------------- LEFT COLUMN ----------------
            with gr.Column(scale=1, min_width=320):
                pdf_input = gr.File(label="Upload PDF", file_types=[".pdf"])
                search_box = gr.Textbox(label="Search sections", placeholder="e.g. Introduction")
                debug_toggle = gr.Checkbox(label="Debug mode", value=False)

                extract_btn = gr.Button("🚀 Extract Sections", variant="primary")
                status = gr.Markdown("Upload a PDF to begin.")

                # Download buttons stay here (left side)
                md_download = gr.DownloadButton("⬇️ Download Markdown", visible=False)
                json_download = gr.DownloadButton("⬇️ Download JSON", visible=False)

            # ---------------- RIGHT COLUMN ----------------
            with gr.Column(scale=2):
                gr.Markdown("### 🗂️ Extracted Sections")

                # Compact section list
                sections_html = gr.HTML(
                    """
                    <div style='font-size:14px; line-height:1.4;'>
                        <i>No sections yet.</i>
                    </div>
                    """
                )

                debug_output = gr.Textbox(label="Debug Output", visible=False)

        # Wiring
        extract_btn.click(
            fn=on_extract,
            inputs=[pdf_input, search_box, debug_toggle],
            outputs=[
                gr.State(),      # sections (not used directly)
                status,
                sections_html,
                md_download,
                json_download,
                debug_output
            ],
        )

    return demo



if __name__ == "__main__":
    ui = build_ui()
    ui.launch()
