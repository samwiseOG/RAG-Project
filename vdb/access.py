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


def upsert_point(coll_name, path, cNum, embedding_list, content):
    client.upsert(
    collection_name=coll_name,
    wait=True,
    points=[
        PointStruct(
            id=str(uuid.uuid4()), 
                    vector=embedding_list, payload={"path": path, "content": content, "chunk_number": cNum})
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