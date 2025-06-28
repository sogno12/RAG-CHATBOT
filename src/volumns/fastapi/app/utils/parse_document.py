# src/volumns/fastapi/utils/parse_document.py

from typing import Literal
from fastapi import UploadFile
from bs4 import BeautifulSoup
import docx
import fitz  # PyMuPDF
import requests

async def extract_text_from_txt(file: UploadFile) -> str:
    return (await file.read()).decode("utf-8")

async def extract_text_from_pdf(file: UploadFile) -> str:
    content = ""
    with fitz.open(stream=await file.read(), filetype="pdf") as doc:
        for page in doc:
            content += page.get_text()
    return content

async def extract_text_from_docx(file: UploadFile) -> str:
    content = ""
    file_data = await file.read()
    with open("/tmp/temp.docx", "wb") as f:
        f.write(file_data)
    doc = docx.Document("/tmp/temp.docx")
    content = "\n".join([para.text for para in doc.paragraphs])
    return content

def extract_text_from_url(url: str) -> str:
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    for tag in soup(["script", "style"]):
        tag.decompose()
    return soup.get_text(separator="\n")
