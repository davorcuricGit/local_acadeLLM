import argparse
import sys
from pathlib import Path

from acadllm.config import MODEL
from acadllm.summarize import run_summarize

def main():
    parser = argparse.ArgumentParser(
        prog="acadllm",
        description="Summarize, cluster, and organize academic PDFs into structured Markdown notes using a local LLM.",
    )

    subcommands = parser.add_subparsers(dest="command", required=True)

    summarize = subcommands.add_parser("summarize", help="produce markdown summary of each PDF")
    

    summarize.add_argument("path", type=Path, help="a PDF file, or a directory of PDFs")
    summarize.add_argument("--overwrite", action="store_true",
                        help="re-summarize PDFs that already have a .md summary")
    summarize.add_argument("--model", default=MODEL, help=f"Ollama model to use, (default: {MODEL})")
    summarize.set_defaults(func=run_summarize)

    args = parser.parse_args()
    args.func(args)

    

if __name__ == "__main__":
    main()