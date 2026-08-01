# Paper Section Extractor
 
I got tired of the usual problem I run into building RAG pipelines for research papers: dump the whole PDF into an embedding and the context gets diluted, tokens get wasted, and the model has no idea which section a fact actually came from. This tool is my attempt at solving the "what section is this text even from" problem before worrying about anything smarter.
 
Give it a PDF, and it finds the section headers (Abstract, Introduction, Methods, numbered sections like 1.1 / 2.3.4, the usual academic ones), figures out which pages each section spans, and gives you back clean, searchable chunks instead of one big wall of text. Everything runs locally — no API keys, no cloud calls.
 
## Why I'm building this
 
The end goal is a system that can pull things like model architectures, hyperparameters, datasets, training setups, and evaluation metrics out of deep learning papers and turn them into a structured knowledge graph.
 
Before I can trust an LLM to extract that kind of metadata, I need to hand it the *right* chunk of text — not the whole paper, not a random 500-token window. Reliable section boundaries with page numbers attached is the foundation everything else depends on.
 
## What it does right now
 
- Detects section headers (Abstract, numbered sections, and common academic headers like Related Work, Methods, Results, Discussion, Conclusion, References)
- Tracks the page range for each section
- Keeps paragraphs in order within a section
- Lets you search across section titles and content
- Runs entirely offline — no paid APIs, no external LLM calls

## Why this might be useful if you're doing RAG over papers
 
Splitting by actual section boundaries instead of fixed-size chunks means you can send a model just the Methods section instead of the whole paper, keep page-level provenance so you can cite where something came from, and generally get less noisy retrieval.
 
## What's next
 
Still early and actively changing. On the list:
 
- JSON export alongside Markdown
- Better handling of multi-column layouts and scanned PDFs
- Support for other formats (HTML, LaTeX source, JATS XML)
- Local LLM-based metadata extraction (architectures, hyperparameters, datasets, metrics)
- A knowledge graph builder on top of the extracted metadata
This is technically a side project, but it feeds directly into my thesis work, so I'm treating it like one.
 
## Running it locally
 
```bash
pip install gradio pymupdf4llm
python app.py
```
 
Upload a PDF, hit Extract, and browse the sections.
 
## Contributing
 
If you're working on something similar — RAG over papers, metadata extraction, whatever — feel free to open an issue. Happy to compare notes.
 
## License
 
MIT — use it however you want.