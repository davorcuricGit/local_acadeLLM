import sys
import argparse
from pathlib import Path

from acadllm.config import MODEL, EMBEDDING_MODEL
from acadllm.summarize import summarize_path
from acadllm.llm import ensure_model_available


def existing_path(value):
    """ argparse type: a Path that must exist. """
    path = Path(value)
    if not path.exists():
        raise argparse.ArgumentTypeError(f"{value} does not exist")
    return path

def run_summarize(args):

    # Checked once up front, so a batch run doesn't ask per paper
    if not ensure_model_available(args.model):
        sys.exit(1)

    failed = summarize_path(args.path, args.overwrite, args.model)
    if failed:
        print(f"\n{len(failed)} failed: {', '.join(failed)}")
        sys.exit(1)
    else:
        print("\nAll PDFs summarized successfully.")

def run_embedd(args):
    print('in progress')
    pass

def main():
    parser = argparse.ArgumentParser(
        prog="acadllm",
        description="Summarize, cluster, and organize academic PDFs into structured Markdown notes using a local LLM.",
    )

    subcommands = parser.add_subparsers(dest="command", required=True)

    summarize = subcommands.add_parser("summarize", help="produce markdown summary of each PDF")
    summarize.add_argument("path", type=existing_path, help="a PDF file, or a directory of PDFs")
    summarize.add_argument("--overwrite", action="store_true",
                        help="re-summarize PDFs that already have a .md summary")
    summarize.add_argument("--model", default=MODEL, help=f"Ollama model to use, (default: {MODEL})")
    summarize.set_defaults(func=run_summarize)

    embedd = subcommands.add_parser("embedd", help="produce embeddings for each Markdown summary")
    embedd.add_argument("path", type=existing_path, help="a Markdown file, or a directory of Markdown files")
    embedd.add_argument("--model", default=EMBEDDING_MODEL, help=f"Ollama model to use, (default: {EMBEDDING_MODEL})")
    embedd.set_defaults(func=run_embedd)

    args = parser.parse_args()
    args.func(args)

    

if __name__ == "__main__":
    main()