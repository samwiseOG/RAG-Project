import re
from typing import List

from llm.access import llm_embedding
from .access import *

def chunk_text(text: str, chunk_size: int = 2000, overlap: int = 50) -> List[str]:
    """Chunks a long text into smaller segments based on token count."""
    print("Begin chunking the page")
    print(f"Total length of the page: {len(text)}")


    sentences = re.split(r"([.?!])", text)
    sentences = ["".join(i) for i in zip(sentences[0::2], sentences[1::2])]

    n_tokens = [len(sentence) for sentence in sentences]
    chunks, tokens_so_far, chunk = [], 0, []

    for sentence, token in zip(sentences, n_tokens):
        if tokens_so_far + token > chunk_size:
            chunks.append("".join(chunk))
            if overlap > 0:
                overlap_sentences = [s for s in chunk if len(s) > 0][-overlap:]
                chunk = overlap_sentences
                tokens_so_far = sum(len(s) for s in overlap_sentences)
            else:
                chunk, tokens_so_far = [], 0

        chunk.append(sentence)
        tokens_so_far += token

    if chunk:
        chunks.append("".join(chunk))

    print(f"Total number of chunks: {len(chunks)}")
    return chunks

def text_2_vec(text: str, path: str, coll_name: str):
    """
    Convert text to vector embeddings with configurable chunking parameters.
    
    Args:
        text: Source text to process
        path: File path for reference
        coll_name: Collection name in the vector database
        chunk_size: Size of each chunk in tokens (default: 500)
        overlap: Number of overlapping tokens between chunks (default: 50)
    """
    chunks = chunk_text(text)
    for ind, c in enumerate(chunks):
        if c and len(c.strip()) > 0:  # Only process non-empty chunks
            embedding = llm_embedding(c)
            upsert_point(coll_name=coll_name, path=path, cNum=ind, embedding_list=embedding, content=c)
