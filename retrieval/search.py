from llm.openai_client import OpenAIClient
from config.settings import settings
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery


def embed_query(query:str)->list[float]:

    """
    Generate an embedding for a user query using the same azure
    OpenAI embedding deployment used during ingestion
    """

    if not isinstance(query,str) or not query.strip():
        raise ValueError(" query must be a non empty string")
    
    clean_query= query.strip()
    client= OpenAIClient().get_client()

    response= client.embeddings.create(
        model=settings.AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT,
        input=clean_query,
    )

    query_embedding=response.data[0].embedding

    if not query_embedding:
         raise ValueError("embedding generation failed: empty embedding returned")
    return query_embedding


def vector_search(query_embedding: list[float], top_k: int = 5) -> list[dict]:
    """
    Perform pure vector search in Azure AI Search using a query embedding.
    Returns the top-k most relevant chunks.
    """

    if not query_embedding:
        raise ValueError("query_embedding must be a non-empty list")

    if top_k <= 0:
        raise ValueError("top_k must be greater than 0")

    #Create search client 
    search_client = SearchClient(
        endpoint=settings.AZURE_SEARCH_ENDPOINT,
        index_name=settings.AZURE_SEARCH_INDEX,
        credential=AzureKeyCredential(settings.AZURE_SEARCH_KEY),
    )

    #Build vector query 
    vector_query = VectorizedQuery(
        vector=query_embedding,
        k_nearest_neighbors=top_k,
        fields="embedding",
    )

    #Call search 
    results = search_client.search(
        search_text=None,
        vector_queries=[vector_query],
        select=["id", "text", "document_id", "page_number", "chunk_id"],
        top=top_k,
    )

    #Process results
    chunks = []
    for result in results:
        chunks.append(
            {
                "id": result["id"],
                "text": result["text"],
                "document_id": result["document_id"],
                "page_number": result["page_number"],
                "chunk_id": result["chunk_id"],
            }
        )

    #Return Results 
    return chunks

def search_chunks(query: str, top_k: int = 5)->list[dict]:
    """
    entry point function to retrieval
    """
    query_embedding = embed_query(query)
    results = vector_search(query_embedding, top_k)
    return results