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
quadrant_client = QdrantClient(
    path=config['vector_db']['path'],
)


class SemanticSearcher:
    """Bla bla

    """
    def __init__(self,
                 embedding_engine: EmbeddingEngine,
                 vector_db,
                 n_return_vec: int = 10,
                 ):
        self._embedding_engine = embedding_engine
        self.vector_db = vector_db
        self.n_return_vec = n_return_vec

    def search_by_(self, query: str):
        query_vec = self._embedding_engine.embed(query)
        return self.vector_db.get_nearest_vector_ids(query_vec, self.n_return_vec)


class TextSearcher:
    """Bla bla

    """
    def __init__(self,
                 text_db,
                 semantic_searcher: SemanticSearcher,
                 text_selection: str = 'only return text',
                 ):
        self.text_db = text_db
        self.semantic_searcher = semantic_searcher
        self.text_selection = text_selection

    def search_for_text_related_to_(self, query: str):
        db_ids = self.semantic_searcher.search_by_(query)
        return self._get_text_from_db_ids(db_ids)

    def _get_text_from_db_ids(self, db_ids):
        if self.text_selection == 'only return text':
            return [self.text_db.get_text(db_id) for db_id in db_ids]
        elif self.text_selection == 'return text and id':
            return [(self.text_db.get_text(db_id), db_id) for db_id in db_ids]
        else:
            raise ValueError(f'Invalid text selection {self.text_selection}')