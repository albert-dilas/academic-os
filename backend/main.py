from fastapi import FastAPI, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
import sqlite3
import uuid
from pydantic import BaseModel
from typing import List

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# DB SETUP
DB_PATH = "solutions.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS exams 
                 (id TEXT PRIMARY KEY, name TEXT, status TEXT, progress INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS questions 
                 (id TEXT PRIMARY KEY, exam_id TEXT, area TEXT, num INTEGER, 
                  enunciado TEXT, pasos TEXT, svg TEXT, rpta TEXT)''')
    conn.commit()
    conn.close()

init_db()

# SCHEMAS
class Exam(BaseModel):
    id: str
    name: str
    status: str
    progress: int

@app.get("/")
def read_root():
    return { "status": "ACADEMIC-OS Backend Online" }

@app.get("/exams", response_model=List[Exam])
def get_exams():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM exams")
    rows = c.fetchall()
    conn.close()
    return [{"id": r[0], "name": r[1], "status": r[2], "progress": r[3]} for r in rows]

@app.post("/upload")
async def upload_pdf(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    exam_id = str(uuid.uuid4())
    file_path = f"uploads/{exam_id}.pdf"
    os.makedirs("uploads", exist_ok=True)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO exams VALUES (?, ?, ?, ?)", (exam_id, file.filename, "processing", 0))
    conn.commit()
    conn.close()
    
    # Aquí iría la lógica del solver en segundo plano
    # background_tasks.add_task(run_solver, exam_id, file_path)
    
    return {"id": exam_id, "status": "uploaded"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
