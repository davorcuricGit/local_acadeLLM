import ollama
import numpy as np
import hashlib
import json

from acadllm.config import EMBEDDING_MODEL
from acadllm.docs import load_md, get_prompt_from_md
from acadllm.plotting import plot_similarity_matrix

def normalize_embeddings(embeddings):
    """Normalize embeddings to unit length (L2 norm)."""
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    # Avoid division by zero for empty descriptions
    norms = np.where(norms == 0, 1, norms)
    return embeddings / norms


def cache_embeddings(embeddings, paper_dict, path, model = EMBEDDING_MODEL):
    cache_path = path / "summaries" / ".acadllm" / "embeddings.json"

    cache_path.parent.mkdir(parents=True, exist_ok=True)
    
    data = dict()
    data["model"] = model
    data["entries"] = dict()
    
    for i, (md_name, value) in enumerate(paper_dict.items()):
        data["entries"][md_name] = {"title": value["title"],
                                     "hash": value["hash"], 
                                     "embedding": embeddings[i].tolist()}

    # Save the dictionary to a file
    with open(cache_path, "w") as f:
        json.dump(data, f)




def embed_path(path, model_name = EMBEDDING_MODEL, visualize = False):
    """ Summarizes a Markdown file, or every Markdown file in a directory. Returns the names of files that failed. Called by cli.py"""

    # get all pdf files so that we can get the title of the paper from the pdf file
    # can retrun which pdf files failed to be embedded
    if path.is_dir():
        pdfs = sorted(p for p in path.iterdir() if p.suffix.lower() == ".pdf")
    else:
        pdfs = [path]

    prompt_list = []
    paper_titles = []
    paper_dict = dict()
    failed = []
    for i, pdf_path in enumerate(pdfs, start=1):
        print(f"\n[{i}/{len(pdfs)}] {pdf_path.name}")

        md_path = pdf_path.parent / "summaries" / pdf_path.with_suffix(".md").name
        
        if not md_path.exists():
            print(f"Summary does not exist, skipping: {md_path}")
            failed.append(pdf_path)
            continue

        prompt, title = get_prompt_from_md(md_path)
        prompt_list.append(prompt)  
        paper_titles.append(title)

        paper_dict[pdf_path.with_suffix(".md").name] = {"title": title, 
                                                        "prompt": prompt, 
                                                        "hash": hashlib.sha256(prompt.encode()).hexdigest()}

    response = ollama.embed(model = model_name, input = prompt_list)  
    embeddings = np.vstack(normalize_embeddings(response.embeddings))

    cache_embeddings(embeddings, paper_dict, path)
      
    return failed