from typing import Annotated, Sequence, Optional, Dict, Any
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph import StateGraph, END, START
from langgraph.graph.message import add_messages
from .router import Router
from .evaluator import Evaluator
from .generator import Generator
from ..agents.eutils_agent.graph import create_eutils_subgraph
from ..agents.blast_agent.graph import create_blast_subgraph
from ..agents.search_agent.graph import create_search_subgraph

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    status: str 
    error: Optional[str]  # Add error information field
    metadata: Dict[str, Any]  # Add metadata field

def initialize_rag_system():
    # Create components
    router = Router()
    evaluator = Evaluator()
    generator = Generator()
    
    # Create workflow
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("router", router.route)
    workflow.add_node("evaluator", evaluator.evaluate)
    workflow.add_node("generator", generator.generate)
    workflow.add_node("eutils_agent", create_eutils_subgraph())
    workflow.add_node("blast_agent", create_blast_subgraph())
    workflow.add_node("search_agent", create_search_subgraph())  # Add search agent
    
    # Add edges
    workflow.add_edge(START, "router")  # From START to router
    
    # Router's conditional routing
    workflow.add_conditional_edges(
        "router",
        lambda x: END if x.get("status") == "error" else x["next"],
        {
            "eutils_agent": "eutils_agent",
            "blast_agent": "blast_agent",
            "search_agent": "search_agent",  # Add search agent's edge
            "irrelevant_questions": "generator",
        }
    )
    
    # Agent's conditional routing
    for agent in ["eutils_agent", "blast_agent", "search_agent"]:  # Add search_agent
        workflow.add_conditional_edges(
            agent,
            lambda x: END if x.get("status") == "error" else "evaluator",
            {
                "evaluator": "evaluator",
            }
        )
    
    # Evaluator's conditional routing
    workflow.add_conditional_edges(
        "evaluator",
        lambda x: (
            END if x.get("status") == "error" 
            else x["next"]  # "generate" or "router"
        ),
        {
            "generate": "generator",
            "router": "router",
        }
    )
    
    # Generator generates final answer
    workflow.add_edge("generator", END)
    
    # Compile workflow
    graph = workflow.compile()
    
    # Print Mermaid format graph
    print("\nMermaid Graph:")
    print("```mermaid")
    print(graph.get_graph().draw_mermaid())
    print("```")
    
    return graph