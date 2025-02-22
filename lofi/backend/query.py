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

    def metadata_filter_search(self, filter_dict, n_results=5):
        """
        Search audio files based on metadata filters.
        
        :param filter_dict: Dictionary of metadata filters
        :param n_results: Number of results to return
        :return: List of matching audio files and their metadata
        """
        # Prepare ChromaDB compatible filter
        chroma_filter = {}
        for key, value in filter_dict.items():
            if isinstance(value, dict):
                # Handle special filtering cases
                if '$eq' in value:
                    chroma_filter[key] = value['$eq']
                elif '$contains' in value:
                    # For text containment, we'll do a manual post-filtering
                    return self._manual_contains_filter(key, value['$contains'], n_results)
                else:
                    # Pass through other standard ChromaDB operators
                    chroma_filter[key] = value
            else:
                # Direct equality
                chroma_filter[key] = value
        
        # Perform filtered search
        results = self.collection.get(
            where=chroma_filter,
            limit=n_results
        )
        
        return self._process_get_results(results)

    def _manual_contains_filter(self, key, search_term, n_results=50):
        """
        Manually filter results when $contains is used.
        
        :param key: Metadata key to search
        :param search_term: Term to search for
        :param n_results: Number of results to return
        :return: Filtered results
        """
        # Get all results
        all_results = self.collection.get()
        
        # Manually filter results
        filtered_results = {
            'ids': [],
            'metadatas': []
        }
        
        for i, metadata in enumerate(all_results['metadatas']):
            if search_term.lower() in str(metadata.get(key, '')).lower():
                filtered_results['ids'].append(all_results['ids'][i])
                filtered_results['metadatas'].append(metadata)
                
                # Stop if we've reached the desired number of results
                if len(filtered_results['ids']) >= n_results:
                    break
        
        return self._process_get_results(filtered_results)

    def _process_query_results(self, results):
        """
        Process and format query results.
        
        :param results: Raw query results from ChromaDB
        :return: Formatted list of results
        """
        processed_results = []
        
        # Iterate through results
        for i in range(len(results['ids'][0])):
            result = {
                'id': results['ids'][0][i],
                'prompt': results['metadatas'][0][i].get('prompt', 'No prompt'),
                'audio_url': results['metadatas'][0][i].get('audio_url', 'No URL'),
                'local_audio_path': results['metadatas'][0][i].get('local_audio_path', 'No local path'),
                'distance': results['distances'][0][i] if results['distances'] else None
            }
            processed_results.append(result)
        
        return processed_results

    def _process_get_results(self, results):
        """
        Process and format get results.
        
        :param results: Raw get results from ChromaDB
        :return: Formatted list of results
        """
        processed_results = []
        
        # Iterate through results
        for i in range(len(results['ids'])):
            result = {
                'id': results['ids'][i],
                'prompt': results['metadatas'][i].get('prompt', 'No prompt'),
                'audio_url': results['metadatas'][i].get('audio_url', 'No URL'),
                'local_audio_path': results['metadatas'][i].get('local_audio_path', 'No local path')
            }
            processed_results.append(result)
        
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
Semantic Audio Search and Playback System

Key Features:
1. Semantic Search: Find audio files similar to a text query
2. Metadata Filtering: Search based on specific metadata conditions
3. Automatic Playback: Play the most similar track
4. Interactive Playback Controls

Usage Notes:
1. Install dependencies: 
   pip install chromadb sentence-transformers pygame

Supported Metadata Filters:
- Exact match: {"key": "value"}
- ChromaDB operators: {"key": {"$eq": value, "$gt": value, "$gte": value, "$lt": value, "$lte": value}}
- Partial text search: {"key": {"$contains": "partial"}} (uses manual filtering)
"""