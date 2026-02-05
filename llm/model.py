import ollama

class embedder:
    def __init__(
        self,
        model = "nomic-embed-text"
    ):

        ollama.pull(model, stream=True)
        self.model = model

    def create_embedding(self,_text: str):
        return ollama.embeddings(model=self.model, prompt=_text).embedding

class llm_class:
    def __init__(
        self,
        model = "deepseek-r1:1.5b"
    ):
        ollama.pull(model, stream=True)
        self.messages = []
        self.model = model

    def generate(self, prompt):
        self.messages.append({"role": "user", "content": prompt})

        # Ensure the model is available locally
        #if _ensure_ollama_model(self.model):
            # Call the Ollama chat API
        response_data = ollama.chat(
            model=self.model,
            messages=self.messages,
        )
        #else:
        #   return "Error: Unable to access the specified model."
        
        # Extract the response content
        response = response_data['message']['content']

        self.messages.append({"role": "assistant", "content": response})

        return response
    
    def clear_context(self):
        self.messages = []
        return "Context cleared."