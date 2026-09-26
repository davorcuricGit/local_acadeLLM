#summarize a multi-column academic PDF into a structured literature review summary using a local LLM
#requires ollama and pymupdf to be installed in the Python environment
#and a local LLM model (e.g., qwen2.5:7b) to be running via Ollama

import os
import re
import ollama
import fitz  # PyMuPDF
from pydantic import BaseModel, Field
from config import MODEL, CONTEXT_WINDOW, TEMPERATURE, PROMPT_TEMPLATE

#import pdfhandling
# Append the specific subdirectory path
sys.path.append(os.path.abspath('./my_subdirectory'))

import my_module


# Schema passed to Ollama as `format=`, which constrains the model to output
# JSON with exactly these fields. The Markdown is then built in Python, so the
# headings are always correct regardless of how well the model follows the prompt.
class Term(BaseModel):
    term: str
    definition: str

class PaperSummary(BaseModel):
    title: str
    authors: list[str]
    keywords: list[str] = Field(max_length=3)
    core_contribution: str
    methodology: str
    key_findings: str
    limitations: str
    terms: list[Term]

def ensure_model_available(model_name=MODEL):
    """
    Checks that the model is downloaded in Ollama. If it isn't, asks the user whether
    to download it from the Ollama library. Returns True if the model is ready to use.
    """
    try:
        ollama.show(model_name)
        return True
    except ollama.ResponseError as e:
        if e.status_code != 404:
            raise

    answer = input(f"Model '{model_name}' is not downloaded. Download it from the Ollama library now? [y/N] ")
    if answer.strip().lower() not in ("y", "yes"):
        print(f"Not downloading. Run `ollama pull {model_name}` or change MODEL in .env.")
        return False

    print(f"Downloading {model_name}...")
    for progress in ollama.pull(model_name, stream=True):
        if progress.total:
            print(f"\r{progress.status}: {100 * (progress.completed or 0) / progress.total:.0f}%", end="", flush=True)
        else:
            print(f"\n{progress.status}", end="", flush=True)
    print(f"\n{model_name} downloaded.")
    return True

    

def summarize_academic_paper(paper_text):
    """ Sends academic text to a local LLM for a structured literature review summary. """
    
    # Using qwen:7b or a similar 8B model is highly recommended over smaller 3B models
    # for handling scientific logic, tables, and dense data accurately.
    model_name = MODEL

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
    return summary_to_markdown(summary)

def summary_to_markdown(summary):
    """ Renders a PaperSummary as the Markdown literature review note. """
    terms = "\n".join(f"- **{t.term}**: {t.definition}" for t in summary.terms)

    return (
        f"# {summary.title}\n\n"
        f"## Authors\n{', '.join(summary.authors)}\n\n"
        f"## Keywords\n{', '.join(summary.keywords)}\n\n"
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

if __name__ == "__main__":
    
    #get the input PDF from the user as input argument, otherwise return an error message
    import sys

    if len(sys.argv) < 2:
        print("Usage: python summary_single_paper.py <path_to_academic_pdf>")
        sys.exit(1)
    input_paper = sys.argv[1]

    #output has same name and location as input PDF, but with .md extension
    output_summary = os.path.splitext(input_paper)[0] + ".md"

    if not ensure_model_available():
        sys.exit(1)

    try:
        print("Parsing academic PDF layout...")
        extracted_text = extract_academic_text(input_paper)

     
        
        # Basic check to avoid pushing too many tokens to low-end systems
        estimated_words = len(extracted_text.split())
        print(f"Extracted roughly {estimated_words} words.")
        
        markdown_review = summarize_academic_paper(extracted_text)


        save_markdown_file(markdown_review, output_summary)
        
    except Exception as e:
        print(f"\nAn error occurred: {e}")
