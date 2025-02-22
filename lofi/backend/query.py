import chromadb
from sentence_transformers import SentenceTransformer
import os
import pygame
import threading
import time

class AudioQueryManager:
    def __init__(self, db_path='./chroma_db', collection_name='audio'):
        """
        Initialize ChromaDB client and load or create the audio prompts collection.
        
        :param db_path: Path to ChromaDB storage
        :param collection_name: Name of the collection to query
        """
        # Ensure the database directory exists
        os.makedirs(db_path, exist_ok=True)
        
        # Initialize ChromaDB client
        self.chroma_client = chromadb.PersistentClient(path=db_path)
        
        # Load embedding model
        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
        
        # Create the collection if it doesn't exist
        try:
            self.collection = self.chroma_client.get_collection(name=collection_name)
        except chromadb.errors.InvalidCollectionException:
            # Create the collection with default configuration
            self.collection = self.chroma_client.create_collection(
                name=collection_name, 
                metadata={"description": "Audio tracks for semantic search"}
            )
        
        # Initialize pygame mixer for audio playback
        pygame.mixer.init()
        
        # Current playing track
        self.current_track = None
        self.playback_thread = None
        self.is_playing = False

    def create_or_update_track(self, track_data):
        """
        Create or update a track in the collection.
        
        :param track_data: Dictionary containing track metadata
        """
        # Required fields
        required_fields = ['id', 'embedding', 'metadata']
        
        # Validate input
        for field in required_fields:
            if field not in track_data:
                raise ValueError(f"Missing required field: {field}")
        
        # Add or update the track
        self.collection.upsert(
            ids=[track_data['id']],
            embeddings=[track_data['embedding']],
            metadatas=[track_data['metadata']]
        )

    # Rest of the methods remain the same as in the previous implementation
    # ... (semantic_search, metadata_filter_search, play_audio, etc. methods)

def main():
    # Initialize AudioQueryManager
    query_manager = AudioQueryManager()
    
    # Example of adding a track (you'd typically do this during audio import)
    example_track = {
        'id': 'track_001',
        'embedding': [0.1, 0.2, 0.3],  # Example embedding vector
        'metadata': {
            'prompt': 'relaxing lo-fi beats',
            'local_audio_path': '/path/to/audio/track.mp3',
            'audio_url': 'https://example.com/track.mp3'
        }
    }
    
    # Add the track to the collection
    query_manager.create_or_update_track(example_track)
    
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
Semantic Audio Search and Playback System

Key Features:
1. Automatic Collection Creation
2. Semantic Search: Find audio files similar to a text query
3. Metadata Filtering: Search based on specific metadata conditions
4. Automatic Playback: Play the most similar track
5. Interactive Playback Controls

Usage Notes:
1. Install dependencies: 
   pip install chromadb sentence-transformers pygame

Supported Metadata Filters:
- Exact match: {"key": "value"}
- ChromaDB operators: {"key": {"$eq": value, "$gt": value, "$gte": value, "$lt": value, "$lte": value}}
- Partial text search: {"key": {"$contains": "partial"}} (uses manual filtering)
"""