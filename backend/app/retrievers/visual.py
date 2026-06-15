from backend.app.retrievers.base import Retriever
from backend.app.embeddings.base import EmbeddingModel
from backend.app.indexes.base import VectorIndex

class VisualRetriever(Retriever):
    def __init__(self, embedding_model: EmbeddingModel, vector_index: VectorIndex):
        self.embedding_model = embedding_model
        self.vector_index = vector_index

    def retrieve(self, query_context: dict, top_k: int) -> list[dict]:
        query_text = query_context.get("query")
        if not query_text:
            return []
            
        # Trích xuất vector truy vấn
        query_vectors = self.embedding_model.encode_text([query_text])
        query_vector = query_vectors[0].tolist()
        
        # Tìm kiếm trong chỉ mục vector
        return self.vector_index.search(query_vector, top_k)
