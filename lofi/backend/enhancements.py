import chromadb
import re
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Initialize ChromaDB client
chroma_client = chromadb.PersistentClient(path="./chroma_db")

# Connect to the collection
collection = chroma_client.get_or_create_collection(name="audio")

# Load sentence embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Function to extract prompts from ChromaDB
def get_prompts_from_chromadb():
    """Fetch all stored prompts from ChromaDB."""
    results = collection.get(include=["metadatas"])  # Retrieve metadata
    prompts = [meta["prompt"] for meta in results["metadatas"] if "prompt" in meta]
    return prompts

# Extract keywords from a given text prompt
def extract_keywords(text):
    """Extracts meaningful keywords from a prompt by removing common words."""
    text = re.sub(r"[^a-zA-Z\s]", "", text.lower())  # Remove special characters
    stopwords = {"lofi", "for", "the", "a", "and", "to", "in", "on", "with", "of", "beat", "track", "music"}
    keywords = [word for word in text.split() if word not in stopwords]
    return keywords

# Suggest better descriptive words based on existing dataset
def suggest_better_words(user_prompt, top_n=3):
    """Suggests better descriptive words for a given prompt based on ChromaDB prompts."""

    # Fetch dataset prompts from ChromaDB
    dataset_prompts = get_prompts_from_chromadb()
    
    if not dataset_prompts:
        return ["No prompts found in ChromaDB."]

    # Encode dataset prompts
    prompt_embeddings = model.encode(dataset_prompts)

    # Encode user's input
    user_embedding = model.encode([user_prompt])

    # Compute cosine similarity
    similarities = cosine_similarity(user_embedding, prompt_embeddings)[0]

    # Get top N closest prompts
    top_indices = similarities.argsort()[-top_n:][::-1]
    closest_prompts = [dataset_prompts[i] for i in top_indices]

    # Extract unique keywords from similar prompts
    suggested_words = set()
    user_keywords = set(extract_keywords(user_prompt))

    for prompt in closest_prompts:
        prompt_keywords = set(extract_keywords(prompt))
        new_words = prompt_keywords - user_keywords  # Find words user didn’t include
        suggested_words.update(new_words)

    return list(suggested_words)

# Main execution
if __name__ == "__main__":
    # Example user input
    user_input = "rainy day lofi beat"

    # Get suggestions
    suggestions = suggest_better_words(user_input)

    print(f"🔍 Suggested words: {', '.join(suggestions) if suggestions else 'No suggestions found'}")