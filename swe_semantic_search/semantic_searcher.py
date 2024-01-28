"""Perform the semantic search

"""
import yaml

from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient, models

#
# Parse the configuration file
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

#
# Load the embedding engine
embedding_model = SentenceTransformer(
    model_name_or_path=config['embedding_model']['model_name_or_path'],
    cache_folder=config['embedding_model']['cache_folder'],
)

#
# Load the vector database
qdrant_handle = QdrantClient(
    path=config['vector_db']['path'],
)

#
# Embed query
query_vector = embedding_model.encode([config['my_query']])[0]
hits = qdrant_handle.search(
    collection_name=config['vector_db']['collection_name'],
    query_vector=query_vector,
    limit=5
)
