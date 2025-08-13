import os
import re
from typing import List

import PyPDF2
import numpy as np
import pandas as pd
import tiktoken as tkn
from dotenv import load_dotenv
from openai import OpenAI
from pdf2image import convert_from_path
from sklearn.neighbors import NearestNeighbors
from tqdm import tqdm

client = OpenAI(
    base_url="http://aitools.cs.vt.edu:7860/openai/v1",
    api_key="aitools",
)

EMBEDDING_MODEL = "text-embedding-3-small"
BATCH_SIZE = 20

dirname = os.path.dirname(__file__)
pdf_file_path = os.path.join(dirname, "../data/ThePragmaticProgrammer.pdf")
embedding_file_path = os.path.join(
    dirname, "../data/ThePragmaticProgrammer.embeddings.csv"
)

load_dotenv()

query = "How should one approach debugging?"


def chunk_prompt(prompt: str, chunk_size: int = 2000, overlap: int = 50) -> List[str]:
    print("Begin chunking the page")
    print("Total length of the page: ", len(prompt))

    sentences = re.split(r"[.?!]", prompt)

    n_tokens = [
        len(tkn.encoding_for_model("gpt-3.5-turbo").encode(" " + sentence))
        for sentence in sentences
    ]

    chunks, tokens_so_far, chunk = [], 0, []

    for sentence, token in zip(sentences, n_tokens):
        if tokens_so_far + token > chunk_size:
            chunks.append(". ".join(chunk) + ".")

            if overlap > 0:
                chunk = chunk[-overlap:]
                tokens_so_far = sum(
                    [
                        len(tkn.encoding_for_model("gpt-3.5-turbo").encode(c))
                        for c in chunk
                    ]
                )
            else:
                chunk = []
                tokens_so_far = 0

        chunk.append(sentence)
        tokens_so_far += token + 1

    if chunk:
        chunks.append(". ".join(chunk) + ".")

    print("Total number of chunks: ", len(chunks))


    return chunks


def generate_embeddings(embedding_file_path):
    if os.path.exists(embedding_file_path):
        print(f"Loading embeddings from {embedding_file_path}...")
        embeddings_df = pd.read_csv(embedding_file_path)
    else:
        with open(pdf_file_path, "rb") as file:
            reader = PyPDF2.PdfFileReader(file)

            embeddings = []

            for page_num in tqdm(range(reader.numPages)):
                page = reader.getPage(page_num)
                text = page.extractText().strip()
                if text:
                    page_chunks = chunk_prompt(text, chunk_size=1500, overlap=50)
            
                    for batch_start in range(0, len(page_chunks), BATCH_SIZE):
                        batch_end = batch_start + BATCH_SIZE
                        batch = page_chunks[batch_start:batch_end]
                        print(f"Batch {batch_start} to {batch_end - 1}")

                        response = client.embeddings.create(
                            model=EMBEDDING_MODEL, input=batch, encoding_format="float"
                        )

                        for i, be in enumerate(response.data):
                            assert i == be.index
                            embedding_str = ",".join(map(str, be.embedding))

                            embeddings.append(
                                {
                                    "document_name": "data/ThePragmaticProgrammer.pdf",
                                    "page_number": page_num,
                                    "embedding": embedding_str,
                                    "context": batch[i],
                                }
                            )

        embeddings_df = pd.DataFrame(
            embeddings, columns=["document_name", "page_number", "embedding", "context"]
        )

        embeddings_df.to_csv(embedding_file_path, index=False)

    return embeddings_df


def converse2(
    prompt,
    messages=None,
    model="gpt-3.5-turbo",
    max_tokens=1500,
    temperature=0,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0,
):
    client = OpenAI(
        base_url="http://aitools.cs.vt.edu:7860/openai/v1", api_key="aitools"
    )

    if messages is None:
        messages = []

    messages.append({"role": "user", "content": prompt})

    response = (
        client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
        )
        .choices[0]
        .message.content
    )

    messages.append({"role": "assistant", "content": response})

    return response, messages

def get_embeddings_df(pdf_file_path, embedding_file_path):
    """Returns embeddings_df if it exists in the local database, otherwise generates it."""
    if os.path.exists(embedding_file_path):
        print(f"Loading embeddings from {embedding_file_path}...")
        embeddings_df = pd.read_csv(embedding_file_path)
    else:
        print(f"Embedding file not found. Generating embeddings...")
        embeddings_df = generate_embeddings(embedding_file_path)
    return embeddings_df

def local_search(query):

    prompt_template = """
Answer the following question using the context provided:
%Question: 
```
{question}
``` 
%Context: 
```
{context}
```
"""

    embeddings_df = get_embeddings_df(pdf_file_path, embedding_file_path)

    embeddings = [
        np.array(e.split(",")).astype(float)
        for e in embeddings_df["embedding"].tolist()
    ]
    nbrs = NearestNeighbors(n_neighbors=5, algorithm="ball_tree").fit(embeddings)

    response = client.embeddings.create(model=EMBEDDING_MODEL, input=query)
    query_embedding = np.array(response.data[0].embedding).reshape(1, -1)

    distances, indices = nbrs.kneighbors(query_embedding)

    llm_context = ""
    count_chuns = 0
    for idx in indices[0]:
        if count_chuns < 3:
            llm_context += embeddings_df.iloc[idx]["context"]
            count_chuns += 1
        else:
            break

    page_num = indices[0][0]

    prompt = prompt_template.format(
        question=query, context=llm_context
    )


    return page_num, prompt



async def getPDFImage(pdf_file_path, page_num):
    pdf_images = convert_from_path(pdf_file_path,dpi=200)

    return pdf_images[page_num]
    


async def ask_book(prompt, return_image):
    rag_result = {}
    page_num, prompt = local_search(prompt)
    actual_page = page_num + 1
    response, messages = converse2(prompt, [])
    rag_result["page_number"] = actual_page
    rag_result["context"] = prompt
    rag_result["image_data"] = await getPDFImage(pdf_file_path, page_num) if return_image else None
    print(f"Image data: {rag_result["image_data"]}")
    rag_result["answer"] = response
    return rag_result

