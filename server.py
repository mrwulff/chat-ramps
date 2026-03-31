from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse
import shutil, subprocess, uuid, os

app = FastAPI()
BLENDER = r"C:\Program Files\Blender Foundation\Blender 5.1\blender.exe"


@app.get("/")
def root():
    return FileResponse("index.html")


@app.post("/generate")
async def generate(
    layout: UploadFile = File(...),
    heightA: float = Form(1),
    heightB: float = Form(1),
    colorA: str = Form("#ffffff"),
    colorB: str = Form("#cccccc"),
):
    job = str(uuid.uuid4())
    os.makedirs("jobs", exist_ok=True)

    layout_path = f"jobs/{job}.svg"
    out_path = f"jobs/{job}.stl"

    with open(layout_path, "wb") as f:
        shutil.copyfileobj(layout.file, f)

    cmd = [
        r"C:\Program Files\Blender Foundation\Blender 5.1\blender.exe",
        "-b",
        "template.blend",
        "-P",
        "apply_logo.py",
        "--",
        # files
        pathA,
        pathB,
        output_path,
        # LOGO A
        str(xA),
        str(yA),
        str(scaleA),
        str(rotA),
        str(heightA),
        str(colorA),
        # LOGO B
        str(xB),
        str(yB),
        str(scaleB),
        str(rotB),
        str(heightB),
        str(colorB),
    ]
    print(cmd)
    subprocess.run(cmd)

    return FileResponse(out_path)
