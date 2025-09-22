from pinecone import Pinecone, ServerlessSpec
# from sentence_transformers import SentenceTransformer
from app.config import settings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from protonx import ProtonX
import time

if not settings.PROTONX_API_KEY:
    raise ValueError("PROTONX_API_KEY is not set. Please check your .env file in the 'app' directory.")
client = ProtonX(api_key=settings.PROTONX_API_KEY)

# Add a check to ensure the API key is loaded before initializing Pinecone
if not settings.PINECONE_API_KEY:
    raise ValueError("PINECONE_API_KEY is not set. Please check your .env file in the 'app' directory.")

pc = Pinecone(api_key=settings.PINECONE_API_KEY)
index_name = "chat-history"
if index_name not in pc.list_indexes().names():
    # Check embedding dimension from ProtonX before creating index
    try:
        sample_embedding = client.embeddings.create("sample text")["data"][0]["embedding"]
        dimension = len(sample_embedding)
    except Exception as e:
        print(f"Could not determine embedding dimension from ProtonX, defaulting to 1024. Error: {e}")
        dimension = 1024 # Fallback dimension
    
    pc.create_index(
        name=index_name, 
        dimension=dimension, 
        metric="cosine", 
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )

index = pc.Index(index_name)
# embedder = SentenceTransformer('dangvantuan/vietnamese-embedding')  # Free HF model

def upsert_history(chat_id: str, query: str, response: str, namespace: str):
    text = f"Query: {query} | Response: {response}"
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=50)
    chunks = text_splitter.split_text(text=text)
    for i, chunk_text in enumerate(chunks):
        # Embed with ProtonX
        embeddings_response = client.embeddings.create(chunk_text)
        vector = embeddings_response["data"][0]["embedding"]  # Extract vector list
        vector_id = f"{chat_id}_{int(time.time())}_{i}"
        index.upsert(vectors=[(vector_id, vector, {"text": chunk_text, "chat_id": chat_id})], namespace=namespace)

def rag_query(query: str, agent_context: str, chat_id: str):
    # Embed query with ProtonX
    embeddings_response = client.embeddings.create(query)
    vector = embeddings_response["data"][0]["embedding"]
    results = index.query(vector=vector, top_k=5, namespace=agent_context, filter={"chat_id": chat_id})
    return " ".join([match['metadata']['text'] for match in results['matches']]) if results['matches'] else ""

# def upsert_history(chat_id: str, query: str, response: str, namespace: str):
#     text = f"Query: {query} | Response: {response}"
#     vector = embedder.encode(text).tolist()
#     # Create a unique ID for the vector to avoid collisions
#     vector_id = f"{chat_id}_{int(time.time())}"
#     index.upsert(vectors=[(vector_id, vector, {"text": text, "chat_id": chat_id})], namespace=namespace)

# def rag_query(query: str, agent_context: str, chat_id: str):
#     vector = embedder.encode(query).tolist()
#     results = index.query(vector=vector, top_k=3, namespace=agent_context, filter={"chat_id": chat_id})
#     return " ".join([match['metadata']['text'] for match in results['matches']]) if results['matches'] else ""