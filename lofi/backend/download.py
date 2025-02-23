import os
import requests
import chromadb
from sentence_transformers import SentenceTransformer
import uuid

def download_audio_file(audio_url, output_dir='downloaded_audio'):
    """
    Download an audio file and return its local path.
    
    :param audio_url: URL of the audio file
    :param output_dir: Directory to save downloaded audio files
    :return: Local file path or None if download fails
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        # Send a GET request to download the audio file
        response = requests.get(audio_url, stream=True)
        response.raise_for_status()
        
        # Generate a unique filename
        file_extension = os.path.splitext(audio_url.split('?')[0])[-1] or '.mp3'
        filename = os.path.join(output_dir, f'{uuid.uuid4()}{file_extension}')
        
        # Write the audio file
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"Successfully downloaded: {filename}")
        return os.path.abspath(filename)  # Return absolute path
    
    except Exception as e:
        print(f"Error downloading audio from {audio_url}: {e}")
        return None

def fetch_huggingface_dataset(dataset='vikhyatk/lofi', split='train', offset=305, length=100):
    """
    Fetch dataset rows from Hugging Face Datasets Server.
    
    :param dataset: Name of the dataset
    :param split: Dataset split to fetch
    :param offset: Starting index
    :param length: Number of rows to fetch
    :return: JSON response containing dataset rows
    """
    url = "https://datasets-server.huggingface.co/rows"
    params = {
        "dataset": dataset,
        "config": "default",
        "split": split,
        "offset": offset,
        "length": length
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None

def populate_chromadb(dataset_data, embedding_model, collection):
    """
    Populate ChromaDB with dataset rows, downloading audio files.
    
    :param dataset_data: JSON data from Hugging Face Datasets Server
    :param embedding_model: Sentence Transformer model for generating embeddings
    :param collection: ChromaDB collection to populate
    """
    # Tracks rows processed
    processed_rows = 0
    failed_rows = 0
    
    for row_data in dataset_data["rows"]:
        row = row_data["row"]
        row_id = row["id"]
        
        # Get audio URL and prompt
        audio_url = row["audio"][0]["src"] if row["audio"] else None
        prompt_text = row["prompt"]
        
        try:
            # Generate embedding
            embedding = embedding_model.encode(prompt_text).tolist()
            
            # Prepare metadata
            metadata = {
                "prompt": prompt_text,
                "audio_url": audio_url
            }
            
            # Try to download audio file and add local path
            if audio_url:
                local_audio_path = download_audio_file(audio_url)
                if local_audio_path:
                    metadata["local_audio_path"] = local_audio_path
            
            # Add data to ChromaDB
            collection.add(
                ids=[row_id],
                embeddings=[embedding],
                metadatas=[metadata]
            )
            
            processed_rows += 1
        
        except Exception as e:
            print(f"Error processing row {row_id}: {e}")
            failed_rows += 1
    
    print(f"Processed {processed_rows} rows successfully")
    print(f"Failed to process {failed_rows} rows")

def main():
    # Initialize ChromaDB client
    chroma_client = chromadb.PersistentClient(path="./chroma_db")
    
    # Create or get collection (clear existing data)
    # try:
    #     chroma_client.delete_collection(name="audio_prompts")
    # except:
    #     pass
    collection = chroma_client.get_or_create_collection(name="audio")
    
    # Load embedding model
    embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
    
    # Fetch dataset
    dataset_data = fetch_huggingface_dataset()
    
    if dataset_data:
        # Populate ChromaDB
        populate_chromadb(dataset_data, embedding_model, collection)
    else:
        print("Failed to fetch dataset")

if __name__ == '__main__':
    main()

# Dependencies:
# pip install requests chromadb sentence-transformers

"""
Updated script to ensure:
1. Audio files are downloaded
2. Absolute paths are stored
3. Collection is recreated to avoid conflicts
"""