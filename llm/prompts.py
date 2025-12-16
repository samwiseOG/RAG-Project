
from llm.access import llm_chat


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




def enhance_query(query_text):
    prompt = ENHANCEMENT_TEMPLATE.format(query = query_text)
    # print(prompt)
    return prompt


def search_prompt(context: str, question: str):
    prompt = PROMPT_TEMPLATE.format(context=context, question=question)
    return prompt
