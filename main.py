from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import FileResponse, JSONResponse
from docx import Document
import uuid
import os
import openai

app = FastAPI()

openai.api_key = os.getenv("OPENAI_API_KEY")

# Request Schemas
class ResumeRequest(BaseModel):
    resume: str
    template: str = "c-suite"

class CreateEmbeddingRequest(BaseModel):
    input: str
    model: str = "text-embedding-ada-002"

class JobSearchRequest(BaseModel):
    title: str
    location: str = ""
    keywords: list[str] = []
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

# ROUTES

@app.post("/generateDocx")
async def generate_docx(request: ResumeRequest):
    doc = Document()
    doc.add_paragraph(request.resume)
    filename = f"resume_{uuid.uuid4().hex}.docx"
    filepath = os.path.join("/tmp", filename)
    doc.save(filepath)
    return FileResponse(filepath, filename=filename, media_type="application/octet-stream")

@app.post("/createEmbedding")
async def create_embedding(req: CreateEmbeddingRequest):
    result = openai.Embedding.create(input=req.input, model=req.model)
    return result

@app.post("/jobSearch")
async def job_search(req: JobSearchRequest):
    sample_jobs = [
        {"title": req.title, "company": "Acme Corp", "location": req.location or "Remote", "remote": req.remote},
        {"title": req.title + " II", "company": "Beta Inc", "location": req.location or "Remote", "remote": req.remote}
    ]
    return {"results": sample_jobs}

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
