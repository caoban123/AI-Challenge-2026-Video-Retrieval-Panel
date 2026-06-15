from backend.app.strategies.base import TaskStrategy
from backend.app.retrievers.base import Retriever

class TextualKisStrategy(TaskStrategy):
    def __init__(self, retriever: Retriever):
        self.retriever = retriever

    def retrieve(self, query_context: dict) -> list[dict]:
        top_k = query_context.get("top_k", 100)
        return self.retriever.retrieve(query_context, top_k)

    def rerank(self, candidates: list[dict], query_context: dict) -> list[dict]:
        # Ở P0 Baseline, chúng ta chưa áp dụng mô hình Rerank nâng cao (Gemini/Reranker),
        # vì vậy giữ nguyên thứ tự sắp xếp theo độ tương đồng Cosine của CLIP.
        return candidates

    def build_ui_payload(self, results: list[dict], took_ms: int) -> dict:
        # Nhận query từ kết quả hoặc ngữ cảnh nếu cần, ở đây ta lấy từ kết quả đầu tiên nếu có
        query = ""
        if results and len(results) > 0:
            # Ta có thể truyền câu query ban đầu qua kết quả hoặc metadata
            pass
            
        return {
            "query_type": "textual_kis",
            "strategy": "TextualKisStrategy",
            "took_ms": took_ms,
            "results": results
        }
