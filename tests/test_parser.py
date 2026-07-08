from src.parser import PepParser

SAMPLE = """PEP: 999\nTitle: Sample Typing PEP\nAuthor: Ada Lovelace, Grace Hopper\nStatus: Draft\nType: Standards Track\nCreated: 01-Jan-2024\nPython-Version: 3.13\n\nAbstract\n========\n\nThis PEP introduces SampleType and references PEP 484 plus :pep:`526`.\n\nMotivation\n==========\n\nUsers need clearer annotations.\n"""

def test_parser_extracts_metadata_sections_and_mentions():
    pep = PepParser().parse_text(SAMPLE)
    assert pep.number == 999
    assert pep.title == "Sample Typing PEP"
    assert pep.authors == ["Ada Lovelace", "Grace Hopper"]
    assert pep.python_version == "3.13"
    assert "abstract" in pep.sections
    assert 484 in pep.mentioned_peps
    assert 526 in pep.mentioned_peps
