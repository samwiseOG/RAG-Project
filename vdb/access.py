import uuid
import os
import logging
from dotenv import load_dotenv
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, Filter, FieldCondition, MatchValue
from langchain_core.documents import Document
from llm.model import embedder
from langchain_core.embeddings import Embeddings
from qdrant_client.models import Distance, VectorParams

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

QDRANT_URL = os.getenv('QDRANT_URL', 'http://localhost:6333')
VECTOR_SIZE = int(os.getenv('VECTOR_SIZE', '768'))
DISTANCE_METRIC = os.getenv('DISTANCE_METRIC', 'DOT')

# Initialize client using QDRANT_URL from .env
client = QdrantClient(url=QDRANT_URL)

def create_collection(co):
    folder_name = path.split('/')[-2]
    if not client.collection_exists(folder_name):
        try:
            client.create_collection(
                collection_name=folder_name,
                vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance[DISTANCE_METRIC]),
            )
            logger.info(f"✅ Created collection '{folder_name}' with size={VECTOR_SIZE}, distance={DISTANCE_METRIC}")
        except Exception as e:
            logger.error(f"❌ Failed to create collection '{folder_name}': {e}")
            raise
    else:
        logger.info(f"ℹ️ Collection '{folder_name}' already exists")
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

def get_distance_strategy(coll_name: str) -> str:
    """Retrieve the distance strategy from an existing Qdrant collection."""
    collection_info = client.get_collection(coll_name)
    distance = collection_info.config.params.vectors.distance
    logger.info(f"Distance strategy for collection '{coll_name}': {distance}")
    
    # Map Qdrant Distance enum to LangChain strategy string
    distance_map = {
        "Cosine": "COSINE",
        "Euclid": "EUCLIDEAN",
        "Dot": "DOT",
        "Manhattan": "MANHATTAN"
    }
    
    return distance_map.get(str(distance))

def add_to_qdrant(chunks: list[Document], coll_name: str):
    # Load the existing database.
    embedding_instance = embedder()
    
    # Get distance strategy from collection


    if not client.collection_exists(coll_name):
        try:
            client.create_collection(
                collection_name=coll_name,
                vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance[DISTANCE_METRIC]),
            )
            logger.info(f"✅ Created collection '{coll_name}' with size={VECTOR_SIZE}, distance={DISTANCE_METRIC}")
        except Exception as e:
            logger.error(f"❌ Failed to create collection '{coll_name}': {e}")
            raise

    distance_strategy = get_distance_strategy(coll_name)
    logger.info(f"Using distance strategy: {distance_strategy}")
    
    
    db = QdrantVectorStore(
        client=client,
        collection_name=coll_name,
        embedding=embedding_instance,
    )

    # Calculate Page IDs.
    chunks_with_ids = calculate_chunk_ids(chunks)

    # Add or Update the documents.
    try:
        collection_info = client.get_collection(coll_name)
        existing_ids = set()
        # Get all point IDs from the collection
        if collection_info.points_count > 0:
            points = client.scroll(collection_name=coll_name, limit=collection_info.points_count)[0]
            existing_ids = set(point.id for point in points)
    except Exception as e:
        logger.warning(f"Could not retrieve existing items: {e}. Proceeding with empty set.")
        existing_ids = set()
    
    logger.info(f"Number of existing documents in DB: {len(existing_ids)}")

    # Only add documents that don't exist in the DB.
    new_chunks = []
    for chunk in chunks_with_ids:
        if chunk.metadata["id"] not in existing_ids:
            new_chunks.append(chunk)

    if len(new_chunks):
        logger.info(f"👉 Adding new documents: {len(new_chunks)}")
        # Generate UUID for each chunk and store string ID in metadata
        new_chunk_ids = [str(uuid.uuid4()) for _ in new_chunks]
        for chunk, chunk_id in zip(new_chunks, new_chunk_ids):
            chunk.metadata["chunk_id"] = chunk.metadata["id"]  # Store original ID
        db.add_documents(new_chunks, ids=new_chunk_ids)
    else:
        logger.info("✅ No new documents to add")
    
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