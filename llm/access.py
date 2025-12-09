

import ollama


EMBEDDING_MODEL_NAME = "nomic-embed-text"

CHATTING_MODEL_NAME = "deepseek-r1:1.5b"

def llm_embedding(_text: str):
    return ollama.embeddings(model=EMBEDDING_MODEL_NAME, prompt=_text).embedding

def llm_chat(prompt, messages=None, model=CHATTING_MODEL_NAME):
    """
    Sends a prompt to the Ollama chat model and maintains conversation history.
    """
    if messages is None:
        messages = []

    messages.append({"role": "user", "content": prompt})

    # Call the Ollama chat API
    response_data = ollama.chat(
        model=model,
        messages=messages,
    )
    
    # Extract the response content
    response = response_data['message']['content']

    messages.append({"role": "assistant", "content": response})

    return response, messages