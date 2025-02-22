from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from io import BytesIO
from .image_generation import generate_image

app = FastAPI()


class PromptRequest(BaseModel):
    prompt: str


@app.post("/api/generate-image")
async def generate_image_endpoint(request: PromptRequest):
    try:
        # Generate the image
        image = generate_image(request.prompt)
        
        # Convert PIL Image to bytes
        img_byte_arr = BytesIO()
        image.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        
        # Return the image
        return Response(content=img_byte_arr, media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
