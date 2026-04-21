from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
import shutil

from scraper import CFScraper
from core import ProblemManager
from runner import CodeRunner

# Constants
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
# The project root is one level up from the backend directory
PROJECT_ROOT = os.path.dirname(ROOT_DIR)

app = FastAPI(title="my-codeforces Backend")
scraper = CFScraper()
manager = ProblemManager(PROJECT_ROOT)
runner = CodeRunner()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Data Models ---

class ProblemInit(BaseModel):
    problemId: str

class CodeSave(BaseModel):
    problemId: str
    version: str
    difficulty: str
    content: str

class RunRequest(BaseModel):
    code: str
    problemId: str
    difficulty: str

# --- Helpers ---

def get_template():
    template_path = os.path.join(PROJECT_ROOT, "template.py")
    if os.path.exists(template_path):
        with open(template_path, "r", encoding="utf-8") as f:
            return f.read()
    return "# Write your code here\n"

# --- Endpoints ---

@app.get("/api/history")
async def get_history():
    """Scan filesystem and return problem history."""
    return manager.scan_history()

@app.post("/api/init")
async def init_problem(problem: ProblemInit):
    """Initialize a problem, trigger scraper, and return initial data."""
    data = await scraper.fetch_problem(problem.problemId)
    if not data:
        raise HTTPException(status_code=404, detail="Problem not found or scraping failed")
    
    # Determine directory (default to 800 if rating is unknown)
    rating = data.get("rating", "800")
    difficulty = rating if rating.isdigit() else "800"
    
    target_dir = os.path.join(PROJECT_ROOT, difficulty)
    os.makedirs(target_dir, exist_ok=True)
    
    # Save YAML
    manager.save_yaml(difficulty, problem.problemId, data.get("samples", []))
    
    # Check if v1 already exists
    file_path = os.path.join(target_dir, f"{problem.problemId}_v1.py")
    exists = os.path.exists(file_path)
    
    content = ""
    if exists:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    else:
        # Create from template with metadata
        metadata = manager.write_metadata(data)
        content = metadata + "\n" + get_template()
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

    return {
        "status": "success",
        "data": {
            **data,
            "difficulty": difficulty,
            "content": content,
            "exists": exists,
            "path": file_path
        }
    }

@app.post("/api/save")
async def save_code(data: CodeSave):
    """Save/Auto-save editor content and record session."""
    target_dir = os.path.join(PROJECT_ROOT, data.difficulty)
    os.makedirs(target_dir, exist_ok=True)
    
    filename = f"{data.problemId}_{data.version}.py"
    file_path = os.path.join(target_dir, filename)
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(data.content)
    
    manager.save_last_session(data.problemId, data.difficulty, data.version)
        
    return {"status": "success", "path": file_path}

@app.get("/api/resume")
async def resume_session():
    """Return the last edited problem session."""
    session = manager.get_last_session()
    if not session:
        return {"session": None}
    return {"session": session}

@app.post("/api/clean")
async def get_cleaned_code(data: RunRequest):
    """Return cleaned code for submission."""
    cleaned = manager.clean_code(data.code)
    return {"cleanedCode": cleaned}

@app.post("/api/run")
async def run_test(data: RunRequest):
    """Run local python tests and return results."""
    samples = manager.get_yaml(data.difficulty, data.problemId)
    if not samples:
        return {"error": "No test cases found. Please add them manually."}
    
    work_dir = os.path.join(PROJECT_ROOT, data.difficulty)
    results = runner.run_all(data.code, samples, work_dir)
    
    return {"results": results}

@app.get("/api/problem/{difficulty}/{problem_id}/{version}")
async def get_problem_version(difficulty: str, problem_id: str, version: str):
    """Load a specific version of a problem."""
    file_path = os.path.join(PROJECT_ROOT, difficulty, f"{problem_id}_{version}.py")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    samples = manager.get_yaml(difficulty, problem_id)
    return {"content": content, "samples": samples}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
