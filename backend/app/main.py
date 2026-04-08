import os
import tempfile
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask

from backend.app.converters.pdf_to_word.no_ocr import pdf_to_word_no_ocr
from backend.app.converters.pdf_to_word.ocr import HAS_OCR, pdf_to_word_ocr

app = FastAPI(title="PDF to Word Converter API", description="Minimal file-based converter")

def cleanup_files(files):
    for f in files:
        if os.path.exists(f):
            try:
                os.remove(f)
            except Exception:
                pass

@app.post("/convert")
async def convert_pdf(file: UploadFile = File(...), use_ocr: bool = Form(False)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
        
    if use_ocr and not HAS_OCR:
        raise HTTPException(status_code=500, detail="OCR is requested but pytesseract is not installed.")

    # Create temporary files for input and output
    fd_in, in_path = tempfile.mkstemp(suffix=".pdf")
    fd_out, out_path = tempfile.mkstemp(suffix=".docx")
    
    os.close(fd_in)
    os.close(fd_out)
    
    try:
        content = await file.read()
        with open(in_path, "wb") as f:
            f.write(content)
            
        if use_ocr:
            pdf_to_word_ocr(in_path, out_path)
        else:
            pdf_to_word_no_ocr(in_path, out_path)
            
        out_filename = file.filename.rsplit(".", 1)[0] + ".docx"
        
        return FileResponse(
            out_path, 
            filename=out_filename,
            background=BackgroundTask(cleanup_files, [in_path, out_path])
        )
    except Exception as e:
        cleanup_files([in_path, out_path])
        raise HTTPException(status_code=500, detail=str(e))
