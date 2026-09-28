#loader

import os
from pathlib import Path

MODEL = os.environ.get("ACADLLM_MODEL", "qwen3.5:9b")  # Default to qwen3.5:9b if not set
CONTEXT_WINDOW = int(os.environ.get("ACADLLM_CONTEXT_WINDOW", 32768))  # Default
TEMPERATURE = float(os.environ.get("ACADLLM_TEMPERATURE", 0.2))  # Default to 0.2 if not set

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