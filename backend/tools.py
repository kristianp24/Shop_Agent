from langchain_core.tools import tool
from langgraph.runtime import get_runtime
from runtime_context import RuntimeContex

@tool
def query_table(product_name: str):
    """Executes a SELECT sql command
    Args:
        product_name, the name of the product we want to query the database
        """
    # runtime = get_runtime(RuntimeContex)
   
    try:
        runtime_config = get_runtime(RuntimeContex)  
        supabase_client = runtime_config.context.db
        response = supabase_client.table("products").select("quantity").eq('product_name', product_name).execute()
        if response.data and len(response.data) > 0:
            quantity = response.data[0]['quantity']
            return f"Current stock for '{product_name}' is {quantity} units."
        else:
            return f"The product {product_name} not found in the table"
    except Exception as e:
        return f"An error occured {e}"
                                        
    