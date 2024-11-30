import os

from pinecone import Pinecone
from openai import OpenAI

# Set up Pinecone client
api_key = os.getenv("PINCEONE_API_KEY")
shards = os.getenv("PINECONE_SHARDS")
embedding_model = os.getenv("VECTOR_EMBEDDING_MODEL")
embedding_dim = int(os.getenv("VECTOR_EMBEDDING_DIM"))
vector_search_metric = os.getenv("VECTOR_SEARCH_METRIC")
index_name = os.getenv("PINECONE_DB_NAME")

client = OpenAI() # For Embedding Models, Not LLMs
pc = Pinecone(api_key=api_key)

def get_index():
    if index_name not in pc.list_indexes().names():
        pc.create_index(
            name=index_name,
            dimension=embedding_dim,
            metric=vector_search_metric,
            shards=shards
        ) 

    index = pc.Index(index_name)
    return index

def vectorize(article:str) -> list[float]:
    response = client.embeddings.create(
        input=article,
        model=os.getenv('OPENAI_EMBEDDING_MODEL') 
    )
    
    return response.data[0].embedding 


def upsert_vectors(index:Pinecone.Index, vectors:list[dict], namespace:str): # [ ] Check if the data is being upserted. 
    index.upsert(
        vectors=vectors,
        namespace=namespace
    )

def query_vectors(index:Pinecone.Index, namespace:str, vector:list[float], top_k:int, filter_query:dict=None): # [ ]: Make sure this is working. 
    
    if len(vector) != int(embedding_dim):
        raise ValueError("Length of vector does not match the embedding dimension")
    
    if filter_query: 
        query = index.query(
            namespace=namespace,
            vector=vector,
            filter_query=filter_query,
            top_k=top_k,
            include_metadata=True
        ) 
        
    else:
        query = index.query(
            namespace=namespace,
            vector=vector,
            top_k=top_k
        )
    
    return query


if __name__ == "__main__":
    # Create a large paragraph
    paragraph = '''This is a test.'''
    vectorize("This is a test string")