import streamlit as st
from langchain.llms import Ollama
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from agent import Ecommerce_agent
import json



if "products" not in st.session_state:
    st.session_state.products = Ecommerce_agent()  # Persist product data
# Define a strict prompt template
# Streamlit app
st.title("🛍️ E-commerce Search Assistant")

# Initialize session state to store history
if "history" not in st.session_state:
    st.session_state.history = []

query = st.text_input("Enter your search query:")

if query:
    response = st.session_state.products.run_search_chain(query=query)

    try:
        # Attempt to parse LLM response as JSON
        if '{' in str(response):  # Check if JSON-like
            #extract the json object from the response
            start_index = str(response).find('{')
            end_index = str(response).rfind('}')
            response = str(response)[start_index:end_index+1]
        search_params = json.loads(response)
        print(search_params)
        
        # Ensure the LLM extracted necessary details
        if search_params.get("product_type") and search_params.get("size"):
            # Call the agent to fetch product data
            search_results = st.session_state.products.handle_search_request(search_params)
            #pretty print the search results
            search_results = json.dumps(search_results, indent=4)
            answer_results = st.session_state.products.run_answer_chain(search_results,query)
            st.session_state.history.append({"query": query, "response": answer_results})
        else:
            st.session_state.history.append({"query": query, "response": "Missing required details. Please provide product type and size."})
    
    except json.JSONDecodeError:
        st.session_state.history.append({"query": query, "response": response})  # If not JSON, just display as is

# Display chat history in an always-expanded format
st.subheader("📜 Chat History")
for entry in reversed(st.session_state.history):  # Newest first
    with st.expander(f"**User:** {entry['query']}", expanded=True):
        st.markdown(f"**AI:** {entry['response']}")  # Bold formatting for clarity
