from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import Response, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from io import BytesIO
import traceback
import os
from fastapi.responses import FileResponse
import uuid
from pathlib import Path

# Import image generation
from .image_generation import generate_image

# Import query manager for semantic search
from .query import AudioQueryManager

# Import word suggestions
from .enhancements import suggest_better_words

# Initialize global audio query manager
audio_query_manager = AudioQueryManager()

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
@app.options("/api/suggest-words")
async def options_handler():
    return Response(status_code=200)

@app.post("/api/suggest-words")
async def suggest_words_endpoint(request: PromptRequest):
    try:
        suggestions = suggest_better_words(request.prompt, top_n=3)
        return JSONResponse(content={"suggestions": suggestions[:3]})
    except Exception as e:
        print(f"Error in suggest_words: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

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

@app.post("/api/generate-music")
async def generate_music_endpoint(request: PromptRequest):
    try:
        print(f"Received music prompt: {request.prompt}")
        
        # Perform semantic search to find most similar existing track
        search_results = audio_query_manager.semantic_search(request.prompt, n_results=1)
        
        if not search_results:
            raise HTTPException(status_code=404, detail="No similar audio found")
        
        # Get the most similar track's details
        most_similar_track = search_results[0]
        
        # Create a URL endpoint for the audio file
        audio_endpoint = f"/api/audio/{os.path.basename(most_similar_track['local_audio_path'])}"
        
        # Return track metadata with the endpoint URL
        return JSONResponse(content={
            "prompt": most_similar_track['prompt'],
            "audio_url": audio_endpoint,
            "distance": most_similar_track.get('distance')
        })

    except Exception as e:
        print(f"Error in generate_music endpoint: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/audio/{filename}")
async def get_audio(filename: str):
    try:
        # Use the correct audio directory path
        audio_dir = Path("downloaded_audio")  # Changed from "audio" to "downloaded_audio"
        audio_path = audio_dir / filename
        
        print(f"Attempting to serve audio from: {audio_path}")
        print(f"File exists: {audio_path.exists()}")
        
        if not audio_path.exists():
            raise HTTPException(status_code=404, detail=f"Audio file not found at {audio_path}")
            
        return FileResponse(
            str(audio_path),
            media_type="audio/mpeg",
            headers={
                "Accept-Ranges": "bytes",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, HEAD, OPTIONS",
                "Access-Control-Allow-Headers": "*"
            }
        )
    except Exception as e:
        print(f"Error serving audio: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))