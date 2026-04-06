

from llm.access import llm_chat, llm_embedding
from llm.prompts import search_prompt
from vdb.access import search


def query_rag(query_text: str, coll_name: str = "RAG-Project"):
    
    query_embedding = llm_embedding(query_text)

    search_result = search(coll_name=coll_name, query_embedding=query_embedding)

    context_text = "\n\n---\n\n".join([p.payload.get('content') for p in search_result])
    
    prompt = search_prompt(context=context_text, question=query_text)


    response_text = llm_chat(
        prompt=prompt,
    )[0]

    sources = [p.payload.get('path') for p in search_result]
    formatted_response = f"Response: {response_text}\nSources: {sources}"
    return response_text