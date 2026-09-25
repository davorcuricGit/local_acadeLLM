#loader

import os
from pathlib import Path
from dotenv import load_dotenv


load_dotenv()

DATA_DIR = Path(os.environ.get("PAPERS_DIR", 'data/papers'))

MODEL = os.environ.get("MODEL", "qwen2.5:7b")  # Default to qwen2.5:7b if not set
CONTEXT_WINDOW = int(os.environ.get("CONTEXT_WINDOW", 32000))  # Default to 32000 if not set
TEMPERATURE = float(os.environ.get("TEMPERATURE", 0.2))  # Default to 0.2 if not set