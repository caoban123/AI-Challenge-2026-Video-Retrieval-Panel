from backend.app.strategies.base import TaskStrategy
from backend.app.retrievers.hybrid import HybridRetriever

class HybridKisStrategy(TaskStrategy):
    def __init__(self, hybrid_retriever: HybridRetriever):
        self.hybrid_retriever = hybrid_retriever

    def retrieve(self, query_context: dict) -> dict:
        """
        Lấy các kết quả thô từ cả hai nhánh Dense (Visual) và Sparse (Text).
        """
        top_k = query_context.get("top_k", 100)
        return self.hybrid_retriever.retrieve(query_context, top_k)

    def rerank(self, candidates: dict, query_context: dict) -> list[dict]:
        """
        Áp dụng thuật toán Reciprocal Rank Fusion (RRF) để gộp điểm và xếp hạng lại.
        """
        visual_list = candidates.get("visual", [])
        text_list = candidates.get("text", [])
        
        k = 60
        fused_candidates = {}
        
        # 1. Quét danh sách kết quả Dense Vector (Visual)
        for idx, item in enumerate(visual_list):
            key = (item["video_id"], item["frame_id"])
            if key not in fused_candidates:
                fused_candidates[key] = dict(item)
                fused_candidates[key]["rrf_score"] = 0.0
            
            # Tính điểm RRF
            rank = idx + 1
            fused_candidates[key]["rrf_score"] += 1.0 / (k + rank)
            # Cập nhật điểm visual_score trong evidence
            fused_candidates[key]["evidence"]["visual_score"] = item["score"]

        # 2. Quét danh sách kết quả Sparse BM25 (Text)
        for idx, item in enumerate(text_list):
            key = (item["video_id"], item["frame_id"])
            if key not in fused_candidates:
                # Nếu frame này chưa xuất hiện trong visual_list, khởi tạo
                fused_candidates[key] = dict(item)
                fused_candidates[key]["rrf_score"] = 0.0
                # Reset visual_score
                fused_candidates[key]["evidence"]["visual_score"] = None
                
            # Tính điểm RRF
            rank = idx + 1
            fused_candidates[key]["rrf_score"] += 1.0 / (k + rank)
            # Cập nhật điểm text_score trong evidence
            fused_candidates[key]["evidence"]["text_score"] = item["score"]

        # 3. Sắp xếp lại theo điểm RRF giảm dần
        sorted_candidates = sorted(
            fused_candidates.values(),
            key=lambda x: x.get("rrf_score", 0.0),
            reverse=True
        )
        
        # 4. Giới hạn Top-K kết quả trả về và gán lại rank
        top_k = query_context.get("top_k", 100)
        final_results = []
        
        for rank_idx, item in enumerate(sorted_candidates[:top_k]):
            item["rank"] = rank_idx + 1
            item["score"] = item["rrf_score"]  # Ghi nhận điểm rrf làm score chính để UI hiển thị
            # Xóa trường nháp để giữ sạch payload
            if "rrf_score" in item:
                del item["rrf_score"]
            final_results.append(item)
            
        return final_results

    def build_ui_payload(self, results: list[dict], took_ms: int) -> dict:
        return {
            "query_type": "textual_kis",
            "strategy": "HybridKisStrategy",
            "took_ms": took_ms,
            "results": results
        }
