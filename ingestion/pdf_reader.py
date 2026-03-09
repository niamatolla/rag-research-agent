from pypdf import PdfReader
from pathlib import Path
import re

def clean_text(text: str) -> str:
    """
    Clean raw PDF text for better downstream RAG performance.
    """

    if not text:
        return ""
    
    # Fix hyphenated words across lines ( "inter-\nnational")
    text = re.sub(r"-\s*\n\s*", "", text)

    # Replace single newlines inside sentences with space
    text = re.sub(r"(?<!\n)\n(?!\n)", " ", text)

    # Reduce multiple newlines to max 2 (paragraph separation)
    text = re.sub(r"\n{2,}", "\n\n", text)

    # Normalize spaces/tabs
    text = re.sub(r"[ \t]+", " ", text)
    
    return text.strip()



def read_pdf(file_path: str )->list[dict]:
    """
    Read a PDF and return structured page-level data.
    """
    file_path=Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"File not found :{file_path}")

    if not file_path.is_file():
        raise ValueError(f" Path is not a file :{file_path}")
    
    if file_path.suffix.lower() != ".pdf":
        raise ValueError(f" Path is not a PDF:{file_path}")
    pages_data=[]

    #Name of the file
    file_name=file_path.name

    #create a reader 
    reader=PdfReader(file_path)

    #loop through the pages 
    for i,page in  enumerate(reader.pages):
        #Extract text
        raw_text=page.extract_text() or ""
        cleaned_text=clean_text(raw_text)

        if not  cleaned_text:
            continue

        #Build page record 
        page_record ={
            "source":file_name,
            "page_number": i+1,
            "text":cleaned_text,
            "document_id": f"{file_name}_p{i+1}"
        }

        #append to list 
        pages_data.append(page_record)
    return pages_data

def  read_all_pdfs(folder_path:str)->list[dict]:
    folder=Path(folder_path)

    if not folder.exists():
        raise FileNotFoundError(f"Folder not found :{folder_path}")
    if not folder.is_dir():
        raise ValueError(f"Path is not a folder: {folder_path}")
    
    all_pages=[]
    pdf_files = list(folder.glob("*.pdf"))

    if not pdf_files:
     raise ValueError("No PDF files found in folder")

    for pdf_file in pdf_files:
     try:
        pdf_pages=read_pdf(str(pdf_file))
        all_pages.extend(pdf_pages)
     except Exception as e:
         print(f"Skipping {pdf_file}: {e}")
         continue

    return all_pages

    



