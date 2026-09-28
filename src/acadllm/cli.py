import argparse
import sys
from pathlib import Path

from acadllm.model import ensure_model_available, summarize_academic_paper
from acadllm.output import save_markdown_file
from acadllm.pdf import extract_academic_text, load_pdf


def summarize_pdf(pdf_path, overwrite=False):
    """ Summarizes one PDF into a .md file next to it. Returns False if it failed. """
    output_path = pdf_path.with_suffix(".md")
    if output_path.exists() and not overwrite:
        print(f"Summary already exists, skipping (use --overwrite to redo): {output_path}")
        return True

    try:
        paper_text = extract_academic_text(load_pdf(pdf_path))
        print(f"Extracted roughly {len(paper_text.split())} words.")
        save_markdown_file(summarize_academic_paper(paper_text), output_path)
        return True
    except Exception as e:
        print(f"Error processing {pdf_path.name}: {e}")
        return False



def main():
    parser = argparse.ArgumentParser(
        prog="acadellm",
        description="Summarize academic PDFs into structured Markdown notes using a local LLM.",
    )
    parser.add_argument("path", type=Path, help="a PDF file, or a directory of PDFs")
    parser.add_argument("--overwrite", action="store_true",
                        help="re-summarize PDFs that already have a .md summary")
    args = parser.parse_args()

    if args.path.is_dir():
        pdfs = sorted(p for p in args.path.iterdir() if p.suffix.lower() == ".pdf")
    elif args.path.is_file():
        pdfs = [args.path]
    else:
        parser.error(f"{args.path} does not exist")

    # Checked once up front, so a batch run doesn't ask per paper
    if not ensure_model_available():
        sys.exit(1)

    failed = []
    for i, pdf_path in enumerate(pdfs, start=1):
        print(f"\n[{i}/{len(pdfs)}] {pdf_path.name}")
        if not summarize_pdf(pdf_path, args.overwrite):
            failed.append(pdf_path.name)

    if failed:
        print(f"\n{len(failed)} of {len(pdfs)} failed: {', '.join(failed)}")
        sys.exit(1)


if __name__ == "__main__":
    main()