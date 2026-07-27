import streamlit as st
import requests
from llm.secrets_manager import get_secrets_manager
from llm.providers import PROVIDERS, MODEL_REGISTRY
from llm.config import get_config

st.set_page_config(
    page_title="Settings",
    page_icon="⚙️",
)

st.title("⚙️ Settings")

secrets_manager = get_secrets_manager()
config = get_config()

# Tabs for each provider
tab_ollama, tab_claude, tab_openai, tab_gemini = st.tabs(
    ["🏠 Ollama", "🧠 Claude", "🔓 OpenAI", "✨ Gemini"]
)

# OLLAMA TAB
with tab_ollama:
    st.header("Ollama Settings")
    st.markdown("Local AI models - no API key required")

    # Ollama host configuration
    current_host = config.get_ollama_host()
    ollama_host = st.text_input(
        "Ollama Host Address",
        value=current_host,
        help="Default: localhost:11434"
    )

    if st.button("🔗 Test Ollama Connection", key="test_ollama"):
        try:
            import requests
            response = requests.get(f"http://{ollama_host}/api/tags", timeout=2)
            if response.status_code == 200:
                st.success("✅ Connected to Ollama!")
                available_models = response.json().get("models", [])
                if available_models:
                    st.info(f"Available models: {len(available_models)}")
                    for model in available_models[:5]:
                        st.text(f"  • {model.get('name', model)}")
            else:
                st.error(f"❌ Connection failed: {response.status_code}")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

    st.divider()
    st.subheader("Model Selection")

    default_model = secrets_manager.get_default_models().get("ollama", "deepseek-r1:1.5b")
    selected_model = st.selectbox(
        "Select Ollama LLM Model",
        options=MODEL_REGISTRY.get("ollama", []),
        index=(MODEL_REGISTRY.get("ollama", []).index(default_model) if default_model in MODEL_REGISTRY.get("ollama", []) else 0),
        key="ollama_model_select"
    )

    if st.button("💾 Save Ollama Model", key="save_ollama_model"):
        secrets_manager.set_default_model("ollama", selected_model)
        st.success(f"✅ Saved: {selected_model}")

# CLAUDE TAB
with tab_claude:
    st.header("Claude (Anthropic) Settings")
    st.markdown("Connect to Claude models via Anthropic API")

    # Check if API key is already set
    existing_key = config.get_api_key("claude")
    is_configured = bool(existing_key)

    if is_configured:
        st.success("✅ API key configured")

    # API Key input (masked)
    api_key = st.text_input(
        "Anthropic API Key",
        type="password",
        value="" if not is_configured else "sk-ant-••••••••",
        help="Get your key from https://console.anthropic.com"
    )

    if st.button("🔗 Test Claude Connection", key="test_claude"):
        test_key = api_key if api_key and not api_key.startswith("sk-ant-••") else existing_key
        if test_key:
            try:
                from langchain_anthropic import ChatAnthropic
                llm = ChatAnthropic(model="claude-3-5-sonnet-20241022", api_key=test_key)
                response = llm.invoke("Say 'Hello' in one word.")
                st.success("✅ Connected to Claude!")
                st.info(f"Response: {response.content}")
            except Exception as e:
                st.error(f"❌ Connection failed: {str(e)}")
        else:
            st.warning("Please enter an API key first")

    st.divider()
    st.subheader("API Key Management")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("💾 Save API Key", key="save_claude_key"):
            if api_key and not api_key.startswith("sk-ant-••"):
                secrets_manager.set_credential("claude", api_key)
                st.success("✅ API key saved!")
            elif is_configured:
                st.info("API key already configured")
            else:
                st.warning("Please enter a valid API key")

    with col2:
        if st.button("🗑️ Clear API Key", key="clear_claude_key"):
            if is_configured:
                secrets_manager.clear_credential("claude")
                st.success("✅ API key cleared")
            else:
                st.info("No API key configured")

    st.divider()
    st.subheader("Model Selection")

    default_model = secrets_manager.get_default_models().get("claude", "claude-3-5-sonnet-20241022")
    selected_model = st.selectbox(
        "Select Claude Model",
        options=MODEL_REGISTRY.get("claude", []),
        index=(MODEL_REGISTRY.get("claude", []).index(default_model) if default_model in MODEL_REGISTRY.get("claude", []) else 0),
        key="claude_model_select"
    )

    if st.button("💾 Save Claude Model", key="save_claude_model"):
        secrets_manager.set_default_model("claude", selected_model)
        st.success(f"✅ Saved: {selected_model}")

