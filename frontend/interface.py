import streamlit as st
import sys
import os
import uuid

# --- PATH SETUP START ---
# Get the absolute path of the 'frontend' directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Get the 'backend' directory (sibling to frontend)
backend_dir = os.path.join(os.path.dirname(current_dir), 'backend')

# Add backend to sys.path so Python can find 'agent.py' and its dependencies
sys.path.append(backend_dir)
from agent import ShopAgent
from runtime_context import RuntimeContex

# 1. Page Configuration
st.set_page_config(page_title="Shop SQL Assistant", page_icon="🛒")
st.title("🛒 Shop Database Assistant")


@st.cache_resource
def get_shop_agent():
    return ShopAgent()

agent = get_shop_agent()

# 3. Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# 4. Display Existing Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if "thread_id" not in st.session_state:
    # If not, generate a random unique ID (e.g., "a1b2-c3d4-e5f6...")
    st.session_state.thread_id = str(uuid.uuid4())

with st.sidebar:
    st.header("Control Panel")
    
    # The Button
    if st.button("🗑️ Reset Conversation", type="primary"):
        # A. Clear local UI history
        st.session_state.messages = []
        
        # B. Generate a NEW thread_id
        # This effectively "disconnects" the agent from the previous memory
        st.session_state.thread_id = str(uuid.uuid4())
        
        # C. Refresh the app to show the empty chat
        st.rerun()
    
    st.write(f"**Current Session ID:**")
    st.caption(f"`{st.session_state.thread_id}`")

# 5. Handle User Input
if prompt := st.chat_input("Ask about products, stock, or sales..."):
    
    # A. Display User Message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # B. Generate & Display Assistant Response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        events = agent._agent.stream(
            {"messages": prompt},
            {"configurable": {"thread_id": st.session_state.thread_id}},
            stream_mode="values",
            context=RuntimeContex(db=agent.client)
        )

        # Iterate through the graph updates
        for event in events:
           
            if "messages" in event and len(event["messages"]) > 0:
                last_message = event["messages"][-1]
                raw_content = last_message.content
                if isinstance(raw_content, list):
                    # Extract only the 'text' values from the list items
                    full_response = "".join(
                        [block["text"] for block in raw_content if isinstance(block, dict) and "text" in block]
                    )
                else:
                    full_response = raw_content
        
        # Final display
        message_placeholder.markdown(full_response)
    
    st.session_state.messages.append({"role": "assistant", "content": full_response})