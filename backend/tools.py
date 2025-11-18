from langchain_core.tools import tool
from langgraph.runtime import get_runtime
from runtime_context import RuntimeContex
import datetime

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

                                        
@tool("all_names_selector", description="Selects the names of all available products in the database.")
def query_all_names():
    """
        Returns all names of available products in the store.
    """
    try:
        runtime_config = get_runtime(RuntimeContex)
        supabase_client = runtime_config.context.db
        response = supabase_client.table("products").select("product_name").execute()
        if response.data and len(response.data) > 0:
            return response.data
    except Exception as e:
        return f"An error occured {e}"

@tool("quantity_updater", description="Updates the quantity columns for a given product_name")
def update_quantity(product_name : str, previous_quantity : int, quantity_to_be_added : int = 0):
    """
        This function is responsible for updating the quantity of a certain product_name.
        Args:
            product_name : str -> The name of the product to be updated, very important.
            quantity_to_be_added : int = 0 -> The quantity to be added to the current quantity, if no quantity is provided from the user, 
                                just adds 0 to the current quantity value.
            previous_quantity: int -> The current quantity before update                        
    """
    try:
        runtime_config = get_runtime(RuntimeContex)
        supabase_client = runtime_config.context.db
        data_to_be_updated = {
            "quantity" : previous_quantity + quantity_to_be_added,
            "date_updated": datetime.datetime.now().isoformat()
        }
        response = supabase_client.table("products").update(data_to_be_updated).eq("product_name", product_name).execute()
        return response.data
    except Exception as e:
        return f"An error occured {e}"