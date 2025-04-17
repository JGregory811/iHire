from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import FileResponse, JSONResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from docx import Document
import uuid
import os
import openai

app = FastAPI()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Schemas
class ResumeRequest(BaseModel):
    resume: str
    template: str = "c-suite"

class PDFExportRequest(BaseModel):
    resume: str

class ATSCheckRequest(BaseModel):
    resume: str
    jobDescription: str

# Routes
@app.post("/generateDocx")
async def generate_docx(request: ResumeRequest):
    doc = Document()
    doc.add_paragraph(request.resume)
    filename = f"resume_{uuid.uuid4().hex}.docx"
    filepath = os.path.join("/tmp", filename)
    doc.save(filepath)
    return FileResponse(filepath, filename=filename, media_type="application/octet-stream")

@app.post("/generatePdf")
async def generate_pdf(req: PDFExportRequest):
    filename = f"resume_{uuid.uuid4().hex}.pdf"
    filepath = os.path.join("/tmp", filename)
    c = canvas.Canvas(filepath, pagesize=letter)
    text = c.beginText(40, 750)
    text.setFont("Helvetica", 11)
    for line in req.resume.split("\n"):
        text.textLine(line)
    c.drawText(text)
    c.save()
    return FileResponse(filepath, filename=filename, media_type="application/pdf")

@app.post("/checkATSCompliance")
async def check_ats_compliance(req: ATSCheckRequest):
    prompt = f"""
Act as an ATS Compliance Evaluator. You will receive a resume and a job description.

1. Score the resume out of 100 based on keyword match, structure, formatting, and clarity.
2. List missing or weak keywords from the job description.
3. Suggest improvements to pass ATS and appeal to a human recruiter.

Resume:
{req.resume}

Job Description:
{req.jobDescription}

Provide your answer in JSON format with fields: score, missingKeywords, suggestions.
"""
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    content = response.choices[0].message["content"]
    try:
        result = eval(content.strip())
    except Exception:
        result = {"error": "Could not parse GPT response. Raw output: " + content}
    return result
