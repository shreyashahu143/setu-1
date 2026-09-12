import streamlit as st
import time
from dotenv import load_dotenv

# Load all core logic
load_dotenv()
from src.graph import app as agent_graph

# 1. UI Page Configuration
st.set_page_config(
    page_title="Setu | Newcomer Street Guide",
    page_icon="📍",
    layout="centered"
)

# Title and App Header
st.title("📍 Setu (सेतू)")
st.subheader("Your Local Street-Smart Best Friend in Nagpur")
st.markdown(
    "Helping interstate migrants decode unwritten market lanes, "
    "local Varhadi / Nagpuri lingo, and street negotiation tactics."
)
st.write("---")

# 2. Sidebar Configuration for User Context
st.sidebar.header("🛠️ Newcomer Context")
origin_state = st.sidebar.selectbox(
    "Where are you moving from?",
    ["Telangana", "Kerala", "Tamil Nadu", "Andhra Pradesh", "Karnataka", "Other"]
)

st.sidebar.markdown("""
### 💡 How to Test:
1. **Seed Hits (Instant):**
   * *'Where can I repair my phone display in Sitabuldi?'*
   * *'How do I tell an auto driver to charge by meter?'*
2. **Harvest Misses (Live Scrape):**
   * *'Where to buy wholesale ceramic pots in Nagpur?'*
   * *'Where to buy cheap secondhand laptops?'*
""")

# 3. Main Chat Interface Logic
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages in the session
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Accept user input query
if user_query := st.chat_input("Ask about shopping lanes, local slang, or street prices..."):
    
    # Render user query block immediately
    with st.chat_message("user"):
        st.markdown(user_query)
    st.session_state.messages.append({"role": "user", "content": user_query})
    
    # Process graph logic with an interactive live status engine
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        
        # Using st.status to show the agent's actual chain of thought
        with st.status("🧠 Activating Setu Orchestrator...", expanded=True) as status:
            
            # Step A: Intent Routing
            status.update(label="🔍 Classifying user query intent...")
            time.sleep(0.3)  # Small visual buffer for the user
            
            # Construct execution payload for LangGraph workflow
            initial_state = {
                "raw_query": user_query,
                "user_origin": origin_state
            }
            
            # Fire graph execution
            graph_output = agent_graph.invoke(initial_state)
            
            intent = graph_output.get("intent", "SCOUT")
            cache_status = graph_output.get("cache_status", "HIT")
            
            status.update(label=f"🎯 Intent Route Tagged: {intent}")
            
            # Step B: Data Discovery / Retrieval Step
            if intent in ["SCOUT", "HYBRID"]:
                status.update(label="📍 Processing hyper-local database search...")
                if cache_status == "CACHE_MISS":
                    status.update(label="🌐 Cache Miss! Launching deep harvester web search loop...")
                    # The harvester node is automatically running deep scrapers across text blobs
                else:
                    status.update(label="⚡ Database Hit! Extracting verified lane metadata...")
                    
            if intent in ["LINGO", "HYBRID"]:
                status.update(label="🗣️ Invoking local dialect & culture bridge agent...")
                
            # Step C: Final Response Synthesis
            status.update(label="📝 Storing nodes and synthesizing response card...", state="complete")
        
        # Render the formatted multi-agent payload card into the main chat window
        final_payload = graph_output.get("final_payload", "We couldn't compile a local street guide for this query.")
        st.markdown(final_payload)
        
        # Store response in session memory to persist across renders
        st.session_state.messages.append({"role": "assistant", "content": final_payload})
