from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import FileResponse
from typing import List
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from docx import Document
import uuid
import os
import openai

app = FastAPI()
openai.api_key = os.getenv("OPENAI_API_KEY")

# === Request Schemas ===
class ResumeRequest(BaseModel):
    resume: str
    template: str = "c-suite"

class PDFExportRequest(BaseModel):
    resume: str

class ATSCheckRequest(BaseModel):
    resume: str
    jobDescription: str

class CreateEmbeddingRequest(BaseModel):
    input: str
    model: str = "text-embedding-ada-002"

class JobSearchRequest(BaseModel):
    title: str
    location: str = ""
    keywords: List[str] = []
    remote: bool = False

class TrackJobStatusRequest(BaseModel):
    title: str
    company: str
    stage: str
    appliedDate: str
    notes: str = ""

class GenerateStarStoryRequest(BaseModel):
    question: str
    experienceSummary: str

class BenchmarkSalaryRequest(BaseModel):
    title: str
    location: str
    level: str
    industry: str = ""

class LinkedInProfileRequest(BaseModel):
    profileSummary: str
    careerGoal: str = ""

class WeeklyGoalsRequest(BaseModel):
    currentStage: str = "applying"
    jobGoal: str = ""

# === ROUTES ===

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

@app.post("/createEmbedding")
async def create_embedding(req: CreateEmbeddingRequest):
    result = openai.Embedding.create(input=req.input, model=req.model)
    return result

@app.post("/jobSearch")
async def job_search(req: JobSearchRequest):
    return {
        "results": [
            {"title": req.title, "company": "Acme Corp", "location": req.location or "Remote", "remote": req.remote},
            {"title": req.title + " II", "company": "Beta Inc", "location": req.location or "Remote", "remote": req.remote}
        ]
    }

@app.post("/trackJobStatus")
async def track_job_status(req: TrackJobStatusRequest):
    return {"message": "Application logged", "data": req.dict()}

@app.post("/generateStarStory")
async def generate_star_story(req: GenerateStarStoryRequest):
    prompt = f"Create a STAR-format interview response to this question: {req.question}\nBased on this experience: {req.experienceSummary}"
    completion = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return {"response": completion.choices[0].message["content"]}

@app.post("/benchmarkSalary")
async def benchmark_salary(req: BenchmarkSalaryRequest):
    return {
        "title": req.title,
        "location": req.location,
        "estimatedSalary": "$85,000 - $115,000",
        "level": req.level,
        "source": "MockData"
    }

@app.post("/analyzeLinkedInProfile")
async def analyze_linkedin(req: LinkedInProfileRequest):
    prompt = f"Improve this LinkedIn profile summary to align with the goal '{req.careerGoal}': {req.profileSummary}"
    completion = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return {"optimizedSummary": completion.choices[0].message["content"]}

@app.post("/generateWeeklyGoals")
async def generate_weekly_goals(req: WeeklyGoalsRequest):
    plan = {
        "exploring": ["Identify 5 job titles", "Research 3 companies", "Update resume"],
        "applying": ["Apply to 5 jobs", "Customize resume for each", "Follow up on past apps"],
        "interviewing": ["Practice 3 STAR stories", "Research 2 companies", "Mock interview"],
        "negotiating": ["Review market salary", "List negotiables", "Prepare 3 counterpoints"]
    }
    return {"weeklyPlan": plan.get(req.currentStage, [])}
