import pytest
from unittest.mock import patch
from ingestion.pdf_reader import read_all_pdfs


# ---------------------------
# Case 1 — Normal case
# ---------------------------
def test_read_all_pdfs_success(tmp_path):
    pdf1 = tmp_path / "file1.pdf"
    pdf2 = tmp_path / "file2.pdf"

    pdf1.touch()
    pdf2.touch()

    mock_pages = [{"text": "page 1"}, {"text": "page 2"}]

    with patch("ingestion.pdf_reader.read_pdf", return_value=mock_pages):
        result = read_all_pdfs(str(tmp_path))

    assert isinstance(result, list)
    assert len(result) == 4
    assert result == mock_pages + mock_pages


# ---------------------------
# Case 2 — Empty folder
# ---------------------------
def test_read_all_pdfs_empty_folder(tmp_path):
    with pytest.raises(ValueError, match="No PDF files found in folder"):
        read_all_pdfs(str(tmp_path))


# ---------------------------
# Case 3 — Invalid path
# ---------------------------
def test_read_all_pdfs_invalid_path():
    invalid_path = "this/path/does/not/exist"

    with pytest.raises(FileNotFoundError):
        read_all_pdfs(invalid_path)


# ---------------------------
# Case 4 — Path is not a folder
# ---------------------------
def test_read_all_pdfs_not_a_folder(tmp_path):
    file_path = tmp_path / "not_a_folder.txt"
    file_path.write_text("hello")

    with pytest.raises(ValueError, match="Path is not a folder"):
        read_all_pdfs(str(file_path))

# ---------------------------
# Case 5 — One corrupted PDF
# ---------------------------
def test_read_all_pdfs_with_corrupted_file(tmp_path):
    pdf1 = tmp_path / "good.pdf"
    pdf2 = tmp_path / "bad.pdf"

    pdf1.touch()
    pdf2.touch()

    def mock_read_pdf(path):
        if "bad.pdf" in path:
            raise Exception("Corrupted PDF")
        return [{"text": "valid page"}]

    with patch("ingestion.pdf_reader.read_pdf", side_effect=mock_read_pdf):
        result = read_all_pdfs(str(tmp_path))

    # Only the good PDF should be processed
    assert isinstance(result, list)
    assert len(result) == 1
    assert result == [{"text": "valid page"}]

