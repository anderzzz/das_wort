"""Script to make the databases for the semantic search engine.

"""
import yaml
import sqlite3

from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient, models

from row_factory import dict_factory

#
# Parse the configuration file and sql strings file
with open('./conf.yaml', 'r') as f:
    config = yaml.safe_load(f)
with open('./sql_strings.yaml', 'r') as f:
    sql_strings = yaml.safe_load(f)

#
# Connect to the SQLite database
conn = sqlite3.connect(config['text_source']['text_data_file'])
conn.row_factory = dict_factory
cur = conn.cursor()
cur.execute(sql_strings['sql_select_all'])

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
qdrant_handle.recreate_collection(
    collection_name=config['vector_db']['collection_name'],
    vectors_config=models.VectorParams(
        size=embedding_model.get_sentence_embedding_dimension(),
        distance=models.Distance.COSINE,
    ),
)

#
# Build the vector database for the text segments
while True:
    row = cur.fetchone()
    if row is None:
        break

    vector = embedding_model.encode([row['content']])[0]
    qdrant_handle.upsert(
        collection_name=config['vector_db']['collection_name'],
        points=[
            models.PointStruct(
                id=row['surrogate_key'],
                vector=vector.tolist(),
                payload={"title": row['title'],
                         "url": row['url']}
            )
        ]
    )
