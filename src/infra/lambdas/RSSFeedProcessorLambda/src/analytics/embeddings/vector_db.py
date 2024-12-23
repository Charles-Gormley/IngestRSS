import os

from pinecone import Pinecone
from openai import OpenAI

from utils import setup_logging

logger = setup_logging()


# Set up Pinecone client
api_key = os.getenv("PINCEONE_API_KEY")
shards = os.getenv("PINECONE_SHARDS")
embedding_model = os.getenv("VECTOR_EMBEDDING_MODEL")
embedding_dim = os.getenv("VECTOR_EMBEDDING_DIM")
vector_search_metric = os.getenv("VECTOR_SEARCH_METRIC")
index_name = os.getenv("PINECONE_DB_NAME")

client = OpenAI() # For Embedding Models, Not LLMs
pc = Pinecone(api_key=api_key)

def get_index():
    if index_name not in pc.list_indexes().names():
        return KeyError(f"Index {index_name} not found")

    index = pc.Index(index_name)
    return index

def vectorize(article:str) -> list[float]:
    response = client.embeddings.create(
        input=article, # FIXME: This fails when article is something else, find what the 'something else' is and implement fix.
        model=os.getenv('OPENAI_EMBEDDING_MODEL', 'text-') 
    )

    return response.data[0].embedding 


def upsert_vectors(index:Pinecone.Index, data:list[dict], namespace:str): # [ ] Check if the data is being upserted. 
    response = index.upsert(
        vectors=data,
        namespace=namespace
    )
    logger.info(f'Upserted Vector Response : {response.to_dict()}')
    logger.info(f'Upserted Vector Length : {len(data[0]["values"])}')
    logger.info(f'Upserted Vector Response Type : {type(response)}')
    logger.info(f'Upserted Vector Response - status : {response.status_code}')
    
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