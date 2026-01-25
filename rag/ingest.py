from typing import List, Tuple, Any, Dict
from .utils import clean_text, chunk_text
from pathlib import Path
from pypdf import PdfReader
from .config import settings

supportedFileTypes = ['.pdf']





# PDF Text Extraction
def extract_text_from_pdf(path: Path) -> str:
    reader = PdfReader(str(path))
    pages = []

    for page in reader.pages:
        try:
            pages.append(page.extract_text() or "")
        except Exception:
            pages.append("")

    return "\n\n".join(pages)

# Build Chunks by Page
def build_chunks_by_page(path: Path) -> Tuple[List[str], List[Dict[str, Any]]]:
    reader = PdfReader(str(path))

    all_chunks: List[str] = []
    all_metadatas: List[Dict[str, Any]] = []

    for page_index, page in enumerate(reader.pages):
        raw_page = page.extract_text() or ""
        cleaned_page = clean_text(raw_page)

        page_chunks = chunk_text(   
            cleaned_page,
            chunk_size= settings.chunk_size,
            chunk_overlap= settings.chunk_overlap,
        )

        for chunk_index, chunk in enumerate(page_chunks):  
            all_chunks.append(chunk)
            all_metadatas.append({
                "source": path.name,
                "path": str(path),
                "page_number": page_index + 1,
                "chunk_index": chunk_index,
                "file_ext": ".pdf",
            })

    return all_chunks, all_metadatas

def build_chunks_for_file(path: Path) -> Tuple[List[str], List[Dict[str, Any]]]:
    return build_chunks_by_page(path)



# THIS IS WHERE YOU ADD THE PATH + RUN THE CODE
if __name__ == "__main__":
    # PDF in same folder as this file
    pdf_path = Path("./ShubhamSarpalResume.pdf")

    print("📄 PDF Path:", pdf_path)

    if not pdf_path.exists():
        print("PDF file not found. Check the file name and location.")
        exit()

    # Extract raw text (quick test)
    text = extract_text_from_pdf(pdf_path)
    print("✅ Extracted characters:", len(text))
    print("\n--- First 500 chars of PDF text ---\n")
    print(text[:500])

    # Build chunks
    chunks, metadatas = build_chunks_by_page(pdf_path)
    print("\nTotal chunks:", len(chunks))
    print("Total metadata rows:", len(metadatas))

    if len(chunks) > 0:
        print("\n--- First chunk preview ---\n")
        print(chunks[0][:500])

        print("\n--- First chunk metadata ---\n")
        print(metadatas[0])