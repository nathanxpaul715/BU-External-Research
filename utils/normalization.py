# utils/normalization.py
import os
import docx2python
import mammoth
from pdfminer.high_level import extract_text as extract_pdf_text
from unstructured.partition.pdf import partition_pdf

# --- PATCH: safely import textract-py3 as textract ---
try:
    import textract  # if textract-py3 is installed, it registers as textract
except ImportError:
    try:
        import textract_py3 as textract  # just in case the fork installs under another name
    except ImportError:
        textract = None
        print("[Normalization] WARNING: textract/textract-py3 not installed — fallback extraction will be skipped.")

def normalize_docx(path: str) -> str:
    if not os.path.exists(path):
        raise FileNotFoundError(f"DOCX file not found: {path}")
    try:
        print(f"[Normalization] Using docx2python for {path}")
        parsed = docx2python.docx2python(path)
        return "\n".join(parsed.text)
    except Exception as e:
        print(f"[Normalization] docx2python failed: {e}")
        try:
            print(f"[Normalization] Fallback to mammoth for {path}")
            with open(path, "rb") as docx_file:
                result = mammoth.extract_raw_text(docx_file)
            return result.value
        except Exception as e2:
            raise RuntimeError(f"DOCX normalization failed: {e2}")

def normalize_pdf(path: str) -> str:
    if not os.path.exists(path):
        raise FileNotFoundError(f"PDF file not found: {path}")
    try:
        print(f"[Normalization] Using pdfminer.six for {path}")
        return extract_pdf_text(path)
    except Exception as e:
        print(f"[Normalization] pdfminer failed: {e}")
        try:
            print(f"[Normalization] Fallback to unstructured.partition.pdf for {path}")
            elements = partition_pdf(filename=path)
            return "\n".join(str(el) for el in elements)
        except Exception as e2:
            raise RuntimeError(f"PDF normalization failed: {e2}")

def normalize_any(path: str) -> str:
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")
    ext = os.path.splitext(path)[1].lower()
    try:
        if ext == ".docx":
            return normalize_docx(path)
        elif ext == ".pdf":
            return normalize_pdf(path)
        else:
            raise ValueError(f"Unsupported file format: {ext}")
    except Exception as e:
        print(f"[Normalization] Primary methods failed for {path}: {e}")
        if textract is not None:
            try:
                print(f"[Normalization] Trying textract fallback for {path}")
                text = textract.process(path)
                return text.decode("utf-8", errors="ignore")
            except Exception as e2:
                raise RuntimeError(f"Textract fallback failed for {path}: {e2}")
        else:
            raise RuntimeError("Textract fallback not available — install textract-py3 to enable.")