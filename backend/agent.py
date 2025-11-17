from env_checker import check_env_variables
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from runtime_context import RuntimeContex
from system_prompt import  SYSTEM_PROMPT
import os
from dotenv import load_dotenv
from supabase.client import Client, create_client
from tools import query_table
# load_dotenv()
check_env_variables()
class ShopAgent:
    def __init__(self):
        self._llm = ChatGoogleGenerativeAI(model = "gemini-2.5-flash")
        self.client = self.create_supabase_client()
        print("HEREE-------", self.client.supabase_url)
        print("HEREE-------", self.client.supabase_key)

        self._agent = create_agent(
            model = self._llm,
            tools=[query_table],
            system_prompt= SYSTEM_PROMPT,
            context_schema=RuntimeContex
        )
    
    def create_supabase_client(self):
        url: str = os.environ.get("PROJECT_URL")
        key: str = os.environ.get("PROJECT_API")
        client: Client = create_client(url, key)
        return client

 