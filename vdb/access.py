import uuid
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, Filter, FieldCondition, MatchValue
from langchain_core.documents import Document
from llm.access import get_embedding_function


# client = QdrantClient(url="http://localhost:6333")
client = QdrantClient(":memory:")

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
    
def add_documents(coll_name:str, documents: list):
    vector_store = QdrantVectorStore(
        client=client,
        collection_name=coll_name,
        embedding=get_embedding_function()
    )
    vector_store.add_documents(documents)

def calculate_chunk_ids(chunks):

    # This will create IDs like "data/monopoly.pdf:6:2"
    # Page Source : Page Number : Chunk Index

    last_page_id = None
    current_chunk_index = 0

    for chunk in chunks:
        source = chunk.metadata.get("source")
        page = chunk.metadata.get("page")
        current_page_id = f"{source}:{page}"

        # If the page ID is the same as the last one, increment the index.
        if current_page_id == last_page_id:
            current_chunk_index += 1
        else:
            current_chunk_index = 0

        # Calculate the chunk ID.
        chunk_id = f"{current_page_id}:{current_chunk_index}"
        last_page_id = current_page_id

        # Add it to the page meta-data.
        chunk.metadata["id"] = chunk_id

    return chunks

def add_to_qdrant(chunks: list[Document], coll_name: str):
    # Load the existing database.
    db = QdrantVectorStore(
        client=client,
        collection_name=coll_name,
        embedding=get_embedding_function()
    )

    # Calculate Page IDs.
    chunks_with_ids = calculate_chunk_ids(chunks)

    # Add or Update the documents.
    existing_items = db.get(include=[])  # IDs are always included by default
    existing_ids = set(existing_items["ids"])
    print(f"Number of existing documents in DB: {len(existing_ids)}")

    # Only add documents that don't exist in the DB.
    new_chunks = []
    for chunk in chunks_with_ids:
        if chunk.metadata["id"] not in existing_ids:
            new_chunks.append(chunk)

    if len(new_chunks):
        print(f"👉 Adding new documents: {len(new_chunks)}")
        new_chunk_ids = [chunk.metadata["id"] for chunk in new_chunks]
        db.add_documents(new_chunks, ids=new_chunk_ids)
        db.persist()
    else:
        print("✅ No new documents to add")

    
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