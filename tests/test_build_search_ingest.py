import pytest
from ingestion.ingest import build_search_documents

# ---------------------------
# Case 1 — Happy path
# ---------------------------
def test_build_search_documents_creates_valid_search_record():
    enriched_chunks = [
        {
            "text": "This is a test chunk.",
            "chunk_id": 0,
            "start_char": 0,
            "end_char": 21,
            "page_number": 1,
            "document_id": "doc1",
            "embedding": [0.1, 0.2, 0.3],
        }
    ]

    result = build_search_documents(enriched_chunks)

    assert len(result) == 1

    search_doc = result[0]

    assert search_doc["id"] == "doc1-p1-c0"
    assert search_doc["text"] == "This is a test chunk."
    assert search_doc["chunk_id"] == 0
    assert search_doc["start_char"] == 0
    assert search_doc["end_char"] == 21
    assert search_doc["page_number"] == 1
    assert search_doc["document_id"] == "doc1"
    assert search_doc["embedding"] == [0.1, 0.2, 0.3]


def test_build_search_documents_handles_multiple_chunks():
    enriched_chunks = [
        {
            "text": "Chunk one",
            "chunk_id": 0,
            "start_char": 0,
            "end_char": 9,
            "page_number": 1,
            "document_id": "doc1",
            "embedding": [0.1, 0.2],
        },
        {
            "text": "Chunk two",
            "chunk_id": 1,
            "start_char": 10,
            "end_char": 19,
            "page_number": 1,
            "document_id": "doc1",
            "embedding": [0.3, 0.4],
        },
    ]

    result = build_search_documents(enriched_chunks)

    assert len(result) == 2
    assert result[0]["id"] == "doc1-p1-c0"
    assert result[1]["id"] == "doc1-p1-c1"


def test_build_search_documents_returns_empty_list_for_empty_input():
    result = build_search_documents([])

    assert result == []


def test_build_search_documents_preserves_input_data():
    enriched_chunks = [
        {
            "text": "Original chunk",
            "chunk_id": 2,
            "start_char": 50,
            "end_char": 100,
            "page_number": 3,
            "document_id": "docA",
            "embedding": [0.5, 0.6],
        }
    ]

    original_copy = [chunk.copy() for chunk in enriched_chunks]

    result = build_search_documents(enriched_chunks)

    assert enriched_chunks == original_copy
    assert result[0]["text"] == "Original chunk"
    assert result[0]["document_id"] == "docA"

# ---------------------------
# Case 2 — Error tests
# ---------------------------
def test_build_search_documents_raises_error_if_text_missing():
    enriched_chunks = [
        {
            "chunk_id": 0,
            "start_char": 0,
            "end_char": 10,
            "page_number": 1,
            "document_id": "doc1",
            "embedding": [0.1, 0.2],
        }
    ]

    with pytest.raises(ValueError, match="Missing required keys"):
        build_search_documents(enriched_chunks)

# ---------------------------
# Case 1 — Happy path
# ---------------------------
def test_build_search_documents_raises_error_if_chunk_id_missing():
    enriched_chunks = [
        {
            "text": "Test chunk",
            "start_char": 0,
            "end_char": 10,
            "page_number": 1,
            "document_id": "doc1",
            "embedding": [0.1, 0.2],
        }
    ]

    with pytest.raises(ValueError, match="Missing required keys"):
        build_search_documents(enriched_chunks)

# ---------------------------
# Case 1 — Happy path
# ---------------------------
def test_build_search_documents_raises_error_if_start_char_missing():
    enriched_chunks = [
        {
            "text": "Test chunk",
            "chunk_id": 0,
            "end_char": 10,
            "page_number": 1,
            "document_id": "doc1",
            "embedding": [0.1, 0.2],
        }
    ]

    with pytest.raises(ValueError, match="Missing required keys"):
        build_search_documents(enriched_chunks)

# ---------------------------
# Case 1 — Happy path
# ---------------------------
def test_build_search_documents_raises_error_if_end_char_missing():
    enriched_chunks = [
        {
            "text": "Test chunk",
            "chunk_id": 0,
            "start_char": 0,
            "page_number": 1,
            "document_id": "doc1",
            "embedding": [0.1, 0.2],
        }
    ]

    with pytest.raises(ValueError, match="Missing required keys"):
        build_search_documents(enriched_chunks)

# ---------------------------
# Case 1 — Happy path
# ---------------------------
def test_build_search_documents_raises_error_if_page_number_missing():
    enriched_chunks = [
        {
            "text": "Test chunk",
            "chunk_id": 0,
            "start_char": 0,
            "end_char": 10,
            "document_id": "doc1",
            "embedding": [0.1, 0.2],
        }
    ]

    with pytest.raises(ValueError, match="Missing required keys"):
        build_search_documents(enriched_chunks)

# ---------------------------
# Case 1 — Happy path
# ---------------------------
def test_build_search_documents_raises_error_if_document_id_missing():
    enriched_chunks = [
        {
            "text": "Test chunk",
            "chunk_id": 0,
            "start_char": 0,
            "end_char": 10,
            "page_number": 1,
            "embedding": [0.1, 0.2],
        }
    ]

    with pytest.raises(ValueError, match="Missing required keys"):
        build_search_documents(enriched_chunks)


def test_build_search_documents_raises_error_if_embedding_missing():
    enriched_chunks = [
        {
            "text": "Test chunk",
            "chunk_id": 0,
            "start_char": 0,
            "end_char": 10,
            "page_number": 1,
            "document_id": "doc1",
        }
    ]

    with pytest.raises(ValueError, match="Missing required keys"):
        build_search_documents(enriched_chunks)

# ----------------------------
# Case 3 — ID GENERATION TESTS
# ----------------------------
def test_build_search_documents_creates_unique_ids_for_different_pages():
    enriched_chunks = [
        {
            "text": "Page 1 chunk",
            "chunk_id": 0,
            "start_char": 0,
            "end_char": 20,
            "page_number": 1,
            "document_id": "doc1",
            "embedding": [0.1, 0.2],
        },
        {
            "text": "Page 2 chunk",
            "chunk_id": 0,
            "start_char": 0,
            "end_char": 20,
            "page_number": 2,
            "document_id": "doc1",
            "embedding": [0.3, 0.4],
        },
    ]

    result = build_search_documents(enriched_chunks)

    assert result[0]["id"] == "doc1-p1-c0"
    assert result[1]["id"] == "doc1-p2-c0"
    assert result[0]["id"] != result[1]["id"]


def test_build_search_documents_creates_unique_ids_for_different_documents():
    enriched_chunks = [
        {
            "text": "Doc 1 chunk",
            "chunk_id": 0,
            "start_char": 0,
            "end_char": 20,
            "page_number": 1,
            "document_id": "doc1",
            "embedding": [0.1, 0.2],
        },
        {
            "text": "Doc 2 chunk",
            "chunk_id": 0,
            "start_char": 0,
            "end_char": 20,
            "page_number": 1,
            "document_id": "doc2",
            "embedding": [0.3, 0.4],
        },
    ]

    result = build_search_documents(enriched_chunks)

    assert result[0]["id"] == "doc1-p1-c0"
    assert result[1]["id"] == "doc2-p1-c0"
    assert result[0]["id"] != result[1]["id"]