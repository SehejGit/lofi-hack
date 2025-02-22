from huggingface_hub import InferenceClient

client = InferenceClient(
	api_key="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"
)

# output is a PIL.Image object
image = client.text_to_image(
	"Girl playing with her cats",
	model="alvdansen/lofi-cuties"
)

image.show()