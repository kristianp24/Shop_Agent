from agent import ShopAgent
from langchain_core.messages import HumanMessage
from runtime_context import RuntimeContex

shop_agent = ShopAgent()

print("Agent Initialized!")

with open("graph_output.png", "wb") as f:
    f.write(shop_agent._agent.get_graph().draw_mermaid_png())


user_input = """
    Costumer 1 20-05-2025
    Dolls 5 200 2500
    Cars 3 150 
    Books 10 50 500
    Toys 2 300 
    Books2 4 80 
    Socks 100 150.5
"""
inputs = {"messages": [HumanMessage(content=user_input)]}


config = {
    "configurable": {
        "thread_id": "1", 
       
    }
}

print(f"User: {user_input}")

# We use .stream() to see steps, or .invoke() for the final result
for event in shop_agent._agent.stream(inputs, config=config, context= RuntimeContex(db = shop_agent.client)):
    # 'event' is a dictionary like: {'node_name': {'messages': [...]}}
    for node_name, value in event.items():
        print(f"--- Step: {node_name} ---")
        
        if "messages" in value and value["messages"]:
            last_msg = value["messages"][-1]
            
            # Check if it's a Tool Call or a Final Answer
            if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
                print(f"🛠️ Calling Tool: {last_msg.tool_calls[0]['name']}")
            elif hasattr(last_msg, "content") and last_msg.content:
                print(f"💬 Content: {last_msg.content}")
                
        print("") 

