from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from rembg import remove, new_session
from PIL import Image, ImageFilter

import os
import uuid
import io

port = int(os.environ.get("PORT", 8000))

# =========================
# APP SETUP
# =========================

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# FOLDERS
# =========================

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# =========================
# LOAD MODEL (ONCE ONLY)
# =========================

session = new_session("birefnet-general")

# =========================
# API ENDPOINT
# =========================

@app.post("/remove-bg")
async def remove_bg(file: UploadFile = File(...)):

    file_id = str(uuid.uuid4())

    output_path = f"{OUTPUT_FOLDER}/{file_id}.png"

    # =========================
    # READ IMAGE
    # =========================

    input_bytes = await file.read()

    image = Image.open(io.BytesIO(input_bytes)).convert("RGBA")

    # =========================
    # REMOVE BACKGROUND
    # =========================

    output_image = remove(
        image,
        session=session,
        alpha_matting=True,
        alpha_matting_foreground_threshold=240,
        alpha_matting_background_threshold=10,
        alpha_matting_erode_size=10
    )

    # =========================
    # EDGE SMOOTHING
    # =========================

    alpha = output_image.getchannel("A")
    alpha = alpha.filter(ImageFilter.GaussianBlur(1))
    output_image.putalpha(alpha)

    # =========================
    # SAVE OUTPUT
    # =========================

    output_image.save(output_path)

    return FileResponse(
        output_path,
        media_type="image/png",
        filename="output.png"
    )
