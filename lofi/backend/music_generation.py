from huggingface_hub import HfApi, hf_hub_download
import os
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import logging
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LofiMusicGenerator:
    def __init__(self):
        self.model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        self.api = HfApi()
        self.static_prompts = []
        self.dynamic_prompts = []
        self.prompt_embeddings = None
        self._load_dataset()

    def _load_dataset(self):
        """Load and cache the dataset prompts"""
        try:
            # Load a few static prompt files for quick testing
            # In production, you'd want to load all files
            static_file = hf_hub_download(
                repo_id="vikhyatk/lofi",
                filename="data/static-prompts-022ecf03-24a6-4b73-a2bf-063928125f48.parquet",
                repo_type="dataset"
            )
            
            # Load static prompts
            df_static = pd.read_parquet(static_file)
            self.static_prompts = df_static['prompt'].tolist()
            
            # Create embeddings
            logger.info(f"Creating embeddings for {len(self.static_prompts)} prompts")
            self.prompt_embeddings = self.model.encode(self.static_prompts)
            
        except Exception as e:
            logger.error(f"Error loading dataset: {str(e)}")
            raise

    def find_closest_match(self, prompt):
        """Find the closest matching prompt in the dataset"""
        try:
            # Generate embedding for input prompt
            prompt_embedding = self.model.encode([prompt])[0]
            
            # Reshape for sklearn
            prompt_embedding = prompt_embedding.reshape(1, -1)
            
            # Calculate similarities
            similarities = cosine_similarity(
                prompt_embedding,
                self.prompt_embeddings
            )[0]
            
            # Get best match
            best_match_idx = np.argmax(similarities)
            best_match_score = similarities[best_match_idx]
            matched_prompt = self.static_prompts[best_match_idx]
            
            logger.info(f"Best match score: {best_match_score}")
            logger.info(f"Matched prompt: {matched_prompt}")
            
            # For now, return a standard filename since we need to map between prompts and audio files
            return {
                'file_path': 'lofi_track_001.mp3',  # This would come from your prompt-to-audio mapping
                'prompt': matched_prompt,
                'score': best_match_score
            }
            
        except Exception as e:
            logger.error(f"Error finding match: {str(e)}")
            raise

    def get_audio(self, file_path):
        """Get the audio file from the dataset"""
        try:
            # For now, return a dummy audio buffer since we need the actual audio files
            # In production, this would download and return the actual audio file
            logger.info(f"Would fetch audio file: {file_path}")
            return bytes([0] * 44100)  # 1 second of silence as dummy data
                
        except Exception as e:
            logger.error(f"Error getting audio: {str(e)}")
            raise

# Global instance
generator = LofiMusicGenerator()

def generate_music(prompt):
    """Main function to generate/retrieve music based on prompt"""
    try:
        logger.info(f"Processing prompt: {prompt}")
        
        # Find best matching track
        match = generator.find_closest_match(prompt)
        logger.info(f"Found matching track: {match['file_path']}")
        
        # Get the audio data
        audio_data = generator.get_audio(match['file_path'])
        logger.info(f"Retrieved audio data: {len(audio_data)} bytes")
        
        return audio_data
        
    except Exception as e:
        logger.error(f"Error in generate_music: {str(e)}")
        raise