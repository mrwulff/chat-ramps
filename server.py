from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import FileResponse
import shutil, subprocess, uuid, os

app = FastAPI()


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
        "blender",
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
