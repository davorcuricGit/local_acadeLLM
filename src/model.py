import ollama
from src.config import MODEL

def ensure_model_available(model_name=MODEL):
    """
    Checks that the model is downloaded in Ollama. If it isn't, asks the user whether
    to download it from the Ollama library. Returns True if the model is ready to use.
    """
    try:
        ollama.show(model_name)
        return True
    except ollama.ResponseError as e:
        if e.status_code != 404:
            raise

    answer = input(f"Model '{model_name}' is not downloaded. Download it from the Ollama library now? [y/N] ")
    if answer.strip().lower() not in ("y", "yes"):
        print(f"Not downloading. Run `ollama pull {model_name}` or change MODEL in .env.")
        return False

    print(f"Downloading {model_name}...")
    for progress in ollama.pull(model_name, stream=True):
        if progress.total:
            print(f"\r{progress.status}: {100 * (progress.completed or 0) / progress.total:.0f}%", end="", flush=True)
        else:
            print(f"\n{progress.status}", end="", flush=True)
    print(f"\n{model_name} downloaded.")
    return True
