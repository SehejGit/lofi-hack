import chromadb
from sentence_transformers import SentenceTransformer
import os
import pygame
import threading
import time

class AudioQueryManager:
    def __init__(self, db_path='./chroma_db', collection_name='audio'):
        """
        Initialize ChromaDB client and load the audio prompts collection.
        
        :param db_path: Path to ChromaDB storage
        :param collection_name: Name of the collection to query
        """
        # Initialize ChromaDB client
        self.chroma_client = chromadb.PersistentClient(path=db_path)
        
        # Load embedding model
        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
        
        # Get the collection
        self.collection = self.chroma_client.get_collection(name=collection_name)
        
        # Initialize pygame mixer for audio playback
        pygame.mixer.init()
        
        # Current playing track
        self.current_track = None
        self.playback_thread = None
        self.is_playing = False

    def semantic_search(self, query, n_results=5, play_most_similar=True):
        """
        Perform semantic search on audio prompts and optionally play the most similar track.
        
        :param query: Text query to search
        :param n_results: Number of results to return
        :param play_most_similar: Whether to automatically play the most similar track
        :return: List of matching audio files and their metadata
        """
        # Generate embedding for the query
        query_embedding = self.embedding_model.encode(query).tolist()
        
        # Perform semantic search
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        
        processed_results = self._process_query_results(results)
        
        # Play the most similar track if requested
        if play_most_similar and processed_results:
            self.play_audio(processed_results[0]['local_audio_path'])
        
        return processed_results

    def play_audio(self, audio_path):
        """
        Play an audio file, stopping any currently playing track.
        
        :param audio_path: Path to the audio file to play
        """
        # Stop any currently playing track
        self.stop_audio()
        
        # Check if file exists
        if not os.path.exists(audio_path):
            print(f"Error: Audio file not found at {audio_path}")
            return
        
        try:
            # Load and play the audio file
            pygame.mixer.music.load(audio_path)
            pygame.mixer.music.play()
            
            # Update current track and playing status
            self.current_track = audio_path
            self.is_playing = True
            
            # Start a thread to monitor playback
            self.playback_thread = threading.Thread(target=self._monitor_playback)
            self.playback_thread.start()
        except Exception as e:
            print(f"Error playing audio: {e}")

    def _monitor_playback(self):
        """
        Monitor audio playback and update status when track finishes.
        """
        while self.is_playing:
            # Check if music has stopped naturally
            if not pygame.mixer.music.get_busy():
                self.is_playing = False
                self.current_track = None
                break
            time.sleep(1)

    def stop_audio(self):
        """
        Stop currently playing audio.
        """
        if self.is_playing:
            pygame.mixer.music.stop()
            self.is_playing = False
            self.current_track = None

    def pause_audio(self):
        """
        Pause currently playing audio.
        """
        if self.is_playing:
            pygame.mixer.music.pause()

    def resume_audio(self):
        """
        Resume paused audio.
        """
        if self.current_track:
            pygame.mixer.music.unpause()

    # Rest of the existing methods remain the same (metadata_filter_search, _process_query_results, etc.)
    # ... [previous implementation of other methods]

def main():
    # Initialize AudioQueryManager
    query_manager = AudioQueryManager()
    
    # Interactive audio search and playback
    while True:
        # Get user input
        user_query = input("Enter a music description (or 'quit' to exit): ")
        
        # Exit condition
        if user_query.lower() == 'quit':
            break
        
        # Perform semantic search and play most similar track
        results = query_manager.semantic_search(user_query)
        
        # Print results
        print("\nTop matching tracks:")
        for i, result in enumerate(results, 1):
            print(f"{i}. Prompt: {result['prompt']}")
            print(f"   Local Path: {result['local_audio_path']}")
            print(f"   Distance: {result['distance']}\n")
        
        # Provide playback control options
        while query_manager.is_playing:
            control = input("Playback controls (stop/pause/resume/next): ").lower()
            if control == 'stop':
                query_manager.stop_audio()
                break
            elif control == 'pause':
                query_manager.pause_audio()
            elif control == 'resume':
                query_manager.resume_audio()
            elif control == 'next':
                query_manager.stop_audio()
                break

if __name__ == '__main__':
    main()

# Dependencies:
# pip install chromadb sentence-transformers pygame

"""
Enhanced Audio Query and Playback System

Key Features:
1. Semantic Search: Find audio files similar to a text query
2. Automatic Playback: Play the most similar track automatically
3. Playback Controls: Stop, Pause, Resume audio

Usage Notes:
1. Install dependencies: 
   pip install chromadb sentence-transformers pygame

Playback Workflow:
- Enter a text description of the music you want
- System finds and plays the most similar track
- Interactive controls to manage playback
"""