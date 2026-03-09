import argparse
from pathlib import Path

from ingestion.pdf_reader import read_pdf, read_all_pdfs
from ingestion.chunker import chunk_text
from ingestion.ingest import embed_chunks, build_search_documents, index_chunks


def load_pages(input_path: str) -> list[dict]:
    """
    Load pages from either:
    - a single PDF file
    - a folder containing PDF files
    """
    path = Path(input_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Path not found: {input_path}\n"
            f"Please provide a valid PDF file or a folder containing PDF files."
        )

    if path.is_file():
        if path.suffix.lower() != ".pdf":
            raise ValueError(
                f"Expected a PDF file, but got: {input_path}"
            )
        return read_pdf(str(path))

    if path.is_dir():
        return read_all_pdfs(str(path))

    raise ValueError(
        f"Unsupported path type: {input_path}"
    )


def build_chunks(pages: list[dict]) -> list[dict]:
    """
    Chunk all extracted pages into chunk records.
    """
    all_chunks = []

    for page in pages:
        chunks = chunk_text(
            text=page["text"],
            page_number=page["page_number"],
            document_id=page["document_id"],
        )
        all_chunks.extend(chunks)

    return all_chunks


def build_knowledge_base(input_path: str) -> None:
    """
    Build the knowledge base by running the full ingestion pipeline:
    1. Read PDF(s)
    2. Chunk text
    3. Embed chunks
    4. Build Azure AI Search documents
    5. Index documents into Azure AI Search
    """

    print(f"Starting ingestion for: {input_path}")

    # 1. Read PDF(s)
    pages = load_pages(input_path)
    print(f"Pages extracted: {len(pages)}")

    if not pages:
        raise ValueError(
            "No readable pages were extracted from the provided path."
        )

    # 2. Chunk text
    all_chunks = build_chunks(pages)
    print(f"Chunks created: {len(all_chunks)}")

    if not all_chunks:
        raise ValueError(
            "No chunks were created. Check PDF extraction or chunking."
        )

    # 3. Embed chunks
    enriched_chunks = embed_chunks(all_chunks)
    print(f"Enriched chunks: {len(enriched_chunks)}")

    if not enriched_chunks:
        raise ValueError(
            "No enriched chunks were created. Check embedding stage."
        )

    # 4. Build search documents
    search_documents = build_search_documents(enriched_chunks)
    print(f"Search documents built: {len(search_documents)}")

    if not search_documents:
        raise ValueError(
            "No search documents were built. Check document construction stage."
        )

    # 5. Index into Azure AI Search
    index_chunks(search_documents)

    print("Ingestion pipeline completed successfully.")


def run_ingestion(input_path: str) -> None:
    """
    Backward-compatible wrapper for existing callers.
    """
    build_knowledge_base(input_path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the PDF ingestion pipeline for Azure AI Search."
    )
    parser.add_argument(
        "--path",
        required=True,
        help="Path to a PDF file or a folder containing PDF files.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    build_knowledge_base(args.path)