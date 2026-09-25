#loader

import os
from pathlib import Path
from dotenv import load_dotenv


load_dotenv()

DATA_DIR = Path(os.environ.get("PAPERS_DIR", 'data/papers'))

MODEL = os.environ.get("MODEL", "qwen2.5:7b")  # Default to qwen2.5:7b if not set
CONTEXT_WINDOW = int(os.environ.get("CONTEXT_WINDOW", 32768))  # Default to 32000 if not set
TEMPERATURE = float(os.environ.get("TEMPERATURE", 0.2))  # Default to 0.2 if not set

PROMPT_TEMPLATE = (
"You are an elite academic peer reviewer. Analyze the provided text from a research paper "
"and produce a rigorous, publication-grade summary. "
"Respond in JSON with these fields:\n"
"- title: the name of the paper\n"
"- authors: list of author names\n"
"- keywords: up to three keywords\n"
"- core_contribution: What problem does this paper solve? What is the core hypothesis?\n"
"- methodology: experiment design, dataset, or architectural setup\n"
"- key_findings: synthesize the main results, specifically highlighting any data, figures, or tables mentioned\n"
"- limitations: what constraints, gaps, or future work did the authors mention?\n"
"- terms: up to three technical terms or acronyms, each with a concise definition\n"
)