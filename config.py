#loader

import os
from pathlib import Path
from dotenv import load_dotenv


load_dotenv()

DATA_DIR = Path(os.environ.get("PAPERS_DIR", 'data/papers'))