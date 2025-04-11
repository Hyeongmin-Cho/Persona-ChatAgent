from typing import Annotated, TypedDict
from langgraph.graph.message import add_messages

class ConversationState(TypedDict):
    messages: Annotated[list, add_messages]
    documents: list
    web_query: Annotated[list, add_messages]
    web_search_flag: bool
    generation: str
    retry_flag: bool
    retries: int
    profile: dict