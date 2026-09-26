import os
import re
import fitz  # PyMuPDF


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

    return "\n\n".join(remove_tables(remove_references(full_text)))

def remove_references(blocks):
    """
    Drops everything from the last 'References' (or similar) heading onward,
    to save context-window tokens. Returns the blocks unchanged if no heading is found.
    """
    heading = re.compile(r"(\d+\.?\s*)?(references|bibliography|works cited|literature cited)", re.IGNORECASE)

    for i in range(len(blocks) - 1, -1, -1):
        if heading.fullmatch(blocks[i]):
            return blocks[:i]
    return blocks

def remove_tables(blocks):
    """
    Drops blocks that are mostly bare numbers (flattened table cells). They cost
    many tokens and the model can't reconstruct the table layout from them anyway.
    """
    # A table cell like 0.36, -1.2, (2.07), 1,234, 12%, or %0.14 (PyMuPDF sometimes renders minus signs as %)
    number = re.compile(r"[%\-–−]?\(?[\d.,]+\)?%?\**")

    kept = []
    for block in blocks:
        lines = [line.strip() for line in block.split("\n") if line.strip()]
        numeric = sum(1 for line in lines if number.fullmatch(line))
        if len(lines) >= 4 and numeric / len(lines) > 0.5:
            continue
        kept.append(block)
    return kept