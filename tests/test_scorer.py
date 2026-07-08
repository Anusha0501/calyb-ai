from src.graph.graph_builder import GraphBuilder
from src.parser import PepParser
from src.reasoning.input_parser import InputParser
from src.reasoning.scorer import Scorer

TEXT = """PEP: 612\nTitle: Parameter Specification Variables\nAuthor: Typing Author\nStatus: Final\nType: Standards Track\nCreated: 01-Jan-2020\nPython-Version: 3.10\n\nAbstract\n========\n\nThis PEP introduces ParamSpec for Callable decorators and type hints.\n\nMotivation\n==========\n\nDecorators need to preserve callable parameter types.\n"""

def test_scorer_counts_two_hop_concept_overlap():
    graph = GraphBuilder().build([PepParser().parse_text(TEXT)])
    parsed = InputParser().parse("Callable decorator ParamSpec")
    score = Scorer().score_pep(graph, parsed, "pep:612")
    assert score.concept_overlap > 0
    assert score.overall > 0
