from vdb.util import chunk_text
from vdb.access import client
from qdrant_client.models import Filter, FieldCondition, MatchValue, VectorParams, Distance, PointStruct
from llm.access import llm_embedding
import uuid

def cross_fold(text: str, params_list: list, path: str):
    """
    Cross validate different parameter effects on chunking method.
    
    For each set of parameters in params_list, chunk the text, and store the new chunks
    in the collection 'RAG_Project_Test' with chunk_size and overlap in payload.
    
    Args:
        text: The input text to chunk.
        params_list: List of dicts with 'chunk_size' and 'overlap' keys.
        path: The file path for metadata.
    """
    coll_name = "RAG_Project_Test"
    
    # Create collection if not exists
    if not client.collection_exists(coll_name):
        client.create_collection(
            collection_name=coll_name,
            vectors_config=VectorParams(size=768, distance=Distance.DOT),
        )
    
    for params in params_list:
        # Chunk with new params
        chunks = chunk_text(text, chunk_size=params['chunk_size'], overlap=params['overlap'])
        
        # Store chunks
        for ind, c in enumerate(chunks):
            if c and len(c.strip()) > 0:
                embedding = llm_embedding(c)
                client.upsert(
                    collection_name=coll_name,
                    wait=True,
                    points=[
                        PointStruct(
                            id=str(uuid.uuid4()), 
                            vector=embedding, 
                            payload={"path": path, "content": c, "chunk_number": ind, "chunk_size": params['chunk_size'], "overlap": params['overlap']}
                        )
                    ],
                )
        
        print(f"Tested params: chunk_size={params['chunk_size']}, overlap={params['overlap']}, chunks: {len(chunks)}")


if __name__ == "__main__":
    sample_file = '' # TODO: find dataset
    
    test_params = [
        {'chunk_size': 50, 'overlap': 1},
        {'chunk_size': 100, 'overlap': 1},
        {'chunk_size': 150, 'overlap': 1},        
        {'chunk_size': 50, 'overlap': 2},
        {'chunk_size': 100, 'overlap': 2},
        {'chunk_size': 150, 'overlap': 2},
    ]
    
    cross_fold(sample_file, test_params, path="sample.txt")