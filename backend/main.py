from agent import ShopAgent
from runtime_context import RuntimeContex

agent = ShopAgent()

question = "NA"
while question != "exit":
    question = input("Enter your prompt: ")
    for step in agent._agent.stream(
        {"messages": question},
        stream_mode="values",
        context=RuntimeContex(db = agent.client)
        ):
        step["messages"][-1].pretty_print()