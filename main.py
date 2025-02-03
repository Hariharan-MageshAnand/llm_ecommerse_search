import streamlit as st
from agent import Ecommerce_agent
import json



if "products" not in st.session_state:
    st.session_state.products = Ecommerce_agent()  # Persist product data
# Streamlit app
st.title("🛍️ Personal E-commerce Search Assistant")

# Initialize session state to store history
if "history" not in st.session_state:
    st.session_state.history = []

query = st.text_input("Enter your search query:")

if query:
    response = st.session_state.products.run_search_chain(query=query) # initiating first agent to search product in flipkart
    response = str(response).replace("'",'"')
    response=response.replace("Action:","")
    try:
        
        search_params = json.loads(response)
        search_params = search_params["action_input"]
        
        # Ensure the LLM extracted necessary details
        if search_params.get("product_type"):
            # Call the agent to fetch product data
            search_results = st.session_state.products.handle_search(search_params) # calling handle search tool and passing the json created by the agent
            st.session_state.products.add_data(search_results)
            search_results = json.dumps(search_results, indent=4)
            final_results = st.session_state.products.run_tool_chain(query) # running tool agent to find what type of query is it 
            st.session_state.history.append({"query": query, "response": final_results})
        else:
            st.session_state.history.append({"query": query, "response": "Missing required details. Please provide product type"}) # return this error in chat if product type is not mentioned
    
    except Exception as e:
        print(e)
        st.session_state.history.append({"query": query, "response": response})  # If not JSON, just display as is
    print("complete")

# Display chat history in an always-expanded format
st.subheader("📜 Chat History")
for entry in reversed(st.session_state.history):  # Newest first
    with st.expander(f"**User:** {entry['query']}", expanded=True):
        st.markdown(f"**AI:** {entry['response']}")  # Bold formatting for clarity
