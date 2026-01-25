import re       


## Text Cleaning Utility

def clean_text(text: str) -> str:
    """Cleans the input text by removing extra whitespace and special characters."""
    text = text.replace('\u00a0', ' ')  # Replace newlines with space
    text = re.sub(r'\t', ' ', text)  # Replace multiple newlines with single space
    text = re.sub(r"\n{3,}", "\n\n", text)  
    return text.strip()

## Text Chunking Utility

def chunk_text(text: str, chunk_size: int, chunk_overlap: int) :
    step = max(1, chunk_size - chunk_overlap)
    n = len(text)
    chunks = []

#   Generate chunks with specified size and overlap
    for i in range(0, n, step): 
        end = min(i + chunk_size, n) 

        if i < n:
         # try to cut on a whitespace boundary
            cut = text.rfind(" ", i, end)
        if cut != -1 and cut > i + 50:
            end = cut

        chunks.append(text[i:end])

        return chunks
    
# Clean Snippet Utility 
def safe_snipet(text: str, max_length: int) -> str:
    """Returns a safe snippet of the text up to max_length without cutting words."""
    if len(text) <= max_length:
        return text
    cut = text.rfind(" ", 0, max_length)
    if cut != -1 and cut > 50:
        end = cut
    return text[:end].strip()



