# tests/conftest.py
import pytest
from types import SimpleNamespace

def write_summary(directory, name, title, body):
    """create empty pdf and matching minimal summary, used for unit testing"""

    #write an empty bytes object
    (directory / f"{name}.pdf").write_bytes(b"")
    summaries = directory / "summaries"
    summaries.mkdir(exist_ok = True)

    #write the summary to the .md file for embedding
    (summaries / f"{name}.md").write_text(f"# {title}\n\n{body}\n", encoding="utf-8")


@pytest.fixture
def paper_dir(tmp_path):
    """ temporary directory with two papers and their summaries """
    write_summary(tmp_path, "alpha", "Alpha paper", "A study of asset pricing")
    write_summary(tmp_path, "beta", "Beta paper", "A study of cell biology")



class FakeEmbed:
    """ ollama.embed standing: returns fixed vectrs and records each calls inputs"""

    def __init__(self):
        self.calls = []

    def __call__(self, model, input):
        self.calls.append(list(input))
        return SimpleNamespace(embeddings=[[len(text), 1.0] for text in input])


@pytest.fixture
def fake_embed(monkeypatch):
    fake = FakeEmbed()
    monkeypatch.setattr("acadllm.embed.ollama.embed", fake)
    return fake