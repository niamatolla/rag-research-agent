from run_ingestion import build_knowledge_base

def run_ingestion_smoke_test():
    build_knowledge_base("data/sample_pdfs/A-RAG.pdf")
    print("Ingestion smoke test completed successfully")

if __name__ == "__main__":
    run_ingestion_smoke_test()