# OPENAI TAB
with tab_openai:
    st.header("OpenAI Settings")
    st.markdown("Connect to ChatGPT models via OpenAI API")

    existing_key = config.get_api_key("openai")
    is_configured = bool(existing_key)

    if is_configured:
        st.success("✅ API key configured")

    api_key = st.text_input(
        "OpenAI API Key",
        type="password",
        value="" if not is_configured else "sk-••••••••",
        help="Get your key from https://platform.openai.com"
    )

    if st.button("🔗 Test OpenAI Connection", key="test_openai"):
        test_key = api_key if api_key and not api_key.startswith("sk-••") else existing_key
        if test_key:
            try:
                from langchain_openai import ChatOpenAI
                llm = ChatOpenAI(model="gpt-3.5-turbo", api_key=test_key)
                response = llm.invoke("Say 'Hello' in one word.")
                st.success("✅ Connected to OpenAI!")
                st.info(f"Response: {response.content}")
            except Exception as e:
                st.error(f"❌ Connection failed: {str(e)}")
        else:
            st.warning("Please enter an API key first")

    st.divider()
    st.subheader("API Key Management")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("💾 Save API Key", key="save_openai_key"):
            if api_key and not api_key.startswith("sk-••"):
                secrets_manager.set_credential("openai", api_key)
                st.success("✅ API key saved!")
            elif is_configured:
                st.info("API key already configured")
            else:
                st.warning("Please enter a valid API key")

    with col2:
        if st.button("🗑️ Clear API Key", key="clear_openai_key"):
            if is_configured:
                secrets_manager.clear_credential("openai")
                st.success("✅ API key cleared")
            else:
                st.info("No API key configured")

    st.divider()
    st.subheader("Model Selection")

    default_model = secrets_manager.get_default_models().get("openai", "gpt-4o")
    selected_model = st.selectbox(
        "Select OpenAI Model",
        options=MODEL_REGISTRY.get("openai", []),
        index=(MODEL_REGISTRY.get("openai", []).index(default_model) if default_model in MODEL_REGISTRY.get("openai", []) else 0),
        key="openai_model_select"
    )

    if st.button("💾 Save OpenAI Model", key="save_openai_model"):
        secrets_manager.set_default_model("openai", selected_model)
        st.success(f"✅ Saved: {selected_model}")

# GEMINI TAB
with tab_gemini:
    st.header("Google Gemini Settings")
    st.markdown("Connect to Gemini models via Google AI API")

    existing_key = config.get_api_key("gemini")
    is_configured = bool(existing_key)

    if is_configured:
        st.success("✅ API key configured")

    api_key = st.text_input(
        "Google API Key",
        type="password",
        value="" if not is_configured else "AIzaSy••••••••",
        help="Get your key from https://aistudio.google.com"
    )

    if st.button("🔗 Test Gemini Connection", key="test_gemini"):
        test_key = api_key if api_key and not api_key.startswith("AIzaSy••") else existing_key
        if test_key:
            try:
                from langchain_google_genai import ChatGoogleGenerativeAI
                llm = ChatGoogleGenerativeAI(model="gemini-pro", api_key=test_key)
                response = llm.invoke("Say 'Hello' in one word.")
                st.success("✅ Connected to Gemini!")
                st.info(f"Response: {response.content}")
            except Exception as e:
                st.error(f"❌ Connection failed: {str(e)}")
        else:
            st.warning("Please enter an API key first")

    st.divider()
    st.subheader("API Key Management")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("💾 Save API Key", key="save_gemini_key"):
            if api_key and not api_key.startswith("AIzaSy••"):
                secrets_manager.set_credential("gemini", api_key)
                st.success("✅ API key saved!")
            elif is_configured:
                st.info("API key already configured")
            else:
                st.warning("Please enter a valid API key")

    with col2:
        if st.button("🗑️ Clear API Key", key="clear_gemini_key"):
            if is_configured:
                secrets_manager.clear_credential("gemini")
                st.success("✅ API key cleared")
            else:
                st.info("No API key configured")

    st.divider()
    st.subheader("Model Selection")

    default_model = secrets_manager.get_default_models().get("gemini", "gemini-2.0-flash")
    selected_model = st.selectbox(
        "Select Gemini Model",
        options=MODEL_REGISTRY.get("gemini", []),
        index=(MODEL_REGISTRY.get("gemini", []).index(default_model) if default_model in MODEL_REGISTRY.get("gemini", []) else 0),
        key="gemini_model_select"
    )

    if st.button("💾 Save Gemini Model", key="save_gemini_model"):
        secrets_manager.set_default_model("gemini", selected_model)
        st.success(f"✅ Saved: {selected_model}")
