from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import subprocess
import uuid
import os
from fastapi import Form
import shutil

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

BLENDER = r"C:\Program Files\Blender Foundation\Blender 5.1\blender.exe"
WORK_DIR = "jobs"
os.makedirs(WORK_DIR, exist_ok=True)


@app.get("/", response_class=HTMLResponse)
def home():
    with open("index.html", "r") as f:
        return f.read()


@app.post("/generate")
async def generate(
    fileA: UploadFile = File(...),
    fileB: UploadFile = File(None),
    xA: float = Form(0),
    yA: float = Form(0),
    scaleA: float = Form(20),
    rotA: float = Form(0),
    heightA: float = Form(0.8),
    xB: float = Form(0),
    yB: float = Form(0),
    scaleB: float = Form(20),
    rotB: float = Form(0),
    heightB: float = Form(1.6),
):
    job_id = str(uuid.uuid4())
    os.makedirs("jobs", exist_ok=True)

    pathA = f"jobs/{job_id}_A.svg"
    pathB = f"jobs/{job_id}_B.svg"
    out_path = f"jobs/{job_id}.stl"

    with open(pathA, "wb") as f:
        shutil.copyfileobj(fileA.file, f)

    if fileB:
        with open(pathB, "wb") as f:
            shutil.copyfileobj(fileB.file, f)

    cmd = [
        BLENDER,
        "-b",
        "template.blend",
        "-P",
        "apply_logo.py",
        "--",
        pathA,
        pathB,
        out_path,
        str(xA),
        str(yA),
        str(scaleA),
        str(rotA),
        str(heightA),
        str(xB),
        str(yB),
        str(scaleB),
        str(rotB),
        str(heightB),
    ]

    print("CMD:", cmd)

    subprocess.run(cmd)

    return FileResponse(out_path, media_type="application/octet-stream")
