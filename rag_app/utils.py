import fitz  # PyMuPDF
import easyocr
import numpy as np
from PIL import Image
from docx import Document
import tempfile
from pdf2image import convert_from_bytes

reader = easyocr.Reader(['en'], gpu=True)

def extract_from_pdf(file):
    try:
        file_bytes = file.read()
        if not file_bytes:
            return "Empty file. Please upload a valid PDF."

        with fitz.open(stream=file_bytes, filetype="pdf") as doc:
            if len(doc) == 0:
                return "PDF has no pages or is encrypted."

            text = ""
            for page in doc:
                try:
                    page_text = page.get_text()
                    if page_text.strip():
                        text += page_text + "\n"
                    else:
                        pix = page.get_pixmap(dpi=200)
                        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                        img_np = np.array(img)
                        results = reader.readtext(img_np, detail=0)
                        text += " ".join(results) + "\n"
                except Exception as page_err:
                    text += f"\n[Error reading page {page.number + 1}] "

            return text.strip() or "No readable text found in PDF."

    except Exception as e:
        return f"Error opening PDF: {str(e)}"

def ocr_image(file):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
            tmp.write(file.read())
            tmp_path = tmp.name

        image = Image.open(tmp_path)
        image_np = np.array(image)
        results = reader.readtext(image_np, detail=0)
        return " ".join(results)
    except Exception as e:
        return f"Error reading image: {str(e)}"

def extract_from_docx(file):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
            tmp.write(file.read())
            tmp_path = tmp.name

        doc = Document(tmp_path)
        return "\n".join([para.text for para in doc.paragraphs])
    except Exception as e:
        return f"Error reading DOCX: {str(e)}"

def extract_text(file, filetype):
    if filetype == "application/pdf":
        return extract_from_pdf(file)
    elif filetype in ["image/jpeg", "image/jpg", "image/png"]:
        return ocr_image(file)
    elif filetype == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        return extract_from_docx(file)
    elif filetype == "text/plain":
        try:
            return str(file.read(), "utf-8")
        except Exception as e:
            return f"Error reading TXT: {str(e)}"
    else:
        return "Unsupported file type."