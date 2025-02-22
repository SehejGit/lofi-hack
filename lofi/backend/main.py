from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import Response, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from io import BytesIO
import traceback
from .image_generation import generate_image
from .music_generation import generate_music

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

class PromptRequest(BaseModel):
    prompt: str

@app.options("/api/generate-image")
@app.options("/api/generate-music")
async def options_handler():
    return Response(status_code=200)

@app.post("/api/generate-image")
async def generate_image_endpoint(request: PromptRequest):
    try:
        image = generate_image(request.prompt)
        img_byte_arr = BytesIO()
        image.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        return Response(content=img_byte_arr, media_type="image/png")
    except Exception as e:
        print(f"Error in generate_image: {str(e)}")
        print(traceback.format_exc())  # Print full traceback
        raise HTTPException(status_code=500, detail=str(e))

# In main.py, modify the generate_music_endpoint:
@app.post("/api/generate-music")
async def generate_music_endpoint(request: PromptRequest):
    try:
        print(f"Received music prompt: {request.prompt}")
        audio_bytes = generate_music(request.prompt)
        
        if not audio_bytes:
            raise HTTPException(status_code=500, detail="No audio generated")
        
        # Set to MP3 as that's most common for lofi tracks
        return Response(content=audio_bytes, media_type="audio/mpeg")
    except Exception as e:
        print(f"Error in generate_music endpoint: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))