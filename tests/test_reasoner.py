from src.graph.graph_builder import GraphBuilder
from src.parser import PepParser
from src.reasoning.reasoner import Reasoner

TEXT = """PEP: 612\nTitle: Parameter Specification Variables\nAuthor: Typing Author\nStatus: Final\nType: Standards Track\nCreated: 01-Jan-2020\nPython-Version: 3.10\n\nAbstract\n========\n\nThis PEP introduces ParamSpec for Callable decorators and type hints.\n\nMotivation\n==========\n\nDecorators need to preserve callable parameter types.\n\nRationale\n=========\n\nThis PEP specifies a parameter specification variable for forwarding callable signatures.\n"""

def test_reasoner_returns_structured_json():
    pep = PepParser().parse_text(TEXT)
    graph = GraphBuilder().build([pep])
    result = Reasoner(graph).reason("How should decorators preserve Callable parameter types?")
    assert result["RelevantPEPs"]
    assert "Evidence" in result
    assert "ConfidenceScore" in result
