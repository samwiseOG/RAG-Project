from vdb.util import chunk_text
from vdb.access import client, upsert_point
from qdrant_client.models import Filter, FieldCondition, MatchValue, VectorParams, Distance
from llm.access import llm_embedding

def cross_fold(text: str, params_list: list, path: str):
    """
    Cross validate different parameter effects on chunking method.
    
    For each set of parameters in params_list, chunk the text, replace the previous
    chunks in the collection 'RAG_Project_Test', and store the new chunks.
    
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
        # Clear previous chunks for this path
        client.delete(
            collection_name=coll_name,
            points_selector=Filter(
                must=[
                    FieldCondition(
                        key="path",
                        match=MatchValue(value=path)
                    )
                ]
            )
        )
        
        # Chunk with new params
        chunks = chunk_text(text, chunk_size=params['chunk_size'], overlap=params['overlap'])
        
        # Store chunks
        for ind, c in enumerate(chunks):
            if c and len(c.strip()) > 0:
                embedding = llm_embedding(c)
                upsert_point(coll_name=coll_name, path=path, cNum=ind, embedding_list=embedding, content=c)
        
        print(f"Tested params: chunk_size={params['chunk_size']}, overlap={params['overlap']}, chunks: {len(chunks)}")