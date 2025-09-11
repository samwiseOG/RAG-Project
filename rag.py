import os
import re
from typing import List

import PyPDF2
import numpy as np
import pandas as pd
import tiktoken as tkn
import ollama  # Replaced OpenAI with ollama
from pdf2image import convert_from_path
from sklearn.neighbors import NearestNeighbors
from tqdm import tqdm

# --- Ollama Model Placeholders ---
# Replace these with the names of the models you have pulled in Ollama.
# For embeddings, you might use 'mxbai-embed-large', 'nomic-embed-text', or 'all-minilm'.
# For chat, you might use 'llama3', 'mistral', 'gemma', etc.
OLLAMA_EMBEDDING_MODEL = "nomic-embed-text" 
OLLAMA_CHAT_MODEL = "deepseek-r1:1.5b"
# ------------------------------------

BATCH_SIZE = 20

dirname = os.path.dirname(__file__)
pdf_file_path = os.path.join(dirname, "./data/history of submarines.pdf")
embedding_file_path = os.path.join(
    dirname, "./data/history of submarines.pdf.embeddings.csv"
)

# The 'query' variable is defined but not used in the original script's main flow.
# It is used as an example input for the functions if called directly.
query = "How should one approach debugging?"


def chunk_prompt(prompt: str, chunk_size: int = 2000, overlap: int = 50) -> List[str]:
    """Chunks a long text into smaller segments based on token count."""
    print("Begin chunking the page")
    print(f"Total length of the page: {len(prompt)}")

    # Note: Using tiktoken for gpt-3.5-turbo is an approximation.
    # Tokenization will vary slightly for different Ollama models.
    encoding = tkn.encoding_for_model("gpt-3.5-turbo")
    sentences = re.split(r"([.?!])", prompt)
    # Group sentences and their terminators back together
    sentences = ["".join(i) for i in zip(sentences[0::2], sentences[1::2])]

    n_tokens = [len(encoding.encode(" " + sentence)) for sentence in sentences]
    chunks, tokens_so_far, chunk = [], 0, []

    for sentence, token in zip(sentences, n_tokens):
        if tokens_so_far + token > chunk_size:
            chunks.append("".join(chunk))
            if overlap > 0:
                # A simple overlap strategy; more sophisticated methods could be used.
                overlap_sentences = [s for s in chunk if len(encoding.encode(s)) > 0][-overlap:]
                print(overlap_sentences)
                chunk = overlap_sentences
                tokens_so_far = sum(len(encoding.encode(" " + s)) for s in overlap_sentences)
            else:
                chunk, tokens_so_far = [], 0

        chunk.append(sentence)
        tokens_so_far += token

    if chunk:
        chunks.append("".join(chunk))

    print(f"Total number of chunks: {len(chunks)}")
    return chunks


def generate_embeddings(embedding_file_path):
    """Generates and saves embeddings for a PDF document if they don't already exist."""
    if os.path.exists(embedding_file_path):
        print(f"Loading embeddings from {embedding_file_path}...")
        return pd.read_csv(embedding_file_path)

    print("Generating embeddings...")
    with open(pdf_file_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        embeddings = []

        for page_num, page in enumerate(tqdm(reader.pages, desc="Processing Pages")):
            text = page.extract_text()
            if not text or not text.strip():
                continue

            page_chunks = chunk_prompt(text, chunk_size=500, overlap=5)

            for chunk in page_chunks:
                # Generate embedding for each chunk using Ollama
                response = ollama.embeddings(
                    model=OLLAMA_EMBEDDING_MODEL,
                    prompt=chunk
                )
                embedding_str = ",".join(map(str, response["embedding"]))
                embeddings.append(
                    {
                        "document_name": "data/ThePragmaticProgrammer.pdf",
                        "page_number": page_num,
                        "embedding": embedding_str,
                        "context": chunk,
                    }
                )

    embeddings_df = pd.DataFrame(
        embeddings, columns=["document_name", "page_number", "embedding", "context"]
    )
    embeddings_df.to_csv(embedding_file_path, index=False)
    print(f"Embeddings saved to {embedding_file_path}")
    return embeddings_df


def converse2(prompt, messages=None, model=OLLAMA_CHAT_MODEL):
    """
    Sends a prompt to the Ollama chat model and maintains conversation history.
    """
    if messages is None:
        messages = []

    messages.append({"role": "user", "content": prompt})

    # Call the Ollama chat API
    response_data = ollama.chat(
        model=model,
        messages=messages,
    )
    
    # Extract the response content
    response = response_data['message']['content']

    messages.append({"role": "assistant", "content": response})

    return response, messages

def get_embeddings_df(pdf_file_path, embedding_file_path):
    """Returns embeddings_df if it exists, otherwise generates it."""
    if os.path.exists(embedding_file_path):
        print(f"Loading embeddings from {embedding_file_path}...")
        embeddings_df = pd.read_csv(embedding_file_path)
    else:
        print("Embedding file not found. Generating embeddings...")
        embeddings_df = generate_embeddings(embedding_file_path)
    return embeddings_df

def local_search(query):
    """
    Finds the most relevant context from the PDF based on the query's embedding.
    """
    prompt_template = """
Answer the following question using only the context provided.
If the context does not contain the answer, state that you don't know.

Question: 
{question}

Context: 
{context}
"""
    embeddings_df = get_embeddings_df(pdf_file_path, embedding_file_path)

    # Ensure embeddings are loaded correctly as numpy arrays
    embeddings = np.array([np.fromstring(e, sep=',') for e in embeddings_df["embedding"]])
    
    nbrs = NearestNeighbors(n_neighbors=5, algorithm="ball_tree").fit(embeddings)

    # Generate embedding for the user query using Ollama
    response = ollama.embeddings(model=OLLAMA_EMBEDDING_MODEL, prompt=query)
    query_embedding = np.array(response["embedding"]).reshape(1, -1)

    distances, indices = nbrs.kneighbors(query_embedding)

    # Combine context from the top 3 nearest neighbors
    llm_context = "\n---\n".join(
        embeddings_df.iloc[idx]["context"] for idx in indices[0][:3]
    )

    # The most relevant page number
    page_num = embeddings_df.iloc[indices[0][0]]["page_number"]

    prompt = prompt_template.format(question=query, context=llm_context)

    return int(page_num), prompt


def getPDFImage(pdf_file_path, page_num):
    """Converts a specific page of a PDF to an image."""
    pdf_images = convert_from_path(pdf_file_path, dpi=200)
    return pdf_images[page_num]


def ask_book(prompt, return_image=False):
    """
    Main function to ask a question about the book, retrieve relevant context,
    get an answer from the LLM, and optionally return an image of the page.
    """
    rag_result = {}
    page_num, llm_prompt = local_search(prompt)
    
    response, messages = converse2(llm_prompt, [])
    
    rag_result["page_number"] = page_num + 1  # Adjust for 1-based indexing
    rag_result["context"] = llm_prompt
    rag_result["answer"] = response
    
    if return_image:
        rag_result["image_data"] = getPDFImage(pdf_file_path, page_num)
    else:
        rag_result["image_data"] = None
        
    print(f"Image data: {'Available' if rag_result['image_data'] else 'Not requested'}")
    
    return rag_result

# Example of how to run the main function:
# import asyncio
#
# async def main():
#     result = await ask_book("How should one approach debugging?", return_image=False)
#     print("--- Question ---")
#     print(query)
#     print("\n--- Answer ---")
#     print(result["answer"])
#     print(f"\nSource Page: {result['page_number']}")
#
# if __name__ == "__main__":
#     asyncio.run(main())