
from typing import TypedDict, Annotated
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages
import operator

class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    target_product: str | None  
    action: str | None # Here we save either if it is a deletion, insert or update