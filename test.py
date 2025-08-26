print("Hello world")

import ollama
sky_embedding = ollama.embeddings(model='nomic-embed-text', prompt='The sky is blue because of rayleigh scattering')
print(len(sky_embedding.embedding))
print(sky_embeddin)