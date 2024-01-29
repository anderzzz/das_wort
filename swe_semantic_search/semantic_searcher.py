"""Perform the semantic search

"""
import yaml
import sqlite3

from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient

from row_factory import dict_factory

#
# Parse the configuration file
with open('conf.yaml', 'r') as f:
    config = yaml.safe_load(f)
with open('sql_strings.yaml', 'r') as f:
    sql_strings = yaml.safe_load(f)

#
# Connect to the SQLite database
conn = sqlite3.connect(config['text_source']['text_data_file'])
conn.row_factory = dict_factory
cur = conn.cursor()

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
# Embed query and do the semantic similarity search
query_vector = embedding_model.encode([config['search']['my_query']])[0]
hits = qdrant_handle.search(
    collection_name=config['vector_db']['collection_name'],
    query_vector=query_vector,
    limit=config['search']['n_results']
)

#
# Retrieve the text segments
semantically_similar_segments = []
for hit in hits:
    cur.execute(sql_strings['sql_select_by_id'], (hit.id,))
    data = cur.fetchone()
    semantically_similar_segments.append({field: data[field] for field in config['search']['output_keys']})

print (semantically_similar_segments)
