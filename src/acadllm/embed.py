import ollama
import numpy as np
import hashlib
import json

from acadllm.config import EMBEDDING_MODEL
from acadllm.docs import get_prompt_from_md, ensure_path_exists



def normalize_embeddings(embeddings):
    """Normalize embeddings to unit length (L2 norm)."""
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    # Avoid division by zero for empty descriptions
    norms = np.where(norms == 0, 1, norms)
    return embeddings / norms


def get_cache_path(path):
    """ Location of the embedding cache for a directory of PDFs (or a single PDF's directory). """
    path = ensure_path_exists(path)
    directory = path if path.is_dir() else path.parent
    return directory / "summaries" / ".acadllm" / "embeddings.json"


def save_cache(entries, cache_path, model_name):
    """ Writes to a temporary file first, so an interrupted write can't corrupt the cache. """
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = cache_path.with_suffix(".tmp")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump({"model": model_name, "entries": entries}, f)

    #now overwrite the tmp file    
    tmp_path.replace(cache_path)

def load_cache(cache_path, model_name):
    """ Returns cached entries keyed by summary file name, or {} if there is no usable cache. """
    try:
        with open(cache_path, encoding="utf-8") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

    # Vectors from a different embedding model can't be compared with new ones
    if data.get("model") != model_name:
        return {}
    return data.get("entries", {})



def embed_path(path, model_name = EMBEDDING_MODEL):
    """ Summarizes a Markdown file, or every Markdown file in a directory. Returns the names of files that failed. Called by cli.py"""

    # get all pdf files so that we can get the title of the paper from the pdf file
    # can retrun which pdf files failed to be embedded
    if path.is_dir():
        pdfs = sorted(p for p in path.iterdir() if p.suffix.lower() == ".pdf")
    else:
        pdfs = [path]

    cache_path = get_cache_path(path)
    cached = load_cache(cache_path, model_name)

    entries = {}
    to_embed = []


    failed = []
    for i, pdf_path in enumerate(pdfs, start=1):
        print(f"\n[{i}/{len(pdfs)}] {pdf_path.name}")

        md_path = pdf_path.parent / "summaries" / pdf_path.with_suffix(".md").name
        
        if not md_path.exists():
            print(f"Summary does not exist, skipping: {md_path}")
            failed.append(pdf_path)
            continue

        prompt, title = get_prompt_from_md(md_path)

        prompt_hash = hashlib.sha256(prompt.encode()).hexdigest()
        name = md_path.name

        #check if prompt already cached
        if name in cached and cached[name]["hash"] == prompt_hash:
            entries[name] = {**cached[name], "title":title}
        else:
            entries[name] = {"title": title, "hash": prompt_hash}
            to_embed.append((name, prompt))

    print(f"{len(entries) - len(to_embed)} cached, {len(to_embed)} to embed.")

    if to_embed:
        response = ollama.embed(model=model_name, input=[prompt for _, prompt in to_embed])
        for (name, _), vector in zip(to_embed, normalize_embeddings(np.array(response.embeddings))):
            entries[name]["embedding"] = vector.tolist()

    save_cache(entries, cache_path, model_name)