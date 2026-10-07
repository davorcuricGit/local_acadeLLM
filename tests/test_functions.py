import pytest
import numpy as np

import acadllm.docs as docs
import acadllm.embed as embed
from acadllm.summarize import to_tag

SAMPLE_PATH = './sample_paper/AFA611-S6B-FamaFrench-CAPM-JEP04.pdf'



@pytest.mark.parametrize('string, expected',[
   ("Capital Asset Pricing Model (CAPM)", "capital-asset-pricing-model-capm"),
   ("Capital  Asset Pricing_Model (CAPM)", "capital-asset-pricing-model-capm"), 
])
def test_to_tag(string, expected):
    assert to_tag(string) == expected

@pytest.mark.parametrize("text_block, expected", [
    ('REFERENCES', ['pre']),
    ('7. References', ['pre']),
    ('Bibliography', ['pre']),
    ('steve', ['pre', 'steve', 'post']),
    ('see References below', ['pre', 'see References below', 'post']),
])
def test_remove_references(text_block, expected):
    result = docs.remove_references(['pre', text_block, 'post'])
    assert result == expected

def test_load_pdf():
    result = docs.load_pdf(SAMPLE_PATH)
    num_pages = len(result)
    assert result is not None
    assert num_pages == 22


def test_cache_path():
    result = embed.get_cache_path(SAMPLE_PATH)
    assert result is not None
    assert result.name == "embeddings.json"


@pytest.mark.parametrize('vec, expected',[
   (np.array([[1, 1],[1,2]]), [1,1]), 
   (np.array([[0, 0],[0.1,0]]), [0,1]),
   (np.array([[0, 1]]), [1]),
])
def test_normalize_embeddings(vec, expected):
    normalized = embed.normalize_embeddings(vec)
    assert normalized.shape == vec.shape
    assert np.linalg.norm(normalized, axis=1) == pytest.approx(expected, rel=1e-5)




def test_second_run_with_unchanged_summaries_makes_no_embed_call(paper_dir, fake_embed):
    embed.embed_path(paper_dir, model_name="fake-model")
    embed.embed_path(paper_dir, model_name="fake-model")

    assert len(fake_embed.calls) == 1        # only the first run embedded anything
    assert len(fake_embed.calls[0]) == 2     # ... and it embedded both papers


def test_changed_summary_is_the_only_one_re_embedded(paper_dir, fake_embed):
    embed.embed_path(paper_dir, model_name="fake-model")
    write_summary(paper_dir, "beta", "Beta paper", "Now about something else entirely.")
    embed.embed_path(paper_dir, model_name="fake-model")

    assert len(fake_embed.calls[1]) == 1
    assert "something else" in fake_embed.calls[1][0]