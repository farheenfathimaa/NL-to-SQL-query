import streamlit as st
import requests
import pandas as pd
import os
import json

# Page configuration
st.set_page_config(page_title="NL to SQL Assistant", layout="wide")

st.title("📊 NL → SQL Query Assistant")
st.markdown("""
Ask questions about your sales data in plain English. 
Example: *'Show me total sales by region for last quarter'* or *'Who is the top sales rep?'*
""")

# Backend configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")

# User input
question = st.text_input("Enter your question:", placeholder="e.g. List all products and their prices")

if st.button("Generate & Run Query"):
    if question:
        with st.spinner("Analyzing and querying database..."):
            try:
                response = requests.post(f"{BACKEND_URL}/query", json={"question": question})
                response.raise_for_status()
                data = response.json()
                
                if data["status"] == "success":
                    st.success("Query Executed Successfully!")
                    
                    col1, col2 = st.columns([1, 1])
                    
                    with col1:
                        st.subheader("Generated SQL")
                        st.code(data["query"], language="sql")
                        
                        st.subheader("Plain English Result")
                        st.write(data["explanation"])
                    
                    with col2:
                        st.subheader("Query Results")
                        try:
                            # Try to parse result into a dataframe if it's a list of tuples/dicts
                            # result usually comes as a string from langchain SQLDatabase.run
                            # We might need to handle formatting if it's a string
                            st.text(data["result"])
                        except Exception as e:
                            st.write(data["result"])
                            
                else:
                    st.error(f"Error: {data.get('error', 'Unknown error')}")
                    st.subheader("Generated SQL (Failed)")
                    st.code(data["query"], language="sql")
                    
            except Exception as e:
                st.error(f"Failed to connect to backend: {e}")
    else:
        st.warning("Please enter a question.")

st.sidebar.markdown("""
### About
This assistant uses:
- **FastAPI** for the backend
- **LangChain** for SQL generation
- **Gemini 1.5 Pro** as the LLM
- **PostgreSQL** for the data
- **Streamlit** for the UI
""")
