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
if "selected_model" not in st.session_state:
    st.session_state.selected_model = "ollama:deepseek-r1:1.5b"

# Sidebar for configuration and file upload
with st.sidebar:
    st.header("⚙️ Configuration")

    # Settings button link
    st.link_button("🔧 Settings", "http://localhost:8501/settings", use_container_width=True)

    st.divider()

    # Server connection status
    try:
        response = requests.get(f"{SERVER_BASE_URL}/ollama", params={"query": "test"}, timeout=2)
        st.success("✅ Server Connected")
    except:
        st.error("❌ Server Disconnected")
        st.warning("Make sure the server is running on http://localhost:5001")

    st.divider()

    # Get available models from server
    try:
        models_response = requests.get(f"{SERVER_BASE_URL}/models", timeout=5)
        if models_response.status_code == 200:
            models_data = models_response.json()
        else:
            models_data = {"providers": {}}
    except:
        models_data = {"providers": {}}

    # Model selection dropdown
    st.header("🤖 Model Selection")

    model_options = []
    model_display_names = {}

    for provider, info in models_data.get("providers", {}).items():
        status = "✅" if info.get("available") else "❌"
        for model in info.get("models", []):
            display_name = f"{status} {provider}: {model}"
            model_value = f"{provider}:{model}"
            model_options.append(model_value)
            model_display_names[model_value] = display_name

    if model_options:
        selected_model_value = st.selectbox(
            "Select Model",
            options=model_options,
            format_func=lambda x: model_display_names.get(x, x),
            index=0
        )
        st.session_state.selected_model = selected_model_value
    else:
        st.warning("No models available. Configure settings.")
        st.session_state.selected_model = "ollama:deepseek-r1:1.5b"

    # Display selected model
    st.info(f"Using: {st.session_state.selected_model}")

    st.divider()
    st.header("📁 File Management")

    # Get available collections
    try:
        collections_response = requests.get(f"{SERVER_BASE_URL}/collections", timeout=5)
        if collections_response.status_code == 200:
            collections = collections_response.json()
        else:
            collections = []
    except:
        collections = []

    # Collection selection dropdown
    selected_collection = st.selectbox(
        "Select collection to upload into",
        options=collections if collections else ["default"],
        index=0
    )

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
                        f"{SERVER_BASE_URL}/upload",
                        files=files,
                        params={"collection": selected_collection},
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
                    f"{SERVER_BASE_URL}/rag",
                    params={
                        "query": prompt,
                        "collection_name": selected_collection,
                        "model": st.session_state.selected_model
                    },
                    timeout=120
                )

                if response.status_code == 200:
                    answer = response.json().get("response", response.text)
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
    <p>RAG Project v2.0 | Hybrid LLM Support (Ollama, Claude, ChatGPT, Gemini)</p>
</div>
""", unsafe_allow_html=True)

