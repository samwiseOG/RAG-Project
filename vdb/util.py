import re
from typing import List

from llm.access import llm_embedding
from .access import *

import re
from typing import List

from llm.access import llm_embedding
from .access import *

def chunk_text(text: str, chunk_size: int = 2000, overlap: int = 1) -> List[str]:
    """
    Chunks a long text into smaller segments based on character count (approximating tokens).
    
    This function splits the input text into sentences, then groups them into chunks
    where each chunk's total character length does not exceed chunk_size. Overlapping
    sentences can be included between chunks to maintain context.
    
    Args:
        text: The input text to be chunked.
        chunk_size: Maximum character count per chunk (default: 2000).
        overlap: Number of overlapping sentences between chunks (default: 50).
    
    Returns:
        List[str]: A list of text chunks, each as a string.
    
    Expected output: A list of strings, where each string is a chunk of the original text.
    For example, if the input text is a long document, the output might be:
    ["This is the first chunk of text.", "This is the second chunk with some overlap."]
    """
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
    Convert text to vector embeddings and store them in the vector database.
    
    This function takes input text, chunks it into smaller segments, generates
    vector embeddings for each chunk using an LLM, and stores the embeddings
    along with metadata in the specified vector database collection.
    
    Args:
        text: The source text to process and embed.
        path: File path for reference (used as metadata).
        coll_name: Name of the collection in the vector database.
    
    Returns:
        None: This function does not return a value. It performs side effects
        by storing vector embeddings in the database.
    
    Expected output: No direct output. The function modifies the vector database
    by adding points (embeddings) for each text chunk. Each point includes:
    - The embedding vector
    - Metadata: path, chunk number (cNum), and the chunk content
    """
    chunks = chunk_text(text)
    for ind, c in enumerate(chunks):
        if c and len(c.strip()) > 0:  # Only process non-empty chunks
            embedding = llm_embedding(c)
            upsert_point(coll_name=coll_name, path=path, cNum=ind, embedding_list=embedding, content=c)
