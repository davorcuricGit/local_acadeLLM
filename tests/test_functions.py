import pytest

import acadllm.pdf as pdf
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
    result = pdf.remove_references(['pre', text_block, 'post'])
    assert result == expected

def test_load_pdf():
    result = pdf.load_pdf(SAMPLE_PATH)
    num_pages = len(result)
    assert result is not None
    assert num_pages == 22

