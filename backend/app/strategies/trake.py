from backend.app.strategies.base import TaskStrategy
from backend.app.retrievers.base import Retriever

class TrakeStrategy(TaskStrategy):
    def __init__(self, retriever: Retriever):
        self.retriever = retriever

    def retrieve(self, query_context: dict) -> dict:
        top_k = query_context.get("top_k", 100)
        return self.retriever.retrieve(query_context, top_k)

    def rerank(self, candidates: dict, query_context: dict) -> list[dict]:
        # Sử dụng giải thuật RRF để kết hợp hình ảnh (dense) và từ khóa (sparse) tìm bằng chứng tốt nhất
        visual_list = candidates.get("visual", [])
        text_list = candidates.get("text", [])
        
        k = 60
        fused_candidates = {}
        
        for idx, item in enumerate(visual_list):
            key = (item["video_id"], item["frame_id"])
            if key not in fused_candidates:
                fused_candidates[key] = dict(item)
                fused_candidates[key]["rrf_score"] = 0.0
            rank = idx + 1
            fused_candidates[key]["rrf_score"] += 1.0 / (k + rank)
            fused_candidates[key]["evidence"]["visual_score"] = item["score"]

        for idx, item in enumerate(text_list):
            key = (item["video_id"], item["frame_id"])
            if key not in fused_candidates:
                fused_candidates[key] = dict(item)
                fused_candidates[key]["rrf_score"] = 0.0
                fused_candidates[key]["evidence"]["visual_score"] = None
            rank = idx + 1
            fused_candidates[key]["rrf_score"] += 1.0 / (k + rank)
            fused_candidates[key]["evidence"]["text_score"] = item["score"]

        sorted_candidates = sorted(
            fused_candidates.values(),
            key=lambda x: x.get("rrf_score", 0.0),
            reverse=True
        )
        
        top_k = query_context.get("top_k", 100)
        final_results = []
        for rank_idx, item in enumerate(sorted_candidates[:top_k]):
            item["rank"] = rank_idx + 1
            item["score"] = item["rrf_score"]
            if "rrf_score" in item:
                del item["rrf_score"]
            final_results.append(item)
            
        return final_results

    def build_ui_payload(self, results: list[dict], took_ms: int) -> dict:
        # Dựng lộ trình (trajectory) giả lập của đối tượng được truy vết:
        # Lấy video xuất hiện phổ biến nhất trong kết quả và xếp các frame theo thời gian tăng dần
        video_counts = {}
        for item in results:
            v_id = item["video_id"]
            video_counts[v_id] = video_counts.get(v_id, 0) + 1
            
        best_video = None
        if video_counts:
            best_video = max(video_counts, key=video_counts.get)
            
        trajectory = []
        if best_video:
            trajectory_candidates = [item for item in results if item["video_id"] == best_video]
            # Sắp xếp theo thứ tự xuất hiện của frame_id
            trajectory = sorted(trajectory_candidates, key=lambda x: x["frame_id"])[:6]
            
        return {
            "query_type": "trake",
            "strategy": "TrakeStrategy",
            "took_ms": took_ms,
            "trajectory": trajectory,
            "results": results
        }
