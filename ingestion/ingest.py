from config.settings import settings
from llm.openai_client import OpenAIClient
from config.settings import settings
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential

def embed_chunks(chunks_data:list[dict])->list[dict]:

    """
        Generate embeddings for chunk records and return enriched chunk records
        containing the original metadata, text, and embedding vector.
    """


    client = OpenAIClient().get_client()
    enriched_chunk_data=[]

    for chunk in chunks_data:
        text=chunk["text"]

        if not text or not text.strip():
            continue
        try:     
            response = client.embeddings.create(
            input=text,
            model=settings.AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT
    )
            embedding = response.data[0].embedding
    
            enriched_chunk_record={
                 "text":text,
                "chunk_id":chunk["chunk_id"],
                "start_char":chunk["start_char"],
                "end_char":chunk["end_char"],
                "page_number": chunk["page_number"],
                "document_id": chunk["document_id"],
                "embedding":embedding,
        }
            enriched_chunk_data.append(enriched_chunk_record)
        except Exception as e:
           print(f"chunk {chunk['chunk_id']} from page {chunk['page_number']} of doc {chunk['document_id']} failed : {e}")
    return(enriched_chunk_data)

def build_search_documents(enriched_chunks: list[dict]) -> list[dict]:
    """
        Convert enriched chunk records into Azure AI Search document format.

         Each input record is expected to contain:
            - text
            - chunk_id
            -   start_char
            - end_char
            - page_number
            - document_id
            - embedding

        Returns:
        list[dict]: Search-ready documents with unique "id" field.
    """
    search_documents = []

    required_keys = {
        "text",
        "chunk_id",
        "start_char",
        "end_char",
        "page_number",
        "document_id",
        "embedding",
    }

    for chunk in enriched_chunks:
        missing_keys = required_keys - chunk.keys()
        if missing_keys:
            raise ValueError(
                f"Missing required keys in enriched chunk: {missing_keys}"
            )
        safe_document_id = (
            chunk["document_id"]
            .replace(".pdf", "")
            .replace(".", "_")
            .replace(" ", "_")
        )

        search_document = {
            "id": f"{safe_document_id}-p{chunk['page_number']}-c{chunk['chunk_id']}",
            "text": chunk["text"],
            "chunk_id": chunk["chunk_id"],
            "start_char": chunk["start_char"],
            "end_char": chunk["end_char"],
            "page_number": chunk["page_number"],
            "document_id": chunk["document_id"],
            "embedding": chunk["embedding"],
        }

        search_documents.append(search_document)

    return search_documents

def index_chunks(search_documents: list[dict]) -> None:
    """
        Index search documents to the Azure AI  search index 

        v1 prioritize correctness so failed indexing for one chunk we fail the
        whole indexing pipeline to  avoid having an icomplete knowledge base and miss context
    
    """

    if not search_documents:
        raise ValueError("No search documents provided for indexing")

    #Create a client
    client=  SearchClient(
        endpoint=settings.AZURE_SEARCH_ENDPOINT,
        index_name=settings.AZURE_SEARCH_INDEX,
        credential= AzureKeyCredential(settings.AZURE_SEARCH_KEY))

    #Call upload
    results=client.upload_documents(documents=search_documents)

    #Inspect result 
    failed =[]

    for r in results:
        if not r.succeeded:
            failed.append({
                "id":r.key,
                "error":r.error_message
            })

    #Handle Failure
    if failed:
        print("❌ Some documents failed:")
        for f in failed:
            print(f)
        raise Exception("Indexing failed")
    
    print("✅ All documents indexed successfully")






