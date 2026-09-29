import ollama
from pydantic import BaseModel, Field
from acadllm.config import MODEL, PROMPT_TEMPLATE, CONTEXT_WINDOW, TEMPERATURE
from acadllm.pdf import extract_academic_text, load_pdf


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
        print(f"Not downloading. Run `ollama pull {model_name}` or choose another model with --model.")
        return False

    print(f"Downloading {model_name}...")
    for progress in ollama.pull(model_name, stream=True):
        if progress.total:
            print(f"\r{progress.status}: {100 * (progress.completed or 0) / progress.total:.0f}%", end="", flush=True)
        else:
            print(f"\n{progress.status}", end="", flush=True)
    print(f"\n{model_name} downloaded.")
    return True


# Schema passed to Ollama as `format=`
# constrains the model to output JSON with exactly these fields. 
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
    return summary_to_markdown(summary)




def run_summarize(args):
    if args.path.is_dir():
            pdfs = sorted(p for p in args.path.iterdir() if p.suffix.lower() == ".pdf")
    elif args.path.is_file():
        pdfs = [args.path]
    else:
        parser.error(f"{args.path} does not exist")

    # Checked once up front, so a batch run doesn't ask per paper
    if not ensure_model_available(args.model):
        sys.exit(1)

    failed = []
    for i, pdf_path in enumerate(pdfs, start=1):
        print(f"\n[{i}/{len(pdfs)}] {pdf_path.name}")
        if not summarize_pdf(pdf_path, args.overwrite, args.model):
            failed.append(pdf_path.name)

    if failed:
        print(f"\n{len(failed)} of {len(pdfs)} failed: {', '.join(failed)}")
        sys.exit(1)



def summarize_pdf(pdf_path, overwrite=False, model_name=MODEL):
    """ Summarizes one PDF into a .md file next to it. Returns False if it failed. """
    output_path = pdf_path.with_suffix(".md")
    if output_path.exists() and not overwrite:
        print(f"Summary already exists, skipping (use --overwrite to redo): {output_path}")
        return True

    try:
        paper_text = extract_academic_text(load_pdf(pdf_path))
        print(f"Extracted roughly {len(paper_text.split())} words.")
        save_markdown_file(summarize_academic_paper(paper_text, model_name), output_path)
        return True
    except Exception as e:
        print(f"Error processing {pdf_path.name}: {e}")
        return False

