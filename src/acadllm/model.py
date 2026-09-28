import ollama
from pydantic import BaseModel, Field
from acadllm.config import MODEL, PROMPT_TEMPLATE, CONTEXT_WINDOW, TEMPERATURE
from acadllm.output import summary_to_markdown


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
