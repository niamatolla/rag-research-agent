import pytest
from llm.answer import build_prompt

# ---------------------------
# Case 1 — Happy path
# ---------------------------
def test_build_prompt_includes_query_and_chunks():
    chunks = [
        {
            "document_id": "A-RAG.pdf_p9",
            "chunk_id": 0,
            "text": "A-RAG is an agentic RAG framework."
        }
    ]

    prompt = build_prompt("What is A-RAG?",chunks)

    assert "What is A-RAG?" in prompt
    assert "A-RAG is an agentic RAG framework." in prompt 
    assert "A-RAG.pdf_p9" in prompt

# ---------------------------
# Case 2 — No chunks
# ---------------------------
def test_build_prompt_no_chunks():
    prompt = build_prompt("What is A-RAG?",[])

    assert "What is A-RAG?" in prompt
    assert "Context:" in prompt
    assert "Answer:" in prompt
    # With no chunks, context section should be empty but structure intact
    assert "Context:\n\n\nQuestion:" in prompt    