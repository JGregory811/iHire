from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import FileResponse
from docx import Document
import uuid
import os

app = FastAPI()

class ResumeRequest(BaseModel):
    resume: str
    template: str = "c-suite"

@app.post("/generateDocx")
async def generate_docx(request: ResumeRequest):
    doc = Document()
    doc.add_paragraph(request.resume)
    filename = f"resume_{uuid.uuid4().hex}.docx"
    filepath = os.path.join("/tmp", filename)
    doc.save(filepath)
    return FileResponse(
        filepath,
        filename=filename,
        media_type="application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
