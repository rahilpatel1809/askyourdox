import fitz  # PyMuPDF
import easyocr
import numpy as np
from PIL import Image
from docx import Document
import tempfile

# Initialize EasyOCR reader (fallbacks to CPU if GPU unavailable)
reader = easyocr.Reader(['en'], gpu=True)

def extract_from_pdf(file):
    file_bytes = file.read()
    text = ""

    with fitz.open(stream=file_bytes, filetype="pdf") as doc:
        for page in doc:
            page_text = page.get_text()
            if page_text.strip():
                text += page_text + "\n"
            else:
                # If no text, fallback to OCR via pixmap
                pix = page.get_pixmap(dpi=200)
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                img_np = np.array(img)
                results = reader.readtext(img_np, detail=0)
                text += " ".join(results) + "\n"

    return text or "No readable text found in PDF."

def ocr_image(file):
    image = Image.open(file)
    image_np = np.array(image)
    results = reader.readtext(image_np, detail=0)
    return " ".join(results)

def extract_from_docx(file):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
        tmp.write(file.read())
        tmp_path = tmp.name
    doc = Document(tmp_path)
    return "\n".join([para.text for para in doc.paragraphs])

def extract_text(file, filetype):
    file.seek(0)
    if filetype == "application/pdf":
        return extract_from_pdf(file)
    elif filetype in ["image/jpeg", "image/jpg", "image/png"]:
        return ocr_image(file)
    elif filetype == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        return extract_from_docx(file)
    elif filetype == "text/plain":
        return str(file.read(), "utf-8")
    else:
        return "Unsupported file type"