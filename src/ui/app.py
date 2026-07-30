import gradio as gr
from pathlib import Path

from src.pipeline.file_loader import save_uploaded_file
from src.pipeline.run_pipeline import run_pipeline


# ---------------------------------------------------------------------------
# Core extraction logic (pipeline calls unchanged)
# ---------------------------------------------------------------------------

def sections_to_markdown(sections):
    """Combine all extracted sections into one downloadable markdown file."""
    lines = []
    for sec in sections:
        lines.append(f"## {sec['section']}  (Pages {sec['page_start']}–{sec['page_end']})\n")
        lines.append("\n\n".join(sec["paragraphs"]))
        lines.append("\n\n---\n")
    return "\n".join(lines)


def prepare_download(sections):
    content = sections_to_markdown(sections)
    out_path = Path("extracted_sections.md")
    out_path.write_text(content, encoding="utf-8")
    return str(out_path)


def filter_sections(sections, query):
    if not query:
        return sections
    query = query.lower().strip()
    return [s for s in sections if query in s["section"].lower()]


def on_extract(file, progress=gr.Progress()):
    if file is None:
        return (
            [],
            "⚠️ No file uploaded yet — drop a PDF above to get started.",
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=False, value=None),
        )

    progress(0.2, desc="Saving uploaded file...")
    saved_path = save_uploaded_file(file)

    progress(0.6, desc="Extracting sections...")
    sections = run_pipeline(saved_path)

    if not sections:
        return (
            [],
            "⚠️ No sections were detected in this PDF. Try a different file.",
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=False, value=None),
        )

    progress(1.0, desc="Done!")
    total_pages = max((s["page_end"] for s in sections), default=0)
    status_msg = f"✅ Extracted **{len(sections)}** sections across **{total_pages}** pages."
    download_path = prepare_download(sections)

    return (
        sections,
        status_msg,
        gr.update(visible=True),
        gr.update(visible=True),
        gr.update(visible=True, value=download_path),
    )


# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------

CUSTOM_CSS = """
#hero {text-align: center; padding: 10px 0 6px 0;}
#hero h1 {margin-bottom: 2px; font-size: 1.9rem;}
#hero p {color: var(--body-text-color-subdued);}
.section-title {font-weight: 600;}
footer {visibility: hidden}
"""


def build_ui():
    with gr.Blocks(
        theme=gr.themes.Soft(primary_hue="indigo", secondary_hue="slate"),
        title="Paper Section Extractor",
        css=CUSTOM_CSS,
    ) as demo:
        sections_state = gr.State([])

        with gr.Column(elem_id="hero"):
            gr.Markdown(
                "# 📄 Paper Section Extractor\n"
                "Turn a research PDF into clean, navigable sections in seconds."
            )

        with gr.Row(equal_height=False):
            # ---------------- Left column: upload & controls ----------------
            with gr.Column(scale=1, min_width=320):
                pdf_input = gr.File(
                    label="Upload a research paper (PDF)",
                    file_types=[".pdf"],
                    file_count="single",
                )

                with gr.Row():
                    extract_btn = gr.Button("🚀 Extract Sections", variant="primary", scale=2)
                    clear_btn = gr.ClearButton(value="Clear", scale=1)

                status = gr.Markdown("Upload a PDF to begin.")

                search_box = gr.Textbox(
                    label="🔍 Search sections",
                    placeholder="e.g. Introduction, Methodology...",
                    visible=False,
                )

                download_btn = gr.DownloadButton("⬇️ Download as Markdown", visible=False)

                gr.Markdown(
                    "---\n"
                    "**Tips**\n"
                    "- Works best on standard single/double-column academic PDFs\n"
                    "- Numbered headers like `1.`, `1.1`, `3.1.2` are detected automatically\n"
                )

            # ---------------- Right column: results ----------------
            with gr.Column(scale=2):
                results_area = gr.Column(visible=False)
                with results_area:
                    gr.Markdown("### 🗂️ Extracted Sections", elem_classes=["section-title"])

                    @gr.render(inputs=[sections_state, search_box])
                    def render_sections(sections, query):
                        filtered = filter_sections(sections, query)
                        if not filtered:
                            gr.Markdown("_No sections match your search._")
                            return
                        for sec in filtered:
                            with gr.Accordion(
                                f"📘 {sec['section']}  ·  pages {sec['page_start']}–{sec['page_end']}",
                                open=False,
                            ):
                                gr.Markdown("\n\n".join(sec["paragraphs"]))

        extract_btn.click(
            fn=on_extract,
            inputs=pdf_input,
            outputs=[sections_state, status, results_area, search_box, download_btn],
        )

        clear_btn.add([pdf_input, sections_state, status, search_box, download_btn])

        gr.Markdown(
            "<div style='text-align:center; color:gray; margin-top:28px;'>"
            "Made with ❤️ for scientific document processing By Sujan Karna."
            "</div>"
        )

    return demo


if __name__ == "__main__":
    ui = build_ui()
    ui.launch()
