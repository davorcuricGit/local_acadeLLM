# acadllm

Summarize academic papers (PDFs) into structured Markdown literature-review notes using a **local** LLM via [Ollama](https://ollama.com). Nothing leaves your machine: no API keys, no cloud calls.

## What it does

1. **Extracts text** from each PDF with PyMuPDF, reading page blocks in order so multi-column layouts stay readable.
2. **Trims the text to fit the model's context window**: drops the reference list, tables of bare numbers, and tiny fragments such as page numbers.
3. **Sends the text to a local model** (default `qwen3.5:9b`). The model's output is constrained to a fixed JSON schema, so every summary has the same structure.
4. **Writes a Markdown summary** next to the PDF (`paper.pdf` → `paper.md`) with these sections:
   - Title, Authors, Keywords
   - 1. Core Contribution & Objective
   - 2. Methodology & Framework
   - 3. Key Findings & Data Insights
   - 4. Limitations & Future Work
   - 5. Terms (key terms and definitions)

See [sample_paper/](sample_paper/) for example PDFs and the summaries generated from them.

## Requirements

- Python 3.10+
- [Ollama](https://ollama.com/download), installed and running
- Enough RAM/VRAM for the model and its context window. The default 32k-token context with a 9B model needs roughly 8–16 GB.

## Installation

```bash
git clone git@github.com:davorcuricGit/local_acadeLLM.git
cd local_acadeLLM

python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

This installs the dependencies listed in [pyproject.toml](pyproject.toml) and creates the `acadllm` command. To use the exact versions this project was tested with, run `pip install -r requirements-lock.txt` before `pip install -e .`.

Make sure the Ollama server is running: open the Ollama app, or run `ollama serve`. If the model isn't downloaded yet, `acadllm` offers to download it on first run (or run `ollama pull qwen3.5:9b` yourself).

## Usage

```bash
acadllm path/to/paper.pdf        # one paper -> path/to/paper.md
acadllm path/to/papers/          # every PDF in the directory
acadllm --help                   # all options
```

| Option | Description |
|---|---|
| `--model NAME` | Ollama model to use for this run, e.g. `--model qwen2.5:7b` |
| `--overwrite` | Re-summarize PDFs that already have a `.md` summary |

PDFs that already have a summary are skipped, so you can stop a directory run and restart it without redoing finished papers. If some papers fail, the others are still processed, and the failures are listed at the end.

**Use it from your own Python code:**

```python
from acadllm.pdf import load_pdf, extract_academic_text
from acadllm.model import summarize_academic_paper
from acadllm.output import save_markdown_file

text = extract_academic_text(load_pdf("paper.pdf"))
save_markdown_file(summarize_academic_paper(text), "paper.md")
```

## Configuration

`acadllm` works without any configuration. To change a default for every run, set an environment variable, for example in your shell or in `~/.zshrc`:

```bash
export ACADLLM_MODEL=qwen2.5:7b
```

| Variable | Default | Description |
|---|---|---|
| `ACADLLM_MODEL` | `qwen3.5:9b` | Any Ollama model. `--model` overrides it for a single run |
| `ACADLLM_CONTEXT_WINDOW` | `32768` | Context size in tokens. Raise it for long papers if your model and memory allow it; lower it if you run out of memory |
| `ACADLLM_TEMPERATURE` | `0.2` | Lower values give more precise, less creative summaries |

## Performance notes

- The model is held in memory by the Ollama server, not by `acadllm`. It loads on the first paper and stays loaded between papers, then unloads after about 5 idle minutes by default.
- Most of the time is spent generating each summary. Expect anywhere from under a minute to several minutes per paper, depending on your hardware and the paper's length.
- If a paper is too long for the context window, Ollama would silently drop the beginning of it. `acadllm` detects this and reports an error for that paper instead of saving an unreliable summary. Raise `ACADLLM_CONTEXT_WINDOW` (`qwen3.5:9b` supports up to 256k tokens, memory permitting).

## Limitations

- **Scanned PDFs** without a text layer produce little or no text, and the model may then write a summary from memory rather than from the paper. OCR them first, e.g. `brew install ocrmypdf` and `ocrmypdf scanned.pdf scanned_ocr.pdf`.
- Tables are removed and equations and figures are extracted as raw text only, so details from them may be missing or imprecise.
- LLM summaries can contain errors or invented details. Check important claims against the paper.

## Roadmap

- **Cluster**: link and group summaries into themes, using Obsidian-style notes and a graph.
- **Organize**: move PDFs into themed subdirectories based on the clusters.
- Automatic OCR for scanned PDFs.
- Chunked summarization for papers too long for the context window.

## Project structure

```
├── pyproject.toml            # Project metadata, dependencies, `acadllm` command
├── requirements-lock.txt     # Exact tested dependency versions
├── src/acadllm/
│   ├── cli.py                # `acadllm` command-line interface
│   ├── config.py             # Default settings and the prompt
│   ├── pdf.py                # PDF loading and text extraction/cleanup
│   ├── model.py              # Ollama model check and summarization
│   └── output.py             # Markdown rendering and saving
├── sample_paper/             # Example PDFs and generated summaries
└── LICENSE                   # MIT license
```

## License

This project is released under the [MIT License](LICENSE).
