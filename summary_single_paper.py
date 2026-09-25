#summarize a multi-column academic PDF into a structured literature review summary using a local LLM
#requires ollama and pymupdf to be installed in the Python environment
#and a local LLM model (e.g., qwen2.5:7b) to be running via Ollama

import os
import ollama
import fitz  # PyMuPDF
from pydantic import BaseModel, Field
from config import MODEL, CONTEXT_WINDOW, TEMPERATURE, PROMPT_TEMPLATE


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
    references: list[str]

def extract_academic_text(pdf_path):
    """
    Extracts text from a multi-column academic PDF, 
    ensuring correct reading order and filtering out layout noise.
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"The file {pdf_path} does not exist.")
        
    doc = fitz.open(pdf_path)
    full_text = []
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        
        # 'blocks' sorting preserves multi-column reading flow natively
        blocks = page.get_text("blocks")
        
        for block in blocks:
            # block[4] contains the actual text string
            text = block[4].strip()
            
            # Simple heuristic filter to skip pure page numbers or tiny footer noise
            if len(text) > 5:
                full_text.append(text)
                
    return "\n\n".join(full_text)

def summarize_academic_paper(paper_text):
    """ Sends academic text to a local LLM for a structured literature review summary. """
    
    # Using qwen:7b or a similar 8B model is highly recommended over smaller 3B models
    # for handling scientific logic, tables, and dense data accurately.
    model_name = MODEL
    
    system_instruction = (
       PROMPT_TEMPLATE
    )
    
    print(f"Sending prompt to local model ({model_name})...")
    response = ollama.chat(
        model=model_name,
        messages=[
            {'role': 'system', 'content': system_instruction},
            {'role': 'user', 'content': f"Here is the text extracted from the paper:\n\n{paper_text}"}
        ],
        format=PaperSummary.model_json_schema(),  # Constrain output to the schema above
                # FIX: Force Ollama to allocate enough VRAM/RAM for the paper length
        options={
            "num_ctx": CONTEXT_WINDOW,       # Sets the context window to 32k tokens
            "temperature": TEMPERATURE      # Lower temperature forces precise, analytical summaries
        }
    )
    summary = PaperSummary.model_validate_json(response['message']['content'])
    return summary_to_markdown(summary)

def summary_to_markdown(summary):
    """ Renders a PaperSummary as the Markdown literature review note. """
    terms = "\n".join(f"- **{t.term}**: {t.definition}" for t in summary.terms)
    references = "\n".join(f"- {r}" for r in summary.references)

    return (
        f"# {summary.title}\n\n"
        f"## Authors\n{', '.join(summary.authors)}\n\n"
        f"## Keywords\n{', '.join(summary.keywords)}\n\n"
        f"## 1. Core Contribution & Objective\n{summary.core_contribution}\n\n"
        f"## 2. Methodology & Framework\n{summary.methodology}\n\n"
        f"## 3. Key Findings & Data Insights\n{summary.key_findings}\n\n"
        f"## 4. Limitations & Future Work\n{summary.limitations}\n\n"
        f"## 5. Terms\n{terms}\n\n"
        f"## 6. Reference summary\n{references}\n"
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
