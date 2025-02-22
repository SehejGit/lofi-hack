from huggingface_hub import InferenceClient
import os


def generate_image(prompt):
    client = InferenceClient(api_key=os.getenv("HF_API_KEY"))

    # Modify the prompt to include pixelated, lofi, and vaporwave aesthetics
    modified_prompt = f"Calm, Peaceful, Pixelated, lofi, vaporwave aesthetic: {prompt}"
    
    image = client.text_to_image(
        modified_prompt,
        model="stabilityai/stable-diffusion-3.5-large-turbo"
    )
    return image
