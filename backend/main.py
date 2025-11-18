from agent import ShopAgent
from runtime_context import RuntimeContex
question = "Per produktin Kukulla modifiko sasine me 10."
agent = ShopAgent()

for step in agent._agent.stream(
    {"messages": question},
    stream_mode="values",
    context=RuntimeContex(db = agent.client)
):
    step["messages"][-1].pretty_print()