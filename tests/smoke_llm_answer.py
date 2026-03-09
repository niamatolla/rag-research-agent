from llm.answer import generate_answer


def run_answer_smoke_test():
    query = "What is A-RAG?"

    result = generate_answer(query, top_k=3)

    print("Question:", query)
    print("Answer:")
    print(result["answer"])

    print("\nSources:")
    for source in result["sources"]:
        print(f"- {source['document_id']} - chunk {source['chunk_id']}")

    assert result is not None
    assert isinstance(result, dict)
    assert isinstance(result["answer"], str)
    assert len(result["answer"].strip()) > 0
    assert isinstance(result["sources"], list)


if __name__ == "__main__":
    run_answer_smoke_test()