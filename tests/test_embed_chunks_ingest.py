import pytest
from unittest.mock import MagicMock, patch
from ingestion.ingest import embed_chunks



# ---------------------------
# Case 1 — Happy path
# ---------------------------
def test_embed_chunks_adds_embedding_to_valid_chunk():

    chunks_data=[
        {
        "text": "This is a test chunk.",
            "chunk_id": 0,
            "start_char": 0,
            "end_char": 21,
            "page_number": 1,
            "document_id": "doc1"
    }
    ]

    #fake embedding response
    fake_embeddings = [0.1, 0.2, 0.3]

    fake_item = MagicMock()
    fake_item.embedding = fake_embeddings

    fake_response = MagicMock()
    fake_response.data = [fake_item]

    mock_client = MagicMock()
    mock_client.embeddings.create.return_value = fake_response

    with patch("ingestion.ingest.OpenAIClient") as MockClient:
        MockClient.return_value.get_client.return_value=mock_client
        result=embed_chunks(chunks_data)


    assert len(result)==1

    enriched=result[0]

    assert enriched["chunk_id"]==0
    assert enriched["text"]=="This is a test chunk."
    assert enriched["document_id"]=="doc1"

    assert "embedding" in enriched
    assert enriched["embedding"] == fake_embeddings

    # make sure API was called
    mock_client.embeddings.create.assert_called_once()


# ---------------------------
# Case 2 — Empty Chunks
# ---------------------------
def test_embed_chunks_skips_empty_chunks():
    
    chunks_data=[{
           "text": "",
            "chunk_id": 0,
            "start_char": 0,
            "end_char": 21,
            "page_number": 1,
            "document_id": "doc1"

    }]

    #fake client 
    mock_client=MagicMock()
    with patch("ingestion.ingest.OpenAIClient") as MockClient:
        MockClient.return_value.get_client.return_value=mock_client
        result=embed_chunks(chunks_data)


    assert len(result)==0
    # make sure API was called
    mock_client.embeddings.create.assert_not_called()
# ---------------------------
# Case 3 — API failures
# ---------------------------
def test_embed_chunks_continues_on_api_failure():
    chunks_data=[
        {
        "text": "This is a test chunk.",
            "chunk_id": 0,
            "start_char": 0,
            "end_char": 21,
            "page_number": 1,
            "document_id": "doc1"
    }
    ]

    
    #fake client
    mock_client=MagicMock()
    mock_client.embeddings.create.side_effect=Exception("API failed")

    with patch("ingestion.ingest.OpenAIClient") as MockClient:
        MockClient.return_value.get_client.return_value=mock_client
        result=embed_chunks(chunks_data)

    assert len(result)==0
    mock_client.embeddings.create.assert_called_once()

# ---------------------------
# Case 4 — Mixed Chunks
# ---------------------------
def test_embed_chunks_handles_mixed_chunks():
    chunks_data = [
        {
            "text": "This is a valid chunk.",
            "chunk_id": 0,
            "start_char": 0,
            "end_char": 22,
            "page_number": 1,
            "document_id": "doc1"
        },
        {
            "text": "   ",
            "chunk_id": 1,
            "start_char": 23,
            "end_char": 26,
            "page_number": 1,
            "document_id": "doc1"
        },
        {
            "text": "This chunk will fail.",
            "chunk_id": 2,
            "start_char": 27,
            "end_char": 48,
            "page_number": 1,
            "document_id": "doc1"
        }
    ]

    fake_embedding = [0.1, 0.2, 0.3]
    fake_response = MagicMock()
    fake_response.data = [MagicMock(embedding=fake_embedding)]

    mock_client = MagicMock()
    mock_client.embeddings.create.side_effect = [
        fake_response,
        Exception("API failed")
    ]

    with patch("ingestion.ingest.OpenAIClient") as MockClient:
        MockClient.return_value.get_client.return_value = mock_client
        result = embed_chunks(chunks_data)

    assert len(result) == 1
    assert result[0]["chunk_id"] == 0
    assert result[0]["document_id"] == "doc1"
    assert result[0]["embedding"] == fake_embedding
    assert "embedding" in result[0]

    mock_client.embeddings.create.assert_called()
    assert mock_client.embeddings.create.call_count == 2

    


    