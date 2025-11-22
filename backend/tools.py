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
        response = supabase_client.table("products").select("quantity").ilike('product_name', product_name).execute()
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

@tool("delete_record", description= "Deletes the record for the given product name")
def delete_record(product_name : str):
    """
        This function is responsible for performing a delete opeation on the database for the product_name given.
        Args:
            product_name: str -> The name of the product to be deleted.
    """
    try:
        runtimeconfig = get_runtime(RuntimeContex)
        supabase_client = runtimeconfig.context.db
        response = supabase_client.table("products").delete().eq("product_name", product_name).execute()
        return response.count
    except Exception as e:
        return f"Error on deleting the record {e}"
    
@tool("insert_product", description= "This method is responsabile for inserting a new row in the table")
def insert_record(product_name: str, quantity: int, price: float, product_code: str = "NA"):
    """
        This tool is responsabile for adding new rows to the table of products
        Args:
            product_name: str -> The name of the product to be added
            quantity: int -> The quantity of the product
            price: float -> The price for 1 piece
            product_code: str = "NA" -> In case the user does not provide this then this function will generate a random code
    """
    try:
        runtime_config = get_runtime(RuntimeContex)
        supabase_client = runtime_config.context.db
        if product_code == "NA":
            product_code = product_name + "123G"
        
        values_to_insert = {
            "product_code": product_code,
            "product_name": product_name,
            "quantity": quantity,
            "price_per_piece": price
        }
        
        response = supabase_client.table("products").insert(values_to_insert).execute()
        return response.count
    except Exception as e:
        return f"An error occured in insertion {e}"
    
@tool("stock_value", description="This tool calculates how much stock is in the shop in terms of money.")
def get_total_stock_value():
    """
        Calculates the total value of all the products (price * quantity)
    """
    try:
        runtime_config = get_runtime(RuntimeContex)
        supabase_client = runtime_config.context.db

        response = supabase_client.rpc("get_total_inventory_value").execute()
        return response.data if response.data else -1
    except Exception as e:
        return f"An error occured during geting the total stock value {e}"
    
@tool("general_information", description="This tool is for selecting all columns for a certain product")
def get_general_information(product_name: str):
    """
        This functions queries all the columns for a certain product name.
        Args:
            product_name: str
    """
    try:
        runtime_config = get_runtime(RuntimeContex)
        supabase_client = runtime_config.context.db

        response = supabase_client.table("products").select("*").ilike("product_name", product_name).execute()
        return response.data
    except Exception as e:
        return f"An error occured {e}"

@tool("most_valuable_product", description="This tool is used to obtain the product with the biggest value")
def get_most_valuable_product():
    try:
        runtime_config = get_runtime(RuntimeContex)
        supabase = runtime_config.context.db
        response = supabase.rpc("get_product_max_values").execute()
        return response.data
    except Exception as e:
        return f"An error occured {e}"

@tool("top_10_products", description="This tool is used to select the top products with by their values(price*quantity)")
def get_top_products(nr_products: int = 5):
    """
        Returns the top {nr_products} with the biggest value.
        Args:
            nr_products: int -> the number to limit the query, if not given falls back to 5.
    """
    try:
        runtime_config = get_runtime(RuntimeContex)
        supabase = runtime_config.context.db
        response = supabase.rpc("get_top_most_valuable_products", {"limit_count": nr_products}).execute()
        return response.data
    except Exception as e:
        return f"An error occured {e}"

@tool("less_10_products", description="This tool is used to select the less 10 products with by their values(price*quantity)")
def get_less_products(nr_products: int = 5):
    """
        Returns the less {nr_products} with the lowest values.
        Args:
            nr_products: int -> the number to limit the query, if not given falls back to 5.
    """
    try:
        runtime_config = get_runtime(RuntimeContex)
        supabase = runtime_config.context.db
        response = supabase.rpc("get_less_valuable_products", {"limit_count": nr_products}).execute()
        return response.data
    except Exception as e:
        return f"An error occured {e}"