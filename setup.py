



# get files from path
import argparse
import glob

import ollama

from extractor import create_extractor
from qdrant import create_collection, search, upsert_point
from util import chunk_text
from ollama import chat

def get_file(root_dir:str, type:str):
    res = []
    print(root_dir + '**/*.{_type}'.format(_type=type))
    for filename in glob.iglob(root_dir + '**/*.{_type}'.format(_type=type), recursive=True):
        print(filename)
        res.append(filename)
    return res


# Find text of pdf
def get_text_from_pdf(file: str):
    extractor = create_extractor(file)
    content = extractor.extract(file)
    return content

    # files_to_process = []
    # file_types = ['txt', 'docx', 'pptx']

    # file_list = []
    # for f in file_types:
    #     file_list.extend(get_file(root_dir=root_dir, type=f))

    # print(file_list)

    # for file in file_list:
    #     print(f"--- Processing: {file} ---")
    #     if not os.path.exists(file):
    #         print(f"Result: File not found. Skipping.\n")
    #         continue

    #     # Use the factory to get the right strategy
    #     extractor = create_extractor(file)
    #     # Execute the strategy
    #     content = extractor.extract(file)

    #     print(f"Result:\n{content}")
    #     print("-" * 25 + "\n")

# FOLDER_PATH: str = ""

# Chunk and insert into vector database
def text_2_vec(text: str, path: str, coll_name: str, chunk_size: int = 500, overlap: int = 50):
    """
    Convert text to vector embeddings with configurable chunking parameters.
    
    Args:
        text: Source text to process
        path: File path for reference
        coll_name: Collection name in the vector database
        chunk_size: Size of each chunk in tokens (default: 500)
        overlap: Number of overlapping tokens between chunks (default: 50)
    """
    chunks = chunk_text(text, chunk_size=chunk_size, overlap=overlap)
    for ind, c in enumerate(chunks):
        if c and len(c.strip()) > 0:  # Only process non-empty chunks
            embedding = ollama.embeddings(model="nomic-embed-text", prompt=c)
            upsert_point(coll_name=coll_name, path=path, cNum=ind, ollama_embedding_return=embedding, content=c)


def setup():
    FOLDER_PATH = "/home/sam/Documents/Projects/RAG/RAG-Project/"
    pdf_files = get_file(root_dir=FOLDER_PATH, type="pdf")
    print(pdf_files)
    coll_name = FOLDER_PATH.split("/")[-2]
    for f in pdf_files:
        text = get_text_from_pdf(file = f)
        text_2_vec(text=text, path=f, coll_name=coll_name)

ENHANCEMENT_TEMPLATE = """
Rewrite this query into a semantically rich search prompt that includes 
synonyms, relevant phrases, and domain-specific terminology, but keep it short:

query: {query}
"""





PROMPT_TEMPLATE = """
Answer the question based only on the following context:

{context}

---

Answer the question based on the above context: {question}
"""



def main():
    # Create CLI.
    parser = argparse.ArgumentParser()
    parser.add_argument("query_text", type=str, help="The query text.")
    args = parser.parse_args()
    query_text = args.query_text
    query_rag(query_text)

def enhance_query(query_text):
    prompt = ENHANCEMENT_TEMPLATE.format(query_text)
    # print(prompt)

    init_message = [{'role': 'user', 'content': prompt}]

    enhanced_query = chat(
        model = "deepseek-r1:1.5b",
        messages=init_message
    )['message']['content']
    print(enhanced_query)
    return enhanced_query

def query_rag(query_text: str):
    
    query_embedding = ollama.embeddings(model="nomic-embed-text", prompt=query_text).embedding

    search_result = search(coll_name="RAG-Project", query_embedding=query_embedding)


    context_text = "\n\n---\n\n".join([p.payload.get('content') for p in search_result])
    # prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = PROMPT_TEMPLATE.format(context=context_text, question=query_text)
    # print(prompt)

    init_message = [{'role': 'user', 'content': prompt}]

    response_text = chat(
        model = "deepseek-r1:1.5b",
        messages=init_message
    )['message']['content']



    sources = [p.payload.get('path') for p in search_result]
    formatted_response = f"Response: {response_text}\nSources: {sources}"
    return response_text


if __name__ == "__main__":
    setup()

    query_rag(query_text="who was the war in the pacific between?")