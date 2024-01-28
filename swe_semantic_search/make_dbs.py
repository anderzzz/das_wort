"""Script to make the databases for the semantic search engine.

"""
import yaml

from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient, models

#
# Parse the configuration file
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)


# Load the embedding engine
embedding_model = SentenceTransformer(
    model_name_or_path=config['embedding_model']['model_name_or_path'],
    cache_folder=config['embedding_model']['cache_folder'],
)

#
# Load the vector database
quadrant_client = QdrantClient(
    path=config['vector_db']['path'],
)

#
# Connect to the textdata collection
pass

