from pinecone import Pinecone
import os
from dotenv import load_dotenv
load_dotenv()

# Set up Pinecone client
api_key = os.getenv("PINCEONE_API_KEY")

pc = Pinecone(api_key=api_key)