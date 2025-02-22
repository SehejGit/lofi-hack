import argparse
from transformers import pipeline, AutoProcessor, MusicgenForConditionalGeneration
import scipy.io.wavfile
from IPython.display import Audio

def generate_audio(query):
    # Initialize the pipeline
    synthesiser = pipeline("text-to-audio", model="facebook/musicgen-small")

    # Generate music
    music = synthesiser(query, forward_params={"do_sample": True})

    # Save the audio to a file
    scipy.io.wavfile.write("musicgen_out.wav", rate=music["sampling_rate"], data=music["audio"])

    # Load the model for conditional generation
    processor = AutoProcessor.from_pretrained("facebook/musicgen-small")
    model = MusicgenForConditionalGeneration.from_pretrained("facebook/musicgen-small")

    # Process the input text
    inputs = processor(
        text=[query],
        padding=True,
        return_tensors="pt",
    )

    # Generate audio values
    audio_values = model.generate(**inputs, max_new_tokens=256)

    # Get the sampling rate
    sampling_rate = model.config.audio_encoder.sampling_rate

    # Return the audio object
    return Audio(audio_values[0].numpy(), rate=sampling_rate)

def main():
    parser = argparse.ArgumentParser(description="Generate audio from text query.")
    parser.add_argument("query", type=str, help="The text query to generate audio from.")
    args = parser.parse_args()

    audio = generate_audio(args.query)
    print("Audio generated and saved as 'musicgen_out.wav'.")

if __name__ == "__main__":
    main()