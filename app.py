from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from rembg import remove, new_session
from PIL import Image, ImageFilter

import os
import uuid
import io
import asyncio
import gc

semaphore = asyncio.Semaphore(1)

MAX_SIZE = 1200

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
# FOLDERS (Render-safe)
# =========================

UPLOAD_FOLDER = "/tmp/uploads"
OUTPUT_FOLDER = "/tmp/outputs"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# =========================
# LOAD MODEL ONCE
# =========================

session = None

@app.on_event("startup")
def load_model():
    global session
    session = new_session("u2net_human_seg")

# =========================
# API
# =========================

@app.post("/remove-bg")
async def remove_bg(file: UploadFile = File(...)):
    async with semaphore:
        file_id = str(uuid.uuid4())
        output_path = f"{OUTPUT_FOLDER}/{file_id}.png"
    
        input_bytes = await file.read()
        image = Image.open(io.BytesIO(input_bytes)).convert("RGBA")
    
        # upscale before processing
        # image = image.resize((image.width * 2, image.height * 2))
    
        # Downscale large images
        image.thumbnail((MAX_SIZE, MAX_SIZE))

        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
    
        output_image = remove(
            image,
            session=session,
            alpha_matting=False
        )

        output_image = Image.open(io.BytesIO(output_bytes)).convert("RGBA")
    
        # downscale back
        # output_image = output_image.resize(
        #     (output_image.width // 2, output_image.height // 2)
        # )
    
        # smooth edges
        alpha = output_image.getchannel("A")
        alpha = alpha.filter(ImageFilter.GaussianBlur(1))
        output_image.putalpha(alpha)
    
        output_image.save(output_path)
    
        return FileResponse(
            output_path,
            media_type="image/png",
            filename="output.png"
        )
