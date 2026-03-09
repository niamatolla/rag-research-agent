from retrieval.search import search_chunks


def run_retrieveal_smoke_test():
    query="What is A-RAG?"
    results=search_chunks(query,top_k=5)

    print(f"Retrieved {len(results)} chunks.\n")

    for i, chunk in enumerate(results, start=1):
        print(f"Result #{i}")
        print("id:", chunk["id"])
        print("document_id:", chunk["document_id"])
        print("page_number:", chunk["page_number"])
        print("chunk_id:", chunk["chunk_id"])
        print("text preview:", chunk["text"][:300])
        print("-" * 80)

if __name__ == "__main__":
    run_retrieveal_smoke_test()