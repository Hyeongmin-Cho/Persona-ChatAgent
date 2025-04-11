from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from src.schema.states import ConversationState
from src.graph.nodes import (
    profiling,
    route_message,
    check_profiling,
    profile_web_search,
    retriever,
    evaluate_documents,
    decide_generation,
    web_search,
    generate,
    evaluate_generation,
    decide_response,
    rewrite_query
)

def create_persona_graph():
    """
    Create the character chatbot conversation graph.
    """
    # State 정의
    PersonaGraph = StateGraph(ConversationState)
    
    # Node 정의
    PersonaGraph.add_node(profiling)
    PersonaGraph.add_node(profile_web_search)
    PersonaGraph.add_node(retriever)
    PersonaGraph.add_node(evaluate_documents)
    PersonaGraph.add_node(web_search)
    PersonaGraph.add_node(generate)
    PersonaGraph.add_node(evaluate_generation)
    PersonaGraph.add_node(rewrite_query)
    
    # Edge 정의
    PersonaGraph.add_conditional_edges(
        START,
        route_message,
        {
            "retriever": "retriever",
            "profiling": "profiling",
        }
    )
    PersonaGraph.add_conditional_edges(
        "profiling",
        check_profiling,
        {
            "profile_web_search": "profile_web_search",
            "insufficient": END
        }
    )
    PersonaGraph.add_edge("profile_web_search", END)
    PersonaGraph.add_edge("retriever", "evaluate_documents")
    PersonaGraph.add_conditional_edges(
        "evaluate_documents",
        decide_generation,
        {
            "generate": "generate",
            "web_search": "web_search",
        }
    )
    PersonaGraph.add_edge("web_search", "generate")
    PersonaGraph.add_edge("generate", "evaluate_generation")
    PersonaGraph.add_conditional_edges(
        "evaluate_generation",
        decide_response,
        {
            "response": END,
            "rewrite_query": "rewrite_query"
        }
    )
    PersonaGraph.add_edge("rewrite_query", "retriever")

    memory = MemorySaver()
    app = PersonaGraph.compile(checkpointer=memory)

    return app

def get_persona_graph():
    graph = create_persona_graph()
    return graph