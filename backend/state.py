
from typing import TypedDict, Annotated
from langchain_core.messages import AnyMessage
import operator

class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
    target_product: str | None  
    action: str | None # Here we save either if it is a deletion, insert or update