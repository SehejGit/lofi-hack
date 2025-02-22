from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import Response, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from io import BytesIO
import traceback
import os
import uuid

# Import image generation
from .image_generation import generate_image

# Import query manager for semantic search
from .query import AudioQueryManager

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

@app.post("/api/generate-music")
async def generate_music_endpoint(request: PromptRequest):
    try:
        print(f"Received music prompt: {request.prompt}")
        
        # Perform semantic search to find most similar existing track
        search_results = audio_query_manager.semantic_search(request.prompt, n_results=1, play_most_similar=False)
        
        if not search_results:
            raise HTTPException(status_code=404, detail="No similar audio found")
        
        # Get the most similar track's details
        most_similar_track = search_results[0]
        
        # Return track metadata
        return JSONResponse(content={
            "prompt": most_similar_track['prompt'],
            "local_audio_path": most_similar_track['local_audio_path'],
            "audio_url": most_similar_track.get('audio_url', ''),
            "distance": most_similar_track.get('distance')
        })
    except Exception as e:
        print(f"Error in generate_music endpoint: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))