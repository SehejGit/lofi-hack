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
        
        # Get the most similar track's local path
        most_similar_track = search_results[0]['local_audio_path']
        
        # Read the audio file
        with open(most_similar_track, 'rb') as audio_file:
            audio_bytes = audio_file.read()
        
        # Optional: Generate a unique filename for tracking/caching
        filename = f"lofi_track_{uuid.uuid4()}.mp3"
        
        # Play the audio track
        audio_query_manager.play_audio(most_similar_track)
        
        return Response(content=audio_bytes, media_type="audio/mpeg", headers={
            "X-Track-Prompt": search_results[0]['prompt'],
            "X-Track-Path": most_similar_track
        })
    except Exception as e:
        print(f"Error in generate_music endpoint: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

# Add endpoint for playback control
@app.post("/api/audio/control")
async def audio_control_endpoint(request: Request):
    try:
        control_data = await request.json()
        action = control_data.get('action')
        
        if action == 'stop':
            audio_query_manager.stop_audio()
        elif action == 'pause':
            audio_query_manager.pause_audio()
        elif action == 'resume':
            audio_query_manager.resume_audio()
        else:
            raise HTTPException(status_code=400, detail="Invalid audio control action")
        
        return JSONResponse(content={"status": "success"})
    except Exception as e:
        print(f"Error in audio control: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Add endpoint to get current track information
@app.get("/api/audio/current")
async def get_current_track():
    try:
        if audio_query_manager.current_track:
            return JSONResponse(content={
                "is_playing": audio_query_manager.is_playing,
                "current_track": audio_query_manager.current_track
            })
        else:
            return JSONResponse(content={
                "is_playing": False,
                "current_track": None
            })
    except Exception as e:
        print(f"Error getting current track: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))