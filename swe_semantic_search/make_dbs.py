"""Script to make the databases for the semantic search engine.

"""
import yaml
import csv

from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient, models

from segment_text import make_segments_of_


#
# Parse the configuration file
with open('./conf.yaml', 'r') as f:
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
qdrant_handle.recreate_collection(
    collection_name=config['vector_db']['collection_name'],
    vectors_config=models.VectorParams(
        size=embedding_model.get_sentence_embedding_dimension(),
        distance=models.Distance.COSINE,
    ),
)

#
# Build the vector database for the texts
with open(config['text_source']['text_data_file'], 'r', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)

    id_db = 0
    for row in reader:
        text_segments = make_segments_of_(
            text=row['content'],
            max_words_in_segment=config['segmentor']['max_segment_size'],
            n_overlapping_sentences=config['segmentor']['n_overlapping_sentences'],
        )

        for i_segment, text in enumerate(text_segments):
            vector = embedding_model.encode([text])[0]
            qdrant_handle.upsert(
                collection_name=config['vector_db']['collection_name'],
                points=[
                    models.PointStruct(
                        id=id_db,
                        vector=vector.tolist(),
                        payload={"title": row['title'],
                                 "url": row['url'],
                                 "text_id": row['document_id'],
                                 "segment_id": i_segment}
                    )
                ]
            )
            id_db += 1
