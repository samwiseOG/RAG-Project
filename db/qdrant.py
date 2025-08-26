from qdrant_client import QdrantClient
import ollama

client = QdrantClient(url="http://localhost:6333")

from qdrant_client.models import Distance, VectorParams

# client.create_collection(
#     collection_name="test_collection",
#     vectors_config=VectorParams(size=768, distance=Distance.DOT),
# )

# from qdrant_client.models import PointStruct

# sky_embedding = ollama.embeddings(model='nomic-embed-text', prompt='The sky is blue because of rayleigh scattering')


# operation_info = client.upsert(
#     collection_name="test_collection",
#     wait=True,
#     points=[
#         PointStruct(id=1, vector=sky_embedding.embedding, payload={"path": "../sops/projecta/sop1.docx", "page": 2})
#     ],
# )

# ground_embedding = ollama.embeddings(model='nomic-embed-text', prompt='The ground is blue because of something else')

# operation_info = client.upsert(
#     collection_name="test_collection",
#     wait=True,
#     points=[
#         PointStruct(id=2, vector=ground_embedding.embedding, payload={"path": "../sops/projecta/sop2.docx", "page": 3})
#     ],
# )


# print(operation_info)

query_embedded = ollama.embeddings(model='nomic-embed-text', prompt='abstract')

print(query_embedded)

search_result = client.query_points(
    collection_name="test_collection",
    query=query_embedded.embedding,
    with_payload=True,
    limit=3
).points

print(search_result)
