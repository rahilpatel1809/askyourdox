import fitz
import easyocr
import numpy as np
from PIL import Image
from docx import Document
import tempfile

reader = easyocr.Reader(['en'], gpu=True)

def extract_from_pdf(file):
    text = ""
    with fitz.open(stream=file.read(), filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return text

def ocr_image(file):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        tmp.write(file.read())
        tmp_path = tmp.name
    image = Image.open(tmp_path)
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