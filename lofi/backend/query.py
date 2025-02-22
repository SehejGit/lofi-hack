import chromadb
from sentence_transformers import SentenceTransformer
import os

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
        
        # Get the collection
        self.collection = self.chroma_client.get_collection(name=collection_name)

    def semantic_search(self, query, n_results=5):
        """
        Perform semantic search on audio prompts.
        
        :param query: Text query to search
        :param n_results: Number of results to return
        :return: List of matching audio files and their metadata
        """
        # Generate embedding for the query
        query_embedding = self.embedding_model.encode(query).tolist()
        
        # Perform semantic search
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        
        return self._process_query_results(results)

    def metadata_filter_search(self, filter_dict, n_results=5):
        """
        Search audio files based on metadata filters.
        
        :param track_data: Dictionary containing track metadata
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

def main():
    # Initialize AudioQueryManager
    query_manager = AudioQueryManager()
    
    # Example 1: Semantic Search
    print("=== Semantic Search ===")
    print("Searching for 'relaxing music':")
    semantic_results = query_manager.semantic_search("relaxing music")
    for result in semantic_results:
        print(f"Prompt: {result['prompt']}")
        print(f"Local Audio Path: {result['local_audio_path']}")
        print(f"Distance: {result['distance']}")
        print("---")
    
    # Example 2: Metadata Filter Search
    print("\n=== Metadata Filter Search ===")
    print("Searching for prompts with 'lo-fi':")
    filter_results = query_manager.metadata_filter_search(
        {"prompt": {"$contains": "lo-fi"}}
    )
    for result in filter_results:
        print(f"Prompt: {result['prompt']}")
        print(f"Local Audio Path: {result['local_audio_path']}")
        print("---")

if __name__ == '__main__':
    main()

# Dependencies:
# pip install chromadb sentence-transformers

"""
Query Types Demonstrated:
1. Semantic Search: Find audio files similar to a text query
2. Metadata Filtering: Search based on specific metadata conditions

Usage Notes:
1. Install dependencies: 
   pip install chromadb sentence-transformers

Supported Metadata Filters:
- Exact match: {"key": "value"}
- ChromaDB operators: {"key": {"$eq": value, "$gt": value, "$gte": value, "$lt": value, "$lte": value}}
- Partial text search: {"key": {"$contains": "partial"}} (uses manual filtering)
"""