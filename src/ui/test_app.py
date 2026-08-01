"""Gradio web app for extracting structured sections from academic PDF papers.

Provides a simple upload -> extract -> browse/search -> download workflow
around the section-extraction pipeline in ``src.pipeline`` / ``src.core``.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List

import gradio as gr

from src.config.constants import DATA_DIR
from src.pipeline.file_loader import save_uploaded_file
from src.pipeline.run_pipeline import run_pipeline

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("paper_section_extractor")

PROCESSED_DIR = DATA_DIR / "processed"


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class Section:
    """A single extracted section of a paper."""

    title: str
    pages: List[int]
    content: str

    @property
    def page_start(self) -> int:
        return self.pages[0] if self.pages else 0

    @property
    def page_end(self) -> int:
        return self.pages[-1] if self.pages else 0

    @property
    def page_range(self) -> str:
        if not self.pages:
            return "—"
        return str(self.page_start) if self.page_start == self.page_end else f"{self.page_start}–{self.page_end}"

    @property
    def word_count(self) -> int:
        return len(self.content.split())


def normalize_sections(raw_sections: dict) -> List[Section]:
    """Convert the pipeline's ``{header: {"pages": [...], "content": "..."}}``
    dict into a list of :class:`Section` objects, dropping any section that
    has no body text (e.g. a stray trailing header).
    """
    sections: List[Section] = []
    for title, data in raw_sections.items():
        content = (data.get("content") or "").strip()
        if not content:
            continue
        sections.append(Section(title=title, pages=sorted(data.get("pages", [])), content=content))
    return sections


def _source_name(file) -> str:
    """Best-effort display filename for a Gradio file upload (which may be
    a temp-file object or a plain path string)."""
    return Path(getattr(file, "name", file)).name


# ---------------------------------------------------------------------------
# Core extraction / formatting logic
# ---------------------------------------------------------------------------

def sections_to_markdown(sections: List[Section], source_name: str) -> str:
    """Combine all extracted sections into one downloadable markdown file."""
    lines = [f"# {source_name}\n", "_Extracted with Paper Section Extractor_\n"]
    for sec in sections:
        lines.append(f"## {sec.title}  (Page {sec.page_range})\n")
        lines.append(sec.content)
        lines.append("\n---\n")
    return "\n".join(lines)


def prepare_download(sections: List[Section], source_name: str) -> str:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    safe_stem = re.sub(r"[^\w\-]+", "_", Path(source_name).stem).strip("_") or "document"
    out_path = PROCESSED_DIR / f"{safe_stem}_sections.md"
    out_path.write_text(sections_to_markdown(sections, source_name), encoding="utf-8")
    return str(out_path)


def filter_sections(sections: List[Section], query: str) -> List[Section]:
    if not query:
        return sections
    q = query.lower().strip()
    return [s for s in sections if q in s.title.lower() or q in s.content.lower()]


def build_summary(sections: List[Section]) -> str:
    total_pages = len({p for s in sections for p in s.pages})
    total_words = sum(s.word_count for s in sections)
    return (
        f"**{len(sections)}** section{'s' if len(sections) != 1 else ''}  ·  "
        f"**{total_pages}** page{'s' if total_pages != 1 else ''}  ·  "
        f"**{total_words:,}** words extracted"
    )


# ---------------------------------------------------------------------------
# Event handlers
# ---------------------------------------------------------------------------

def _outputs(status_msg: str, sections: List[Section] | None = None, show_results: bool = False,
             download_path: str | None = None):
    """Build the return tuple for extract_btn.click in one consistent shape:
    (status, sections_state, summary, results_area, search_box, download_btn)
    """
    sections = sections or []
    summary = build_summary(sections) if sections else ""
    return (
        status_msg,
        sections,
        summary,
        gr.update(visible=show_results),
        gr.update(value="", visible=show_results),
        gr.update(visible=show_results, value=download_path),
    )


def on_file_change(file):
    """Give immediate feedback and clear stale results as soon as the user
    picks a (new) file, before they click Extract."""
    if file is None:
        return "Upload a PDF to begin.", gr.update(visible=False)
    return f"📄 **{_source_name(file)}** ready — click **Extract Sections** to continue.", gr.update(visible=False)


def on_extract(file, progress=gr.Progress()):
    if file is None:
        return _outputs("⚠️ No file uploaded yet — drop a PDF above to get started.")

    source_name = _source_name(file)

    try:
        progress(0.1, desc="Saving uploaded file...")
        saved_path = save_uploaded_file(file)

        progress(0.35, desc="Reading PDF text...")
        raw_sections = run_pipeline(saved_path)

        progress(0.85, desc="Formatting sections...")
        sections = normalize_sections(raw_sections)
    except FileNotFoundError as exc:
        logger.warning("File not found during extraction: %s", exc)
        return _outputs(f"❌ Couldn't find the uploaded file: {exc}")
    except Exception:
        logger.exception("Extraction failed for %s", source_name)
        return _outputs(
            f"❌ Something went wrong while processing **{source_name}**. "
            "It may be scanned/image-based, encrypted, or corrupted."
        )

    if not sections:
        return _outputs(
            "⚠️ No sections were detected in this PDF. It may not follow a "
            "standard academic layout — try a different file."
        )

    progress(1.0, desc="Done!")
    download_path = prepare_download(sections, source_name)
    status_msg = f"✅ Extracted **{len(sections)}** section(s) from **{source_name}**."

    return _outputs(status_msg, sections=sections, show_results=True, download_path=download_path)


def on_clear():
    return (
        None,                                   # pdf_input
        [],                                     # sections_state
        "Upload a PDF to begin.",               # status
        "",                                     # summary
        gr.update(visible=False),               # results_area
        gr.update(value="", visible=False),     # search_box
        gr.update(visible=False, value=None),   # download_btn
    )


# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------

CUSTOM_CSS = """
#hero {text-align: center; padding: 14px 0 8px 0;}
#hero h1 {margin-bottom: 2px; font-size: 1.9rem;}
#hero p {color: var(--body-text-color-subdued);}
.section-title {font-weight: 600;}
#summary-badge {margin: 4px 0 10px 0; color: var(--body-text-color-subdued);}
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
                    clear_btn = gr.Button("Clear", scale=1)

                status = gr.Markdown("Upload a PDF to begin.")

                search_box = gr.Textbox(
                    label="🔍 Search sections",
                    placeholder="Search titles or content...",
                    info="Filters the extracted sections below as you type.",
                    visible=False,
                )

                download_btn = gr.DownloadButton("⬇️ Download as Markdown", visible=False)

                gr.Markdown(
                    "---\n"
                    "**Tips**\n"
                    "- Works best on standard single/double-column academic PDFs\n"
                    "- Numbered headers like `1.`, `1.1`, `3.1.2` are detected automatically\n"
                    "- Scanned (image-only) PDFs with no text layer won't extract correctly\n"
                )

            # ---------------- Right column: results ----------------
            with gr.Column(scale=2):
                results_area = gr.Column(visible=False)
                with results_area:
                    gr.Markdown("### 🗂️ Extracted Sections", elem_classes=["section-title"])
                    summary_md = gr.Markdown("", elem_id="summary-badge")

                    @gr.render(inputs=[sections_state, search_box])
                    def render_sections(sections, query):
                        filtered = filter_sections(sections, query)
                        if not filtered:
                            if sections and query:
                                gr.Markdown("_No sections match your search — try a different term or clear it._")
                            else:
                                gr.Markdown("_No sections to display._")
                            return
                        for i, sec in enumerate(filtered):
                            with gr.Accordion(
                                f"📘 {sec.title}  ·  pages {sec.page_range}  ·  {sec.word_count} words",
                                open=(i == 0),
                            ):
                                gr.Markdown(sec.content)

        extract_btn.click(
            fn=on_extract,
            inputs=pdf_input,
            outputs=[status, sections_state, summary_md, results_area, search_box, download_btn],
        )

        pdf_input.change(
            fn=on_file_change,
            inputs=pdf_input,
            outputs=[status, results_area],
        )

        clear_btn.click(
            fn=on_clear,
            inputs=None,
            outputs=[pdf_input, sections_state, status, summary_md, results_area, search_box, download_btn],
        )

        gr.Markdown(
            "<div style='text-align:center; color:gray; margin-top:28px;'>"
            "Made with ❤️ for scientific document processing By Sujan Karna."
            "</div>"
        )

    return demo


if __name__ == "__main__":
    ui = build_ui()
    ui.queue().launch()
