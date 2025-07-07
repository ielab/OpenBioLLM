from langgraph.graph import StateGraph, END
from .component import BlastComponent
from typing import Annotated, Sequence
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

# Define state type
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    metadata: dict  # Add metadata field for data transfer between nodes

def create_blast_subgraph():
    """Create a subgraph with complete BLAST query process"""
    # Instantiate BLAST component
    blast_component = BlastComponent()
    
    # Create subgraph
    workflow = StateGraph(AgentState)
    
    # Add nodes, remove analyze_results node
    workflow.add_node("init_query", blast_component.init_blast_query)
    workflow.add_node("fetch_results", blast_component.fetch_blast_results)
    
    # Set entry point
    workflow.set_entry_point("init_query")
    
    # Add conditional edges
    workflow.add_conditional_edges(
        "init_query",
        lambda x: x.get("next", END) if "next" in x else END,
        {
            "fetch_results": "fetch_results",
            END: END
        }
    )
    
    workflow.add_conditional_edges(
        "fetch_results",
        lambda x: x.get("next", END) if "next" in x else END,
        {
            "fetch_results": "fetch_results",  # Loop to fetch results until completion or timeout
            END: END
        }
    )
    
    # Compile subgraph
    return workflow.compile()