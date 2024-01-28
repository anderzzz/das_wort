"""Script to make the databases for the semantic search engine.

"""
import yaml
import json

from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient, models

#
# Parse the configuration file
with open('./conf.yaml', 'r') as f:
    config = yaml.safe_load(f)


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
qdrant_handle.recreate_collection(
    collection_name=config['vector_db']['collection_name'],
    vectors_config=models.VectorParams(
        size=embedding_model.get_sentence_embedding_dimension(),
        distance=models.Distance.COSINE,
    ),
)

#
# Build the vector database for the texts
with open(config['text_source']['db_file'], 'r') as f:
    text_data = json.load(f)

for text in text_data:
    vector = embedding_model.encode([text['content']])[0]
    qdrant_handle.upsert(
        collection_name=config['vector_db']['collection_name'],
        points=[
            models.PointStruct(
                id=text['document_id'],
                vector=vector.tolist(),
                payload={"title": text['title'], "url": text['url']}
            )
        ]
    )
