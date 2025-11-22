from env_checker import check_env_variables
from langchain_google_genai import ChatGoogleGenerativeAI
from system_prompt import  SYSTEM_PROMPT
import os
from langgraph.graph import StateGraph
from langchain_core.messages import ToolMessage, SystemMessage
from langgraph.prebuilt import ToolNode
from supabase.client import Client, create_client
from langgraph.checkpoint.memory import InMemorySaver
from state import AgentState
from tools import query_table, query_all_names, update_quantity, delete_record, insert_record, get_total_stock_value, get_general_information
check_env_variables()
class ShopAgent:
    def __init__(self):
        self.tools = [query_table, query_all_names, update_quantity, insert_record, delete_record, get_total_stock_value, get_general_information]
        self._llm = ChatGoogleGenerativeAI(model = "gemini-2.5-flash").bind_tools(self.tools)
        self.client = self.create_supabase_client()
       
        self._agent = self.create_graph()
        
    def create_supabase_client(self):
        url: str = os.environ.get("PROJECT_URL")
        key: str = os.environ.get("PROJECT_API")
        client: Client = create_client(url, key)
        return client
    
    def call_model(self, state: AgentState):
        
        messages = state["messages"]
        system_message = SystemMessage(SYSTEM_PROMPT)
        
        response = self._llm.invoke([system_message] + messages)
        
        # We return the new message to add it to the history
        return {"messages": [response]}
    
    def router(self, state: AgentState):
        last_message = state['messages'][-1]

        if not last_message.tool_calls:
            return "__end__"
        
        tool_name = last_message.tool_calls[0]['name']
        if tool_name == "query_table":
            return "selection_node"
        else:
            return "tools"
    
    def selection_node(self, state: AgentState):
    
        # get the last message the user put
        last_message = state['messages'][-1]

        # Check if LLM is trying to call a tool (because it should call one)
        if not last_message.tool_calls:
            return {"messages": []}
        
        # Get the first tool call
        tool_call = last_message.tool_calls[0]
        target_product = tool_call["args"].get("product_name")

        if not target_product:
            return {"messages": []}
        
        response = query_table.invoke(target_product)

        return {
            "target_product": target_product,
            "messages": [
                ToolMessage(
                    tool_call_id=tool_call["id"], 
                    content=f"Availability Check: {response}",
                    name="query_table"
                )
            ]
        }
    
    def create_graph(self):
        workflow = StateGraph(AgentState)

        workflow.add_node("selection_node", self.selection_node)
        workflow.add_node("model", self.call_model)
        workflow.add_node("tools", ToolNode([query_all_names, update_quantity, insert_record, delete_record, get_total_stock_value, get_general_information]))

        workflow.set_entry_point("model")

        workflow.add_conditional_edges(
            "model",
            self.router,
            {
                "selection_node": "selection_node",
                "tools": "tools",
                "__end__": "__end__"
            }
        )

        workflow.add_edge("selection_node", "model")
        workflow.add_edge("tools", "model")

        return workflow.compile(checkpointer=InMemorySaver())
 