from langgraph.graph import StateGraph, END
from .component import EutilsComponent
from typing import Annotated, Sequence
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

# Define state type - same as BLAST
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    metadata: dict  # For data transfer between nodes

def create_eutils_subgraph():
    """Create a subgraph with complete E-utilities query process"""
    # Instantiate E-utils component
    eutils_component = EutilsComponent()
    
    # Create subgraph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("init_search", eutils_component.init_search)
    workflow.add_node("fetch_details", eutils_component.fetch_details)
    
    # Set entry point
    workflow.set_entry_point("init_search")
    
    # Add conditional edges
    workflow.add_conditional_edges(
        "init_search",
        lambda x: x.get("next", END) if "next" in x else END,
        {
            "fetch_details": "fetch_details",
            END: END
        }
    )
    
    # After fetch_details, end
    workflow.add_edge("fetch_details", END)
    
    # Compile subgraph
    return workflow.compile()