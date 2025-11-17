from agent import ShopAgent
from runtime_context import RuntimeContex
question = "Sa Kukulla kemi ne dyqan?"
agent = ShopAgent()

for step in agent._agent.stream(
    {"messages": question},
    stream_mode="values",
    context=RuntimeContex(db = agent.client)
):
    step["messages"][-1].pretty_print()