from langchain_core.tools import tool
from langgraph.runtime import get_runtime
from runtime_context import RuntimeContex

@tool(description="Updates the inventory based on the generated bill.")
def get_bills_for_client(client_name: str):
    """
    Docstring for get_bills_for_client. it returns the products bought by a specific client.
    The products make up the bill of that client.
    
    :param client_name: Description
    :type client_name: str
    """
    try:
        runtime_config = get_runtime(RuntimeContex)
        supabase_client = runtime_config.context.db

        query = supabase_client.table("view_transactions").select("*").ilike('costumer_name', client_name).execute()
        if query.data and len(query.data) > 0:
            return query.data
        else:
            return f"Customer {client_name} not found in database."
    except Exception as e:
        return f"An error occurred: {e}"