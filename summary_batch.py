import os
import summary_single_paper

from src.pdf import extract_academic_text
from src.io_utils import save_markdown_file, load_pdf

def summarize_directory(directory_path):
    """
    Summarizes all PDF files in the specified directory using the extract_academic_text and summarize_academic_paper functions.
    """
    if not os.path.exists(directory_path):
        raise FileNotFoundError(f"The directory {directory_path} does not exist.")
    
    summaries = {}
    
    for i,filename in enumerate(os.listdir(directory_path)):
        print(f"Processing {i+1}/{len(os.listdir(directory_path))}: {filename}")

        if filename.lower().endswith('.pdf'):
            pdf_path = os.path.join(directory_path, filename)

            #check if the md already exists, if so skip
            if os.path.exists(pdf_path[:-4] + ".md"):
                print(f"Summary for {filename} already exists. Skipping...")
                continue
            
            try:
                input_doc = load_pdf(pdf_path)
                paper_text = extract_academic_text(input_doc)
                summary = summary_single_paper.summarize_academic_paper(paper_text)
                summaries[filename] = summary

                save_markdown_file(summary, pdf_path[:-4] + ".md")
            except Exception as e:
                print(f"Error processing {filename}: {e}")
    
    return summaries


if __name__ == "__main__":

     #get the input directory from the user as input argument, otherwise return an error message
    import sys

    if len(sys.argv) < 2:
        print("Usage: python summary_batch.py <path_to_directory>")
        sys.exit(1)
    input_directory = sys.argv[1]

    if not summary_single_paper.ensure_model_available():
        sys.exit(1)

    try:
        print("Parsing academic PDF layout...")
        summarize_directory(input_directory)
        
    except Exception as e:
        print(f"\nAn error occurred: {e}")

