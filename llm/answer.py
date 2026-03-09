from llm.openai_client import OpenAIClient
from config.settings import settings
from retrieval.search import search_chunks


SYSTEM_PROMPT = """
You are a helpful research assistant.

Use ONLY the provided context to answer the user's question.
Do NOT  use outside knowledge.
Do NOT include information that is not explicitly stated in the context.
Do NOT infer or generalize beyond the context.
If the answer is not available in the context, say:
"The answer is not available in the provided context."

Be clear, concise, and factual.
"""

def build_prompt(query: str, retrieved_chunks: list[dict]) -> str: 
    """
    prompt contruction using retrieved chunks 
    """

    formatted_chunks = []

    for i,chunk in enumerate(retrieved_chunks, start=1):
        formatted_chunks.append(
            "\n".join(
                [
                    f"[Chunk {i}]",
                    f"Document: {chunk['document_id']}",
                    f"Chunk: {chunk['chunk_id']}",
                    f"Text: {chunk['text'].strip()}",
                ]
            )
        )

    context = "\n\n".join(formatted_chunks)

    prompt = f"""

Context:
{context}

Question:
{query}

Answer:
"""

    return prompt.strip()

def generate_answer(query:str, top_k: int=5) -> dict:
    """
    entry point function to answer generation
     - calls retrieval to get relevant chunks
     - builds prompt using retrieved chunks and query
     - calls llm to generate answer
     - returns answer   

    """
    
    # Retrieve
    retrieved_chunks= search_chunks(query, top_k)


    # Handle no context case
    if not retrieved_chunks:
       return{ ""
       "answer": "I could not find relevant context to answer this question.",
         "sources": []
       }
    
    
    sources = [
      {
        "document_id": chunk["document_id"],
        "chunk_id": chunk["chunk_id"],
        }
    for chunk in retrieved_chunks
]
    
    #print("Retrieved Chunks:")
    #for chunk in retrieved_chunks:
        #print(chunk["document_id"], "-", chunk["chunk_id"])

    #Build prompt 

    prompt= build_prompt(query , retrieved_chunks)

    # Call the client and chat completion 
    client = OpenAIClient().get_client()

    response=client.chat.completions.create(
        model=settings.AZURE_OPENAI_CHAT_DEPLOYMENT,
        messages=[
             {"role": "system", "content": SYSTEM_PROMPT.strip()},
             {"role": "user", "content": prompt}
        ],
        temperature=0.0,
        max_tokens=300,
    )

    #Extract the answer 
    grounded_answer= response.choices[0].message.content

    #Sanity check on the answer 
    if not grounded_answer or not grounded_answer.strip():
        return {
            "answer": "The answer is not available in the provided context.",
            "sources": sources
        }

    #Return the answer
    return {
       "answer": grounded_answer.strip(),
       "sources": sources
    }

