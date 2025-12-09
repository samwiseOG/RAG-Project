import streamlit as st
import requests
import pandas as pd
from pathlib import Path
import time

# Configuration
SERVER_BASE_URL = "http://localhost:5001"

st.set_page_config(
    page_title="RAG Project",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🔍 RAG Query Interface")
st.markdown("*Ask questions and get intelligent responses from your knowledge base*")

# Initialize session state for conversation history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar for configuration and file upload
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Server connection status
    try:
        response = requests.get(f"{SERVER_BASE_URL}/ollama", params={"query": "test"}, timeout=2)
        st.success("✅ Server Connected")
    except:
        st.error("❌ Server Disconnected")
        st.warning("Make sure the server is running on http://localhost:5001")
    
    st.divider()
    st.header("📁 File Management")
    
    uploaded_file = st.file_uploader(
        "Upload a PDF file to add to knowledge base",
        type=["pdf"]
    )
    
    if uploaded_file is not None:
        if st.button("📤 Upload & Embed", use_container_width=True):
            with st.spinner("Processing file..."):
                try:
                    files = {"document": (uploaded_file.name, uploaded_file, "application/pdf")}
                    response = requests.post(
                        f"{SERVER_BASE_URL}/embed",
                        files=files,
                        timeout=60
                    )
                    
                    if response.status_code == 201:
                        st.success("✅ File uploaded and embedded successfully!")
                        st.session_state.messages = []  # Clear conversation
                    else:
                        st.error(f"❌ Upload failed: {response.text}")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    
    st.divider()
    
    if st.button("🗑️ Clear History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# Main chat interface
st.subheader("Chat with Your Knowledge Base")

# Display conversation history
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar="🤖" if message["role"] == "assistant" else "👤"):
        st.markdown(message["content"])

# User input
if prompt := st.chat_input("Ask a question..."):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)
    
    # Get response from server
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Thinking..."):
            try:
                response = requests.get(
                    f"{SERVER_BASE_URL}/ollama",
                    params={"query": prompt},
                    timeout=120
                )
                
                if response.status_code == 200:
                    answer = response.text
                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                else:
                    error_msg = f"Error: {response.status_code} - {response.text}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
            except requests.exceptions.Timeout:
                timeout_msg = "⏱️ Request timed out. The server took too long to respond. Please try again."
                st.warning(timeout_msg)
                st.session_state.messages.append({"role": "assistant", "content": timeout_msg})
            except Exception as e:
                error_msg = f"❌ Connection error: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #888; font-size: 0.8em;'>
    <p>RAG Project v1.0 | Powered by Ollama & Vector DB</p>
</div>
""", unsafe_allow_html=True)
