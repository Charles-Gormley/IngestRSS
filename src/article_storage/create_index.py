from pinecone import Pinecone, ServerlessSpec

from initialize import pc

import os
from dotenv import load_dotenv
load_dotenv()


index_name = "quickstart" # TODO: Remove this line after we are done testing with vector dbs. 

if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=2,
        metric="cosine",
        spec=ServerlessSpec(
            cloud='aws', 
            region='us-east-1'
        ) 
    ) 

index = pc.Index(index_name)

index.upsert(
    vectors=[
        {"id": "vec1", "values": [1.0, 1.5]},
        {"id": "vec2", "values": [2.0, 1.0]},
        {"id": "vec3", "values": [0.1, 3.0]},
    ],
    namespace="example-namespace1"
)

index.upsert(
    vectors=[
        {"id": "vec2124", "values": [1.0, -2.5]},
        {"id": "vec21214", "values": [3.0, -2.0]},
        {"id": "vec31251", "values": [0.5, -1.5]},
    ],
    namespace="example-namespace2"
)



index.upsert(
    vectors=[
        {"id": "vec1", "values": [1.0, -2.5]},
        {"id": "vec2", "values": [3.0, -2.0]},
        {"id": "vec3", "values": [0.5, -1.5]},
    ],
    namespace="example-namespace2"
)

print(index.describe_index_stats())

query_results1 = index.query(
    namespace="example-namespace1",
    vector=[1.0, 1.5],
    top_k=3,
    include_values=True
)

print(query_results1)

query_results2 = index.query(
    namespace="example-namespace2",
    vector=[1.0,-2.5],
    top_k=3,
    include_values=True
)

print(query_results2)
