# utils/chunking.py
from langchain.text_splitter import RecursiveCharacterTextSplitter
from config import settings

def chunk_text(text: str, chunk_size: int = None, chunk_overlap: int = None):
    """
    Splits a string into overlapping, token-safe chunks.

    Args:
        text (str): The input text to split.
        chunk_size (int, optional): Maximum token size per chunk.
        chunk_overlap (int, optional): Number of tokens to overlap between chunks.

    Returns:
        list[str]: List of chunked strings.
    """
    if not text:
        return []

    chunk_size = chunk_size or settings.CHUNK_SIZE
    chunk_overlap = chunk_overlap or settings.CHUNK_OVERLAP

    splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        model_name=settings.OPENAI_MODEL,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    return splitter.split_text(text)


def chunk_and_process(text: str, processor_fn, **processor_kwargs):
    """
    Chunks text and applies a processing function to each chunk.

    Args:
        text (str): The text to chunk.
        processor_fn (Callable): Function to process each chunk.
        **processor_kwargs: Extra args to processor_fn.

    Returns:
        str: Concatenation of all processed chunk outputs.
    """
    chunks = chunk_text(text)
    results = []

    for idx, chunk in enumerate(chunks, start=1):
        print(f"[Chunking] Processing chunk {idx}/{len(chunks)} ({len(chunk)} chars)")
        try:
            processed = processor_fn(chunk, **processor_kwargs)
            results.append(processed)
        except Exception as e:
            print(f"[Chunking] ERROR processing chunk {idx}: {e}")
            results.append(f"(Error in chunk {idx}: {e})")

    return "\n".join(results)