print("Hello world")

import ollama
print(ollama.embeddings(model='nomic-embed-text', prompt='The sky is blue because of rayleigh scattering'))