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

@app.options(\"/api/generate-image\")\n@app.options(\"/api/generate-music\")\nasync def options_handler():\n    return Response(status_code=200)

@app.post(\"/api/generate-image\")\nasync def generate_image_endpoint(request: PromptRequest):\n    try:\n        image = generate_image(request.prompt)\n        img_byte_arr = BytesIO()\n        image.save(img_byte_arr, format='PNG')\n        img_byte_arr = img_byte_arr.getvalue()\n        return Response(content=img_byte_arr, media_type=\"image/png\")\n    except Exception as e:\n        print(f\"Error in generate_image: {str(e)}\")\n        print(traceback.format_exc())  # Print full traceback\n        raise HTTPException(status_code=500, detail=str(e))

@app.post(\"/api/generate-music\")\nasync def generate_music_endpoint(request: PromptRequest):\n    try:\n        print(f\"Received music prompt: {request.prompt}\")\n        \n        # Perform semantic search to find most similar existing track\n        search_results = audio_query_manager.semantic_search(request.prompt, n_results=1, play_most_similar=False)\n        \n        if not search_results:\n            raise HTTPException(status_code=404, detail=\"No similar audio found\")\n        \n        # Get the most similar track's local path\n        most_similar_track = search_results[0]['local_audio_path']\n        \n        # Read the audio file\n        with open(most_similar_track, 'rb') as audio_file:\n            audio_bytes = audio_file.read()\n        \n        # Optional: Generate a unique filename for tracking/caching\n        filename = f\"lofi_track_{uuid.uuid4()}.mp3\"\n        \n        # Play the audio track\n        audio_query_manager.play_audio(most_similar_track)\n        \n        return Response(content=audio_bytes, media_type=\"audio/mpeg\", headers={\n            \"X-Track-Prompt\": search_results[0]['prompt'],\n            \"X-Track-Path\": most_similar_track\n        })\n    except Exception as e:\n        print(f\"Error in generate_music endpoint: {str(e)}\")\n        print(traceback.format_exc())\n        raise HTTPException(status_code=500, detail=str(e))

# Add endpoint for playback control
@app.post(\"/api/audio/control\")\nasync def audio_control_endpoint(request: Request):\n    try:\n        control_data = await request.json()\n        action = control_data.get('action')\n        \n        if action == 'stop':\n            audio_query_manager.stop_audio()\n        elif action == 'pause':\n            audio_query_manager.pause_audio()\n        elif action == 'resume':\n            audio_query_manager.resume_audio()\n        else:\n            raise HTTPException(status_code=400, detail=\"Invalid audio control action\")\n        \n        return JSONResponse(content={\"status\": \"success\"})\n    except Exception as e:\n        print(f\"Error in audio control: {str(e)}\")\n        raise HTTPException(status_code=500, detail=str(e))

# Add endpoint to get current track information
@app.get(\"/api/audio/current\")\nasync def get_current_track():\n    try:\n        if audio_query_manager.current_track:\n            return JSONResponse(content={\n                \"is_playing\": audio_query_manager.is_playing,\n                \"current_track\": audio_query_manager.current_track\n            })\n        else:\n            return JSONResponse(content={\n                \"is_playing\": False,\n                \"current_track\": None\n            })\n    except Exception as e:\n        print(f\"Error getting current track: {str(e)}\")\n        raise HTTPException(status_code=500, detail=str(e))