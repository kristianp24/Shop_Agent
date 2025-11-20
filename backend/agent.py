from env_checker import check_env_variables
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from runtime_context import RuntimeContex
from system_prompt import  SYSTEM_PROMPT
import os
from dotenv import load_dotenv
from supabase.client import Client, create_client
from langgraph.checkpoint.memory import InMemorySaver
from tools import query_table, query_all_names, update_quantity, delete_record, insert_record, get_total_stock_value, get_general_information
# load_dotenv()
check_env_variables()
class ShopAgent:
    def __init__(self):
        self._llm = ChatGoogleGenerativeAI(model = "gemini-2.5-flash")
        self.client = self.create_supabase_client()
       
        self._agent = create_agent(
            model = self._llm,
            tools=[query_table, query_all_names, update_quantity, delete_record, insert_record, delete_record, get_total_stock_value, get_general_information],
            system_prompt= SYSTEM_PROMPT,
            context_schema=RuntimeContex,
            checkpointer= InMemorySaver()
        )
    
    def create_supabase_client(self):
        url: str = os.environ.get("PROJECT_URL")
        key: str = os.environ.get("PROJECT_API")
        client: Client = create_client(url, key)
        return client

 