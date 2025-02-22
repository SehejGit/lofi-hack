from huggingface_hub import InferenceClient
import os


def generate_image(prompt):
    client = InferenceClient(api_key=os.getenv("HF_API_KEY"))

    image = client.text_to_image(
        prompt,
        model="alvdansen/lofi-cuties"
    )
    return image
