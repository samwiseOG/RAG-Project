import uuid
from qdrant_client import QdrantClient
import ollama
from qdrant_client.models import PointStruct, Filter, FieldCondition, MatchValue


client = QdrantClient(url="http://localhost:6333")

from qdrant_client.models import Distance, VectorParams

def create_collection(path:str):
    folder_name = path.split('/')[-2]
    if not client.collection_exists(folder_name):
        client.create_collection(
        collection_name=folder_name,
        vectors_config=VectorParams(size=768, distance=Distance.DOT),
    )
    return folder_name


def upsert_point(coll_name, path, cNum, ollama_embedding_return, content):
    client.upsert(
    collection_name=coll_name,
    wait=True,
    points=[
        PointStruct(
            id=str(uuid.uuid4()), 
                    vector=ollama_embedding_return.embedding, payload={"path": path, "content": content, "chunk_number": cNum})
    ],
)
    
def search(coll_name:str, query_embedding: list, file_path: str= None):
    f = None
    if file_path:
        f = Filter(
            must=[
                FieldCondition(
                    key="path",
                    match=MatchValue(value=file_path)
                )
            ]
        )
    return client.query_points(
        collection_name=coll_name,
        query=query_embedding,
        query_filter= f,
        with_payload=True,
        limit=10
    ).points

# test_query = ollama.embeddings(model='nomic-embed-text', prompt='war in pacific').embedding
#print(test_query)
# print(search(coll_name="RAG-Project", query_embedding=test_query, file_path="/home/sam/Documents/Projects/RAG/RAG-Project/app/tmp/WWII-Brief-timeline-06242022.pdf"))
#print(search(coll_name="RAG-Project", query_embedding=test_query))
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

# query_embedded = ollama.embeddings(model='nomic-embed-text', prompt='abstract')

# print(query_embedded)

# search_result = client.query_points(
#     collection_name="test_collection",
#     query=query_embedded.embedding,
#     with_payload=True,
#     limit=3
# ).points

# print(search_result)
