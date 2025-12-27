import os
from dotenv import load_dotenv

load_dotenv()

class config:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    ASTRA_DB_API_ENDPOINT_KEY=os.getenv("ASTRA_DB_API_ENDPOINT")
    ASTRA_DB_APPLICATION_TOKEN=os.getenv("ASTRA_DB_APPLICATION_TOKEN")
    ASTRA_DB_KEYSPACE=os.getenv("ASTRA_DB_KEYSPACE")
    Embedding_Model="sentence-transformers/all-MiniLM-L6-v2"
    RAG_Model="llama-3.1-8b-instant"
