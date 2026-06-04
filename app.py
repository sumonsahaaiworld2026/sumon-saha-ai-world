from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from rembg import remove, new_session
from PIL import Image, ImageFilter

import os
import uuid
import io
import asyncio

# =========================
# CONFIG
# =========================

MAX_SIZE = 1200
semaphore = asyncio.Semaphore(1)

# =========================
# APP SETUP
# =========================

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://snazzy-snickerdoodle-8d6c74.netlify.app",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# =========================
# STORAGE (Railway-safe)
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

    print("Loading U2Net model...")
    session = new_session("u2net_human_seg")
    print("Model loaded successfully.")


# =========================
# HEALTH CHECK
# =========================

@app.get("/")
def root():
    return {"status": "running"}


# =========================
# REMOVE BACKGROUND API
# =========================

@app.post("/remove-bg")
async def remove_bg(file: UploadFile = File(...)):
    async with semaphore:

        file_id = str(uuid.uuid4())
        output_path = os.path.join(
            OUTPUT_FOLDER,
            f"{file_id}.png"
        )

        # Read uploaded file
        input_bytes = await file.read()

        # Open image
        image = Image.open(
            io.BytesIO(input_bytes)
        ).convert("RGBA")

        # Downscale large images
        image.thumbnail((MAX_SIZE, MAX_SIZE))

        # Convert PIL image to bytes
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        image_bytes = buffer.getvalue()

        # Remove background
        output_bytes = remove(
            image_bytes,
            session=session,
            alpha_matting=False
        )

        # Convert result back to PIL image
        output_image = Image.open(
            io.BytesIO(output_bytes)
        ).convert("RGBA")

        # Optional edge smoothing
        alpha = output_image.getchannel("A")
        alpha = alpha.filter(
            ImageFilter.GaussianBlur(1)
        )
        output_image.putalpha(alpha)

        # Save result
        output_image.save(output_path)

        return FileResponse(
            output_path,
            media_type="image/png",
            filename="output.png"
        )


# =========================
# LOCAL DEVELOPMENT
# =========================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8080,
        reload=True
    )
