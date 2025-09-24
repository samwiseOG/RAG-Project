



# get files from path
import glob

import ollama

from extractor import create_extractor
from qdrant import create_collection, upsert_point
from util import chunk_text


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
def text_2_vec(text: str, path: str, coll_name: str):
    chunks = chunk_text(text, chunk_size = 100, overlap=0)
    for ind, c in enumerate(chunks):
        if c:
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

if __name__ == "__main__":
    setup()