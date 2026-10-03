import sys
import argparse
from pathlib import Path

from acadllm.config import MODEL, EMBEDDING_MODEL
from acadllm.summarize import summarize_path
from acadllm.llm import ensure_model_available
from acadllm.embed import embed_path


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

def run_embed(args):
    print('in progress')

    # Checked once up front, so a batch run doesn't ask per paper
    if not ensure_model_available(args.model):
        sys.exit(1)

    failed = embed_path(args.path, args.model, args.visualize)
    if failed:
        print(f"\n{len(failed)} failed: {', '.join(failed)}")
        sys.exit(1)
    else:
        print("\nAll PDFs summarized successfully.")
    pass


def run_visualize(args):
    import json
    import numpy as np
    from acadllm.plotting import plot_similarity_matrix

    #load cached embeddings and visualize the similarity matrix
    cache_path = args.path / "summaries" / ".acadllm" / "embeddings.json"
    if not cache_path.exists():
        print(f"Cached embeddings not found at {cache_path}. Please run 'embed' first.")
        sys.exit(1)


    # Open the file and load it as a dictionary
    with open(cache_path, 'r') as file:
        dict = json.load(file)

    #get titles from dictionary
    titles = [value["title"] for value in dict["entries"].values()]

    #get embeddings from dictionary
    embeddings = [value["embedding"] for value in dict["entries"].values()]


    #print((embeddings))

    plot_similarity_matrix(np.array(embeddings), titles)



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



    embedd = subcommands.add_parser("embed", help="produce embeddings for each Markdown summary")
    embedd.add_argument("path", type=existing_path, help="directory of PDFs (the summaries must already exist)")
    embedd.add_argument("--model", default=EMBEDDING_MODEL, help=f"Ollama model to use, (default: {EMBEDDING_MODEL})")
    embedd.add_argument("--visualize", action="store_true", help="visualize the similarity matrix of resulting embeddings")
    embedd.set_defaults(func=run_embed)


    visualize = subcommands.add_parser("visualize", help="visualize the similarity matrix of embeddings")
    visualize.add_argument("path", type=existing_path, help="directory of PDFs (the summaries must already exist)")
    visualize.set_defaults(func=run_visualize)

    args = parser.parse_args()
    args.func(args)

    

    

if __name__ == "__main__":
    main()