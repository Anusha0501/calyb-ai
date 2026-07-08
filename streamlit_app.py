"""Streamlit application for Python Typing PEP Knowledge Reasoning System."""
from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime
import streamlit as st
from src.config import KNOWLEDGE_STATE_PATH, GRAPHML_PATH, PROCESSED_DIR, ROOT_DIR
from src.graph.graph_loader import load_graph
from src.reasoning.reasoner import Reasoner

# Page configuration
st.set_page_config(
    page_title="Python Typing Knowledge Reasoning System",
    page_icon="🐍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Cache the graph loading
@st.cache_resource
def load_knowledge_graph():
    """Load the knowledge graph from file."""
    if not KNOWLEDGE_STATE_PATH.exists():
        return None
    try:
        return load_graph(KNOWLEDGE_STATE_PATH)
    except Exception as e:
        st.error(f"Error loading knowledge graph: {e}")
        return None

# Cache the parsed PEPs
@st.cache_data
def load_parsed_peps():
    """Load parsed PEP data from file."""
    parsed_peps_path = PROCESSED_DIR / "parsed_peps.json"
    if not parsed_peps_path.exists():
        return []
    try:
        with open(parsed_peps_path, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error loading parsed PEPs: {e}")
        return []

# Get graph build timestamp
def get_build_timestamp():
    """Get the timestamp when the graph was built."""
    if KNOWLEDGE_STATE_PATH.exists():
        return datetime.fromtimestamp(KNOWLEDGE_STATE_PATH.stat().st_mtime)
    return None

# Sidebar
def render_sidebar(graph, parsed_peps):
    """Render the sidebar with project information and statistics."""
    with st.sidebar:
        st.header("🐍 Python Typing Knowledge")
        
        st.markdown("""
        Knowledge graph built from official Python Enhancement Proposals using 
        deterministic rule-based extraction and explainable graph reasoning.
        """)
        
        st.divider()
        
        # Project Information
        st.subheader("Project Information")
        
        # Dataset Status
        if graph is not None:
            st.success("✅ Knowledge Graph Loaded")
            timestamp = get_build_timestamp()
            if timestamp:
                st.caption(f"Built: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            st.error("❌ Knowledge Graph Not Built")
            st.caption("Run the build commands below")
        
        st.divider()
        
        # Graph Statistics
        if graph is not None:
            st.subheader("Graph Statistics")
            
            col1, col2 = st.columns(2)
            col1.metric("Total Nodes", len(graph.nodes))
            col2.metric("Total Relationships", len(graph.edges))
            
            # Node Type Distribution
            node_types = {}
            for node in graph.nodes.values():
                node_type = node.type
                node_types[node_type] = node_types.get(node_type, 0) + 1
            
            st.subheader("Node Types")
            for node_type, count in sorted(node_types.items()):
                st.write(f"**{node_type}**: {count}")
            
            # Dataset Status
            st.divider()
            st.subheader("Dataset Status")
            st.metric("PEPs Parsed", len(parsed_peps))
            
            raw_pep_count = len(list(ROOT_DIR.glob("data/raw/pep-*.rst")))
            st.metric("PEP Files Downloaded", raw_pep_count)
        
        st.divider()
        
        # Quick Links
        st.subheader("Quick Links")
        st.link_button("View on GitHub", "https://github.com/Anusha0501/calyb-ai", use_container_width=True)
        st.link_button("Read Documentation", "https://github.com/Anusha0501/calyb-ai/blob/main/README.md", use_container_width=True)

# Tab 1: Ask Questions
def tab_ask_questions(graph):
    """Render the Ask Questions tab."""
    st.header("❓ Ask Questions")
    st.markdown("Ask questions about Python typing evolution and get evidence-based recommendations from the knowledge graph.")
    
    if graph is None:
        st.error("Knowledge graph has not been built. Please run the following commands:")
        st.code("""
python -m src.main download
python -m src.main build
""", language="bash")
        return
    
    # Example queries
    example_queries = [
        "Why was Protocol introduced?",
        "How did generic typing evolve?",
        "Why are type hints optional?",
        "What tradeoffs led to PEP 695?",
        "How did Python typing evolve?",
        "I want runtime type checking",
        "How should covariance be implemented?"
    ]
    
    # Initialize session state for query input
    if "query_input" not in st.session_state:
        st.session_state.query_input = ""
    
    # Callback function for example buttons
    def set_query(example_query):
        st.session_state.query_input = example_query
    
    # Query input
    query = st.text_input(
        "Enter your question about Python typing:",
        placeholder="Why was Protocol introduced?",
        key="query_input"
    )
    
    # Example buttons
    st.markdown("**Example Queries:**")
    cols = st.columns(4)
    for i, example in enumerate(example_queries):
        col = cols[i % 4]
        col.button(example, key=f"example_{i}", use_container_width=True, on_click=set_query, args=(example,))
    
    # Analyze button
    if st.button("🔍 Analyze", type="primary", use_container_width=True):
        if not query:
            st.warning("Please enter a question.")
            return
        
        with st.spinner("Analyzing your question..."):
            try:
                reasoner = Reasoner(graph)
                result = reasoner.reason(query)
                
                # Display results
                st.success("Analysis Complete")
                
                # Confidence Score
                confidence = result.get("ConfidenceScore", 0)
                st.subheader(f"Confidence Score: {confidence:.2%}")
                st.progress(confidence)
                
                # Relevant PEPs
                if result.get("RelevantPEPs"):
                    with st.expander("📄 Relevant PEPs", expanded=True):
                        for pep in result["RelevantPEPs"]:
                            st.write(f"• {pep}")
                
                # Historical Decisions
                if result.get("HistoricalDecisions"):
                    with st.expander("🎯 Historical Decisions"):
                        for decision in result["HistoricalDecisions"]:
                            st.write(f"• {decision}")
                
                # Tradeoffs
                if result.get("Tradeoffs"):
                    with st.expander("⚖️ Tradeoffs"):
                        for tradeoff in result["Tradeoffs"]:
                            st.write(f"• {tradeoff}")
                
                # Rejected Alternatives
                if result.get("RejectedAlternatives"):
                    with st.expander("❌ Rejected Alternatives"):
                        for alt in result["RejectedAlternatives"]:
                            st.write(f"• {alt}")
                
                # Evidence
                if result.get("Evidence"):
                    with st.expander("🔍 Evidence", expanded=False):
                        for i, evidence in enumerate(result["Evidence"][:10]):  # Show first 10
                            st.write(f"**{i+1}. {evidence.get('relationship', 'Unknown')}**")
                            st.write(f"Node: {evidence.get('node', 'N/A')}")
                            st.write(f"Source: PEP {evidence.get('source_pep', 'N/A')}")
                            st.write(f"Section: {evidence.get('section', 'N/A')}")
                            st.write(f"Confidence: {evidence.get('confidence', 0):.2%}")
                            st.caption(f"\"{evidence.get('sentence', '')[:200]}...\"")
                            st.divider()
                
                # Suggested Reading Order
                if result.get("SuggestedReadingOrder"):
                    st.subheader("📚 Suggested Reading Order")
                    for i, pep in enumerate(result["SuggestedReadingOrder"], 1):
                        st.write(f"{i}. {pep}")
                
            except Exception as e:
                st.error(f"Error during analysis: {e}")

# Tab 2: Explore Knowledge Graph
def tab_explore_graph(graph):
    """Render the Explore Knowledge Graph tab."""
    st.header("🔍 Explore Knowledge Graph")
    
    if graph is None:
        st.error("Knowledge graph has not been built. Please run the build commands first.")
        return
    
    # Graph Statistics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Nodes", len(graph.nodes))
    col2.metric("Total Relationships", len(graph.edges))
    
    # Calculate average degree
    if graph.nodes:
        avg_degree = sum(len(graph.adjacency.get(node_id, set())) for node_id in graph.nodes) / len(graph.nodes)
        col3.metric("Average Degree", f"{avg_degree:.2f}")
    else:
        col3.metric("Average Degree", "0")
    
    col4.metric("Node Types", len(set(node.type for node in graph.nodes.values())))
    
    st.divider()
    
    # Node Type Distribution
    st.subheader("Node Type Distribution")
    node_types = {}
    for node in graph.nodes.values():
        node_type = node.type
        node_types[node_type] = node_types.get(node_type, 0) + 1
    
    col1, col2 = st.columns(2)
    with col1:
        st.bar_chart(node_types)
    with col2:
        for node_type, count in sorted(node_types.items()):
            st.write(f"**{node_type}**: {count}")
    
    st.divider()
    
    # Download GraphML
    if GRAPHML_PATH.exists():
        st.subheader("Download Graph")
        with open(GRAPHML_PATH, 'rb') as f:
            st.download_button(
                label="📥 Download GraphML File",
                data=f,
                file_name="graph.graphml",
                mime="application/xml"
            )
    else:
        st.info("GraphML file not available.")
    
    st.divider()
    
    # Searchable Node Table
    st.subheader("Search Nodes")
    
    # Filter by node type
    all_types = sorted(set(node.type for node in graph.nodes.values()))
    selected_type = st.selectbox("Filter by Node Type", ["All"] + all_types)
    
    # Search by name
    search_term = st.text_input("Search by Name", placeholder="Enter node name...")
    
    # Filter nodes
    filtered_nodes = []
    for node_id, node in graph.nodes.items():
        if selected_type != "All" and node.type != selected_type:
            continue
        if search_term and search_term.lower() not in node.label.lower():
            continue
        filtered_nodes.append({
            "ID": node_id,
            "Type": node.type,
            "Name": node.label,
            "Metadata": str(node.metadata)[:100] if node.metadata else ""
        })
    
    # Display table
    if filtered_nodes:
        st.dataframe(
            filtered_nodes,
            use_container_width=True,
            height=400
        )
    else:
        st.info("No nodes match your filters.")

# Tab 3: Browse PEPs
def tab_browse_peps(parsed_peps):
    """Render the Browse PEPs tab."""
    st.header("📄 Browse PEPs")
    
    if not parsed_peps:
        st.error("No PEP data available. Please run the build commands first.")
        return
    
    # PEP selector
    pep_options = [f"PEP {pep['number']}: {pep['title']}" for pep in parsed_peps]
    selected_pep_display = st.selectbox("Select a PEP", pep_options)
    
    if not selected_pep_display:
        return
    
    # Find selected PEP
    pep_number = int(selected_pep_display.split(":")[0].split()[1])
    selected_pep = next((pep for pep in parsed_peps if pep["number"] == pep_number), None)
    
    if not selected_pep:
        return
    
    # Display PEP information
    col1, col2, col3 = st.columns(3)
    col1.metric("PEP Number", selected_pep["number"])
    col2.metric("Status", selected_pep["status"])
    col3.metric("Python Version", selected_pep.get("python_version", "N/A"))
    
    st.subheader(selected_pep["title"])
    
    # Authors
    st.write(f"**Authors:** {', '.join(selected_pep['authors'])}")
    st.write(f"**Type:** {selected_pep['type']}")
    st.write(f"**Created:** {selected_pep['created']}")
    
    st.divider()
    
    # Mentioned PEPs
    if selected_pep.get("mentioned_peps"):
        st.subheader("Referenced PEPs")
        for pep_ref in selected_pep["mentioned_peps"]:
            st.write(f"• {pep_ref}")
    
    # Sections
    if selected_pep.get("sections"):
        st.subheader("Sections")
        for slug, section in selected_pep["sections"].items():
            with st.expander(f"📖 {section['title']} ({section['paragraph_count']} paragraphs)"):
                st.write(f"**Preview:**")
                for preview in section.get("preview", []):
                    st.write(preview)
                st.caption(f"Section ID: {slug}")

# Tab 4: Project Information
def tab_project_info():
    """Render the Project Information tab."""
    st.header("ℹ️ Project Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Architecture")
        st.markdown("""
```
Official Python PEPs
        │
        ▼
    Downloader
        │
        ▼
      Parser
        │
        ▼
Entity Extraction
        │
        ▼
Relationship Extraction
        │
        ▼
  Knowledge Graph
        │
        ▼
 Reasoning Engine
        │
        ▼
Structured Recommendation
```
""")
    
    with col2:
        st.subheader("Entity Types")
        st.markdown("""
- **PEP** - Python Enhancement Proposals
- **Feature** - Specific typing features
- **Concept** - Typing concepts and ideas
- **Decision** - Design decisions made
- **Tradeoff** - Design tradeoffs considered
- **RejectedAlternative** - Rejected design alternatives
- **Problem** - Problems being solved
- **Author** - PEP authors
- **PythonRelease** - Target Python versions
- **Section** - PEP document sections
- **External** - External references
""")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Relationship Types")
        st.markdown("""
- **INTRODUCES** - Introduces new features/concepts
- **SOLVES** - Solves specific problems
- **REFERENCES** - References other PEPs
- **SUPERSEDES** - Supersedes previous proposals
- **HAS_TRADEOFF** - Has associated tradeoffs
- **REJECTS** - Rejects alternatives
- **DISCUSSES** - Discusses topics
- **AUTHORED_BY** - Written by authors
- **TARGETS_RELEASE** - Targets Python release
- **RELATED_TO** - Related to other nodes
""")
    
    with col2:
        st.subheader("Reasoning Algorithm")
        st.markdown("""
The reasoning engine uses deterministic scoring:

```
overall =
  40% concept overlap
  30% explicitly shared PEP reference
  20% graph distance from requested concepts
  10% supporting relationship count
```

This makes the scoring explainable and easy to adjust.
""")
    
    st.divider()
    
    st.subheader("Engineering Tradeoffs")
    st.markdown("""
- **Custom Graph**: Keeps dependency surface small and makes traversal behavior explicit
- **Rule-based Extraction**: Less flexible than statistical extraction, but predictable and auditable
- **Lightweight Parsing**: Handles common PEP RST patterns without full reStructuredText parser
- **Scoring**: Favors readability over machine-learned ranking quality
- **Testing**: Uses in-memory fixtures; real data obtained through official downloader
""")
    
    st.divider()
    
    st.subheader("Confidence Scoring")
    st.info("""
Confidence values are rule confidence estimates, not statistical probabilities.
They reflect the certainty of the extraction rules and relationship patterns.
""")
    
    st.divider()
    
    st.subheader("Dataset Coverage")
    st.markdown("""
The system currently covers 26 typing-related PEPs:

**Core PEPs**: 3107, 483, 484, 526, 544, 560, 563, 585, 586, 589
**Advanced PEPs**: 591, 593, 604, 612, 613, 646, 647, 655, 673, 675
**Recent PEPs**: 681, 692, 695, 696, 698, 705

These PEPs represent the evolution of Python typing from function annotations
to modern type parameter syntax.
""")

# Main application
def main():
    """Main Streamlit application."""
    # Load data
    graph = load_knowledge_graph()
    parsed_peps = load_parsed_peps()
    
    # Render sidebar
    render_sidebar(graph, parsed_peps)
    
    # Main title
    st.title("🐍 Python Typing Knowledge Reasoning System")
    st.markdown("Knowledge graph built from official Python Enhancement Proposals using deterministic rule-based extraction and explainable graph reasoning.")
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs(["❓ Ask Questions", "🔍 Explore Graph", "📄 Browse PEPs", "ℹ️ Project Info"])
    
    with tab1:
        tab_ask_questions(graph)
    
    with tab2:
        tab_explore_graph(graph)
    
    with tab3:
        tab_browse_peps(parsed_peps)
    
    with tab4:
        tab_project_info()

if __name__ == "__main__":
    main()
