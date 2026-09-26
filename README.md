# local_acadeLLM

Summarize academic papers (PDFs) into structured Markdown literature-review notes using a **local** LLM via [Ollama](https://ollama.com). Nothing leaves your machine: no API keys, no cloud calls.

## What it does

1. **Extracts text** from the PDF with PyMuPDF, reading page blocks in order so multi-column layouts stay readable, and drops tiny fragments such as page numbers.
2. **Sends the text to a local model** (default `qwen3.5:9b`) with a peer-reviewer style prompt.
3. **Writes a Markdown summary** next to the PDF (`paper.pdf` → `paper.md`) with these sections:
   - Title, Authors, Keywords
   - 1. Core Contribution & Objective
   - 2. Methodology & Framework
   - 3. Key Findings & Data Insights
   - 4. Limitations & Future Work
   - 5. Key terms and definitions (optional)
   - 6. Motivating references (optional)

See [sample_paper/](sample_paper/) for example PDFs and the summaries generated from them.

## Requirements

- Python 3.9+
- [Ollama](https://ollama.com/download), installed and running
- Enough RAM/VRAM for the model and its context window. The default 32k-token context with a 9B model needs roughly 8–16 GB.
- Python packages: `ollama`, `pymupdf`, `python-dotenv`. Exact versions are pinned in [requirements-lock.txt](requirements-lock.txt).

## Installation

```bash
git clone git@github.com:davorcuricGit/local_acadeLLM.git
cd local_acadeLLM

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-lock.txt

# Download the model (once)
ollama pull qwen2.5:7b
```

Make sure the Ollama server is running: open the Ollama app, or run `ollama serve`.

## Configuration

Settings are read from a `.env` file in the project root (see [config.py](config.py)). Copy the example to get started:

```bash
cp .env.example .env
```

| Variable         | Default      | Description                                                                        |
|------------------|--------------|------------------------------------------------------------------------------------|
| `MODEL`          | `qwen3.5:9b` | Any model you have pulled with `ollama pull`                                       |
| `CONTEXT_WINDOW` | `32000`      | Context size in tokens. Lower it if you run out of memory; raise it for long papers |
| `TEMPERATURE`    | `0.2`        | Lower values give more precise, less creative summaries                            |

If there is no `.env`, the defaults above are used.

## Usage

**Summarize a single paper:**

```bash
python summary_single_paper.py path/to/paper.pdf
# -> path/to/paper.md
```

**Summarize every PDF in a directory:**

```bash
python summary_batch.py path/to/papers/
```

The batch script saves each summary as soon as it's done. It skips PDFs that already have a matching `.md`, so you can stop and rerun it without redoing finished papers. To regenerate a summary, delete its `.md` file.

**Use it from your own Python code:**

```python
import summary_single_paper as s

text = s.extract_academic_text("paper.pdf")
summary = s.summarize_academic_paper(text)
s.save_markdown_file(summary, "paper.md")
```

## Performance notes

- The model is held in memory by the Ollama server, not by these scripts. It loads once on the first request and stays loaded between papers, then unloads after about 5 idle minutes by default.
- Most of the time is spent generating each summary. Expect anywhere from under a minute to several minutes per paper, depending on your hardware and the paper's length.
- Papers longer than `CONTEXT_WINDOW` tokens are silently truncated by the model. Raise the value (if memory allows) for very long papers.
   - future versions will include automatic chunking for particularly long papers

## Limitations

- Scanned PDFs without a text layer return little or no text; OCR them first.
- Tables, equations, and figures are extracted as raw text only, so summaries of them may be imprecise.
- LLM summaries can contain errors or invented details, especially in citations. Check important claims against the paper.

## Project structure

```
├── summary_single_paper.py   # PDF extraction, LLM call, save to Markdown (CLI for one file)
├── summary_batch.py          # Summarize all PDFs in a directory
├── config.py                 # Loads settings from .env
├── .env.example              # Example configuration
├── requirements-lock.txt     # Pinned dependencies
├── LICENSE                   # MIT license
└── sample_paper/             # Example PDFs and generated summaries
```

## License

This project is released under the [MIT License](LICENSE).
