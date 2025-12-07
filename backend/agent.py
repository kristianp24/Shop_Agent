import io
from env_checker import check_env_variables
from langchain_google_genai import ChatGoogleGenerativeAI
from system_prompt import  SYSTEM_PROMPT
import os
from langgraph.graph import StateGraph
from langchain_core.messages import ToolMessage, SystemMessage
from langgraph.prebuilt import ToolNode
from supabase.client import Client, create_client
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command
from typing import Literal
from state import AgentState
from bills_models import Bill
from bill_pdf_creator import BillPdfCreator
from datetime import datetime
from whatsapp_sender import WhatsappSender
import base64
from langgraph.runtime import get_runtime
from runtime_context import RuntimeContex
from bill_tools import get_bills_for_client

from tools import query_table, query_all_names, update_quantity, delete_record, insert_record, get_total_stock_value, get_general_information, get_most_valuable_product, get_less_products, get_top_products
check_env_variables()
class ShopAgent:
    def __init__(self):
        self.tools = [query_table, query_all_names, update_quantity, insert_record, delete_record, get_total_stock_value, get_general_information, get_less_products, get_top_products, Bill, get_bills_for_client]
        self._llm = ChatGoogleGenerativeAI(model = "gemini-2.5-flash").bind_tools(self.tools)
        self.client = self.create_supabase_client()
       
        self._agent = self.create_graph()
        
    def create_supabase_client(self):
        url: str = os.environ.get("PROJECT_URL")
        key: str = os.environ.get("PROJECT_API")
        client: Client = create_client(url, key)
        return client
    
    def call_model(self, state: AgentState) -> Command[Literal["selection_node", "tools", "bill_processing", "bill_inventory_node", "__end__"]]:
        messages = state["messages"]
        system_message = SystemMessage(SYSTEM_PROMPT)
        
        response = self._llm.invoke([system_message] + messages)
        goto = ""
        
        if not response.tool_calls:
            goto = "__end__"
        elif response.tool_calls[0]['name'] == "query_table":
            goto = "selection_node"
        elif response.tool_calls[0]['name'] == "Bill":
            goto = "bill_processing"
        elif response.tool_calls[0]['name'] == "get_bills_for_client":
            goto = "bill_inventory_node"
        else:
            goto = "tools"
        
        
        return Command(
            update= AgentState(messages=[response]),
            goto = [goto]
        )
    

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
    
    def bill_processing_node(self, state: AgentState):

        last_message = state['messages'][-1]
        tool_call = last_message.tool_calls[0]
        bill_data = tool_call["args"]
        name = bill_data.get("customer_name", "Customer")
        date = bill_data.get("date", datetime.now().strftime("%d-%m-%Y"))
        items = bill_data.get("items", [])
        total_amount = bill_data.get("total_amount", 0.0)
        phone_number = bill_data.get("recipient_contact", None)


        
        print("Processing bill with tool call:", bill_data)
        pdf_creator = BillPdfCreator(name, date, items, total_amount)
        buffer_pdf = pdf_creator.create_pdf("invoice.pdf")
        encoded_pdf = base64.b64encode(buffer_pdf.getvalue()).decode('utf-8')
        return {
            "messages": [
                ToolMessage(
                    tool_call_id=tool_call["id"], 
                    content=f"Bill generated successfully.",
                    name="bill_processing",
                    artifact={
                        "pdf_base64": encoded_pdf,
                        "phone_number": phone_number,
                        "bill_data": bill_data
                    }
                )
            ]
        }
    
    def bills_database_updater(self, state: AgentState):
        last_message = state['messages'][-1]
        values = last_message.artifact
        bill_data = values.get("bill_data", {})

        if bill_data:
            data_for_costumers = {
                "name": bill_data.get("customer_name"),
                "date_acquisiton": bill_data.get("date"),
            }
            try:
                runtime_config = get_runtime(RuntimeContex)
                supabase_client = runtime_config.context.db
                customer_response = supabase_client.table("costumer").insert(data_for_costumers).execute()
               
                new_customer_id = customer_response.data[0]['id']
                
                items = bill_data.get("items", [])
                for item in items:
                    product_name = item.get("product_name")
                    quantity = item.get("quantity")
                    query = supabase_client.table("products").select("id").ilike('product_name', product_name).execute()
                    if query.data and len(query.data) > 0:
                        product_id = query.data[0]['id']
                        bill_record = {
                            "costumer_id": new_customer_id,
                            "product_id": product_id,
                            "quantity": int(quantity),
                            "unit_price": item.get("unit_price"),
                            "total_value": item.get("total_price"),
                        }
                        bill_response = supabase_client.table("orders").insert(bill_record).execute()
                        
                    else:
                        return f"Product {product_name} not found in database."
                

            except Exception as e:
                return f"An error occured {e}"
        return {"messages": [
                ToolMessage(
                    tool_call_id=last_message.tool_call_id,
                    content="Bill data inserted into database successfully.",
                    name="bills_database_updater"
                )]}

    def bill_inventory_node(self, state: AgentState):
        last_message = state['messages'][-1]
        tool_call = last_message.tool_calls[0]

        data = get_bills_for_client.invoke(tool_call["args"]["client_name"])
        
        return {
            "messages": [
                ToolMessage( 
                    tool_call_id=tool_call["id"],
                    content=f"Print the following bills: {data}",
                    name="bill_inventory_node"
                )
            ]
        }

        

  

    def whatsapp_sender_node(self, state: AgentState):
        last_message = state['messages'][-1]
        value = last_message.artifact
        
        pdf_bytes = base64.b64decode(value["pdf_base64"])
        pdf = io.BytesIO(pdf_bytes)
        pdf.seek(0)

        whatsapp_sender = WhatsappSender()
        send_result, status = whatsapp_sender.send_bill("invoice.pdf", pdf, datetime.now().strftime("%d-%m-%Y"))
        if status == -1:
            send_result = f"{send_result}. Saving it into local file 'failed_invoice.pdf'."
            with open("failed_invoice.pdf", "w") as f:
                f.write(pdf.read())
        
        return {
            "messages": [
                ToolMessage( 
                    tool_call_id=last_message.tool_call_id,
                    content=f"{send_result}",
                    name="whatsapp_sender"
                )
            ]
        }


    def create_graph(self):
        workflow = StateGraph(AgentState)

        workflow.add_node("selection_node", self.selection_node)
        workflow.add_node("intent classifier", self.call_model)
        workflow.add_node("tools", ToolNode(self.tools))
        workflow.add_node("bill_processing", self.bill_processing_node)
        workflow.add_node("whatsapp_sender", self.whatsapp_sender_node)
        workflow.add_node("bill_database_updater", self.bills_database_updater)
        workflow.add_node("bill_inventory_node", self.bill_inventory_node)

        workflow.set_entry_point("intent classifier")

        workflow.add_edge("selection_node", "intent classifier")
        workflow.add_edge("tools", "intent classifier")
        workflow.add_edge("bill_processing", "whatsapp_sender")
        workflow.add_edge("bill_processing", "bill_database_updater")
        workflow.add_edge("bill_database_updater", "__end__")
        workflow.add_edge("whatsapp_sender", "__end__")
        workflow.add_edge("bill_inventory_node", "intent classifier")

        return workflow.compile(checkpointer=InMemorySaver())
 