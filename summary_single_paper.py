#summarize a multi-column academic PDF into a structured literature review summary using a local LLM
#requires ollama and pymupdf to be installed in the Python environment
#and a local LLM model (e.g., qwen2.5:7b) to be running via Ollama

import os
import ollama
import fitz  # PyMuPDF
from config import MODEL, CONTEXT_WINDOW, TEMPERATURE

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
        "You are an elite academic peer reviewer. Analyze the provided text from a research paper. "
        "Produce a rigorous, publication-grade summary in clean Markdown (.md). "
        "Structure your response exactly as follows:\n"
        "# [Paper Title / Inferred Title]\n\n"
        "## Authors \n\n"
        "## Keywords (up to three)\n\n"
        "## 1. Core Contribution & Objective\n(What problem does this paper solve? What is the core hypothesis?)\n\n"
        "## 2. Methodology & Framework\n(Describe the experiment design, dataset, or architectural setup.)\n\n"
        "## 3. Key Findings & Data Insights\n(Synthesize main results, specifically highlighting any data, figures, or tables mentioned.)\n\n"
        "## 4. Limitations & Future Work\n(What constraints or gaps did the authors mention?)\n\n"
        "## 5. (optional) up to 3 definitions or key terms required to understand the content\n(Provide concise definitions for any technical terms or acronyms.)\n\n"
        "## 6. (optional) up to 3 motivating references cited in the paper\n(Provide full citations for any references mentioned.)\n\n"
    )
    
    print(f"Sending prompt to local model ({model_name})...")
    response = ollama.chat(
        model=model_name,
        messages=[
            {'role': 'system', 'content': system_instruction},
            {'role': 'user', 'content': f"Here is the text extracted from the paper:\n\n{paper_text}"}
        ],
                # FIX: Force Ollama to allocate enough VRAM/RAM for the paper length
        options={
            "num_ctx": CONTEXT_WINDOW,       # Sets the context window to 32k tokens
            "temperature": TEMPERATURE      # Lower temperature forces precise, analytical summaries
        }
    )
    return response['message']['content']

def save_markdown_file(markdown_content, output_path):
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(markdown_content)
    print(f"\nAcademic summary successfully saved to: {output_path}")

if __name__ == "__main__":
    
    #get the input PDF from the user as input argument, otherwise return an error message
    import sys

    if len(sys.argv) < 2:
        print("Usage: python summary.py <path_to_academic_pdf>")
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
