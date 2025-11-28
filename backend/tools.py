from langchain_core.tools import tool
from langgraph.runtime import get_runtime
from runtime_context import RuntimeContex
import datetime
from models_update_insert_delete import InsertItem, DeleteItem, UpdateQuantityItem, InsertItemsList, DeleteItemsList, UpdateQuantityItemsList
from typing import List

@tool("table_query", description="Executes a SELECT sql command", args_schema=DeleteItemsList)
def query_table(product_names: List[DeleteItem]):
    """Executes a SELECT sql command
    Args:
        product_names: List[DeleteItem], the names of the products
          we want to query the database
        """
    try:
        runtime_config = get_runtime(RuntimeContex)  
        supabase_client = runtime_config.context.db
        responses = {}
        for record in product_names:
            response = supabase_client.table("products").select("quantity").ilike('product_name', record.product_name).execute()
            if response.data and len(response.data) > 0:
                quantity = response.data[0]['quantity']
                responses[record.product_name] = quantity
            else:
                responses[record.product_name] = None
        return responses
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

@tool("quantity_updater", description="Updates the quantity columns for a given product_name", args_schema=UpdateQuantityItemsList)
def update_quantity(records : List[UpdateQuantityItem]):
    """
        This function is responsible for updating the quantity of a certain product_name.
        Args:
            records: List[UpdateQuantityItem] -> A list of pydantic types containing the product_name, previous_quantity and quantity_to_be_added.                     
    """
    try:
        runtime_config = get_runtime(RuntimeContex)
        supabase_client = runtime_config.context.db
        responses = []
        for record in records:
            product_name = record.product_name
            previous_quantity = record.previous_quantity
            quantity_to_be_added = record.quantity_to_be_added
            data_to_be_updated = {
                "quantity" : previous_quantity + quantity_to_be_added,
                "date_updated": datetime.datetime.now().isoformat()
            }
            response = supabase_client.table("products").update(data_to_be_updated).eq("product_name", product_name).execute()
            responses.append(response.data)
        return responses
    except Exception as e:
        return f"An error occured {e}"

@tool("delete_record", description= "Deletes the record for the given product name", args_schema=DeleteItemsList)
def delete_record(product_names : List[DeleteItem]):
    """
        This function is responsible for performing a delete opeation on the database for the product_name given.
        Args:
            product_names: List[DeleteItem] -> The names of the products to be deleted.
    """
    try:
        runtimeconfig = get_runtime(RuntimeContex)
        supabase_client = runtimeconfig.context.db
        responses = []
        for record in product_names:
            product_name = record.product_name
            response = supabase_client.table("products").delete().eq("product_name", product_name).execute()
            responses.append(response.count)
        return responses
    except Exception as e:
        return f"Error on deleting the record {e}"
    
@tool("insert_product", description= "This method is responsabile for inserting a new row in the table, More than one row can be inserted.", args_schema=InsertItemsList)
def insert_record(records : List[InsertItem]):
    """
        This tool is responsabile for adding new rows to the table of products
        Args:
            records: List[InsertItem] -> A list of pydantic types containing the product_name, quantity and price_per_piece. Product_code is a optional one.
    """
    try:
        runtime_config = get_runtime(RuntimeContex)
        supabase_client = runtime_config.context.db
        responses = []
        for record in records:
            product_name = record.product_name
            quantity = record.quantity
            price = record.unit_price
            product_code = record.product_code if record.product_code else f"{product_name}123G"
        
            values_to_insert = {
                "product_code": product_code,
                "product_name": product_name,
                "quantity": quantity,
                "price_per_piece": price
            }
        
            response = supabase_client.table("products").insert(values_to_insert).execute()
            responses.append(response.count)
        return responses
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

@tool("top_products", description="This tool is used to select the top products with by their values(price*quantity)")
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

@tool("less_products", description="This tool is used to select the less 10 products with by their values(price*quantity)")
def get_less_products(nr_products: int = 5):
    """
        Returns the less {nr_products} with the lowest values.
        Args:
            nr_products: int -> the number to limit the query, if not given falls back to 5.
    """
    try:
        runtime_config = get_runtime(RuntimeContex)
        supabase = runtime_config.context.db
        response = supabase.rpc("get_product_values", {"limit_count": nr_products}).execute()
        return response.data
    except Exception as e:
        return f"An error occured {e}"

