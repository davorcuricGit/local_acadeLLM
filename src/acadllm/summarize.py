import ollama
from pydantic import BaseModel, Field
import re
from datetime import date
import yaml

from acadllm.docs import extract_academic_text, load_pdf
from acadllm.config import MODEL, PROMPT_TEMPLATE, CONTEXT_WINDOW, TEMPERATURE


def to_tag(keyword):
    """ Converts a keyword into a valid Obsidian tag: lowercase, hyphens instead of spaces, no punctuation. """
    tag = re.sub(r"[^\w\s-]", "", keyword.lower())
    return re.sub(r"[\s_]+", "-", tag).strip("-")


def summary_to_markdown(summary, source_pdf, model_name):
    """ Renders a PaperSummary as a Markdown note with YAML frontmatter"""
    frontmatter = {
        "title": summary.title,
        "authors": summary.authors,
        "tags": [to_tag(k) for k in summary.keywords],
        "source": f"[[{source_pdf}]]",
        "model": model_name,
        "created": date.today(),
    }
    terms = "\n".join(f"- **{t.term}**: {t.definition}" for t in summary.terms)

    return (
        f"---\n{yaml.safe_dump(frontmatter, sort_keys=False, allow_unicode=True)}---\n\n"
        f"# {summary.title}\n\n"
        f"## Authors\n{', '.join(summary.authors)}\n\n"
        f"## Keywords\n{', '.join(summary.keywords)}\n\n"
        f"## Short Title\n{summary.short_title}\n\n"
        f"## Abstract\n{summary.abstract}\n\n"
        f"## 1. Core Contribution & Objective\n{summary.core_contribution}\n\n"
        f"## 2. Methodology & Framework\n{summary.methodology}\n\n"
        f"## 3. Key Findings & Data Insights\n{summary.key_findings}\n\n"
        f"## 4. Limitations & Future Work\n{summary.limitations}\n\n"
        f"## 5. Terms\n{terms}\n\n"
    )


def save_markdown_file(markdown_content, output_path):
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(markdown_content)
    print(f"\nAcademic summary successfully saved to: {output_path}")

def create_markdown_directory(path):
    """ Creates a directory for Markdown summaries if it doesn't exist. """
    md_dir = path / "summaries"
    md_dir.mkdir(exist_ok=True)
    return md_dir

# Schema passed to Ollama as `format=`
# constrains the model to output JSON with exactly these fields. 
class Term(BaseModel):
    term: str
    definition: str

class PaperSummary(BaseModel):
    title: str
    authors: list[str]
    keywords: list[str] = Field(max_length=3)
    short_title: str
    abstract: str
    core_contribution: str
    methodology: str
    key_findings: str
    limitations: str
    terms: list[Term]

    
def summarize_academic_paper(paper_text, model_name = MODEL):
    """ Sends academic text to a local LLM for a structured literature review summary. """
    
    # Using qwen:9b or a similar is highly recommended over smaller 3B models
    # for handling scientific logic, tables, and dense data accurately.
    

    # Instructions go *after* the paper, in the same user message. Small models attend most
    # to the text just before they answer. (A separate system message would be moved to the
    # top of the prompt by Ollama's chat template, regardless of its position in the list.)
    user_message = (
        f"Here is the text extracted from the paper:\n\n{paper_text}\n\n"
        f"---\n\n{PROMPT_TEMPLATE}"
    )

    print(f"Sending prompt to local model ({model_name})...")
    response = ollama.chat(
        model=model_name,
        messages=[
            {'role': 'user', 'content': user_message}
        ],
        format=PaperSummary.model_json_schema(),  # Constrain output to the schema above
                # FIX: Force Ollama to allocate enough VRAM/RAM for the paper length
        options={
            "num_ctx": CONTEXT_WINDOW,       # Sets the context window to 32k tokens
            "temperature": TEMPERATURE      # Lower temperature forces precise, analytical summaries
        }
    )

    # Ollama silently drops the start of prompts longer than num_ctx (only its server log
    # says so). A prompt that filled the whole window was truncated, so the summary can't be trusted.
    prompt_tokens = response['prompt_eval_count']
    print(f"Prompt used {prompt_tokens} of {CONTEXT_WINDOW} context tokens.")
    if prompt_tokens >= CONTEXT_WINDOW:
        raise ValueError(
            f"Prompt was truncated to fit the {CONTEXT_WINDOW}-token context window; "
            "the model did not see the whole paper. Shorten the input or raise CONTEXT_WINDOW."
        )

    summary = PaperSummary.model_validate_json(response['message']['content'])
    return summary



def summarize_path(path, overwrite=False, model_name=MODEL):
    """ Summarizes a PDF, or every PDF in a directory. Returns the names of PDFs that failed. Called by cli.py"""
    if path.is_dir():
        pdfs = sorted(p for p in path.iterdir() if p.suffix.lower() == ".pdf")
    else:
        pdfs = [path]

    failed = []
    for i, pdf_path in enumerate(pdfs, start=1):
        print(f"\n[{i}/{len(pdfs)}] {pdf_path.name}")
        if not summarize_pdf(pdf_path, overwrite, model_name):
            failed.append(pdf_path.name)
    return failed



def summarize_pdf(pdf_path, overwrite=False, model_name=MODEL):
    """ Summarizes one PDF into a .md file next to it. Returns False if it failed. """
    
    create_markdown_directory(pdf_path.parent)

    #save to the 'summaries' subdirectory
    output_path = pdf_path.parent / "summaries" / pdf_path.with_suffix(".md").name
    
    if output_path.exists() and not overwrite:
        print(f"Summary already exists, skipping (use --overwrite to redo): {output_path}")
        return True
    try:
        paper_text = extract_academic_text(load_pdf(pdf_path))
        print(f"Extracted roughly {len(paper_text.split())} words.")
        summary = summarize_academic_paper(paper_text, model_name)
        save_markdown_file(summary_to_markdown(summary, pdf_path.name,      model_name), output_path)
        return True
    except Exception as e:
        print(f"Error processing {pdf_path.name}: {type(e).__name__}: {e}")
        return False

