from backend.app.retrievers.base import Retriever
from backend.app.indexes.base import TextSearchIndex

class HybridRetriever(Retriever):
    def __init__(self, visual_retriever: Retriever, text_index: TextSearchIndex):
        self.visual_retriever = visual_retriever
        self.text_index = text_index

    def retrieve(self, query_context: dict, top_k: int) -> dict:
        """
        Trích xuất song song kết quả từ hai nhánh:
        1. Dense Vector Search (Visual)
        2. Sparse Text Search (BM25)
        """
        query_text = query_context.get("query", "")
        
        # Nhánh 1: Dense Search
        visual_results = self.visual_retriever.retrieve(query_context, top_k)
        
        # Nhánh 2: Sparse Search (BM25)
        text_results = self.text_index.search(query_text, top_k)
        
        return {
            "visual": visual_results,
            "text": text_results
        }
