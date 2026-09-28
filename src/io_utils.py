import os
import pymupdf


def load_pdf(pdf_path):
    if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"The file {pdf_path} does not exist.")
            
    return pymupdf.open(pdf_path)



def save_markdown_file(markdown_content, output_path):
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(markdown_content)
    print(f"\nAcademic summary successfully saved to: {output_path}")
