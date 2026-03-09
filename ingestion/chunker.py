def chunk_text(
    text: str,
    chunk_size: int = 500,
    overlap_size: int = 50,
    page_number: int | None = None,
    document_id: str | None = None,
) -> list[dict]:
    """
    assumes it receives usable text and the job is only to split it
    """
    start=0
    end=len(text)
    step=chunk_size-overlap_size
    chunks_data=[]
    i=0

    if not text or not text.strip():
        return[]
    
    if(overlap_size<=0 or chunk_size<=0):
        raise ValueError(f"Overlap size  and Chunk size must be positive values:{overlap_size} <=0 {chunk_size}<=0")



    if(overlap_size>=chunk_size):
        raise ValueError(f"Overlap size must be smaller then the Chunking size :{overlap_size} >= {chunk_size}")

    while(start<end):
        chunk=text[start:start+chunk_size]

        chunk_record={
            "text":chunk,
            "chunk_id":i,
            "start_char":start,
            "end_char":start+chunk_size,
            "page_number": page_number,
            "document_id": document_id,
        }

        chunks_data.append(chunk_record)
        start=start+step
        i=i+1
 
    return(chunks_data)
