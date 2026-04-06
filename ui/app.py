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

# Check if this is first-time user (no collections)
try:
    collections_response = requests.get(f"{SERVER_BASE_URL}/collections", timeout=5)
    if collections_response.status_code == 200:
        available_collections = collections_response.json().get("collections", [])
    else:
        available_collections = []
except:
    available_collections = []

# Initialize session state for conversation history
if "messages" not in st.session_state:
    st.session_state.messages = []

if "selected_collection" not in st.session_state:
    # Set default to first collection if available, otherwise None
    if available_collections:
        st.session_state.selected_collection = available_collections[0]
    else:
        st.session_state.selected_collection = None

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
    st.header("🗂️ Collection Management")
    
    # Fetch available collections
    try:
        collections_response = requests.get(f"{SERVER_BASE_URL}/collections", timeout=5)
        if collections_response.status_code == 200:
            available_collections = collections_response.json().get("collections", [])
        else:
            available_collections = []
    except:
        available_collections = []

    
    # Collection dropdown
    selected_collection = st.selectbox(
        "Select Collection:",
        available_collections,
        index=available_collections.index(st.session_state.selected_collection) if st.session_state.selected_collection in available_collections else 0,
        key="collection_selector"
    )
    st.session_state.selected_collection = selected_collection
    
    # Create new collection (hidden by default)
    with st.expander("➕ Create New Collection"):
        new_collection_name = st.text_input(
            "Collection Name:",
            placeholder="e.g., research_papers",
            key="new_collection_name"
        )
        if st.button("Create Collection", use_container_width=True, key="create_collection_btn"):
            if new_collection_name:
                with st.spinner("Creating collection..."):
                    try:
                        response = requests.post(
                            f"{SERVER_BASE_URL}/collections",
                            json={"name": new_collection_name},
                            timeout=10
                        )
                        if response.status_code == 201:
                            st.session_state.selected_collection = new_collection_name
                            st.success(f"✅ Collection created!")
                            st.rerun()
                        else:
                            error_msg = response.json().get("error", "Failed to create collection")
                            st.error(f"❌ Error: {error_msg}")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
            else:
                st.warning("Please enter a collection name")
    
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
                    data = {"collection": st.session_state.selected_collection}
                    response = requests.post(
                        f"{SERVER_BASE_URL}/embed",
                        files=files,
                        data=data,
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

# Check if collections exist and show appropriate UI
if not available_collections:
    st.warning("⚠️ No collections found. Please create a collection in the sidebar to get started.")
else:
    # User input (only enabled if collections exist)
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
                        params={"query": prompt, "collection": st.session_state.selected_collection},
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
