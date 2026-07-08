from src.graph.graph_builder import GraphBuilder
from src.parser import PepParser

TEXT = """PEP: 604\nTitle: Allow writing union types as X | Y\nAuthor: Typing Author\nStatus: Final\nType: Standards Track\nCreated: 01-Jan-2020\nPython-Version: 3.10\n\nAbstract\n========\n\nThis PEP introduces Union syntax using X | Y for type hints.\n\nMotivation\n==========\n\nUsers need concise annotations for optional and union types.\n\nRejected Ideas\n==============\n\nOne rejected alternative was to keep only typing.Union forever.\n"""

def test_graph_builder_creates_evidenced_edges():
    pep = PepParser().parse_text(TEXT)
    graph = GraphBuilder().build([pep])
    assert "pep:604" in graph.nodes
    assert any(edge.type == "INTRODUCES" for edge in graph.edges)
    assert all(edge.evidence.sentence for edge in graph.edges)
