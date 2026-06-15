import numpy as np
from rank_bm25 import BM25Okapi
from backend.app.indexes.base import TextSearchIndex

class Bm25TextSearchIndex(TextSearchIndex):
    def __init__(self):
        self.bm25 = None
        self.metadata = []

    def build(self, docs: list[dict]) -> None:
        """
        Xây dựng chỉ mục BM25 từ danh sách tài liệu.
        Mỗi tài liệu trong docs có định dạng:
        {
            "text": "văn bản mô tả của frame",
            "metadata": {
                "video_title": str,
                "frame_id": str,
                "timestamp_seconds": float
            }
        }
        """
        if not docs:
            print("[BM25] [Warning] Tai lieu nap vao BM25 trong!")
            return

        print(f"[BM25] [Info] Dang phan tich tach tu cho {len(docs)} tai lieu...")
        tokenized_corpus = []
        self.metadata = []

        for doc in docs:
            text = doc.get("text", "")
            # Tách từ đơn giản bằng lowercase và split theo khoảng trắng
            tokens = text.lower().split()
            tokenized_corpus.append(tokens)
            self.metadata.append(doc.get("metadata", {}))

        print("[BM25] [Info] Dang khoi tao chi muc BM25Okapi...")
        self.bm25 = BM25Okapi(tokenized_corpus)
        print("[BM25] [Success] Xay dung chi muc BM25 thanh cong!")

    def search(self, query: str, top_k: int) -> list[dict]:
        if not self.bm25 or not query:
            return []

        tokenized_query = query.lower().split()
        scores = self.bm25.get_scores(tokenized_query)
        
        # Lấy các index có điểm số cao nhất
        top_indices = np.argsort(scores)[::-1][:top_k]
        
        results = []
        for rank_idx, idx in enumerate(top_indices):
            score = scores[idx]
            # Chỉ lấy các kết quả có điểm trùng khớp lớn hơn 0 để tránh nhiễu
            if score <= 0:
                continue
                
            meta = self.metadata[idx]
            video_title = meta.get("video_title")
            frame_id = meta.get("frame_id")
            
            results.append({
                "rank": rank_idx + 1,
                "video_id": video_title,
                "frame_id": frame_id,
                "timestamp": float(meta.get("timestamp_seconds", 0)),
                "score": float(score),
                "thumb_url": f"/media/thumbs/{video_title}/{frame_id}.jpg",
                "frame_url": f"/media/frames/{video_title}/{frame_id}.jpg",
                "video_url": f"/media/videos/{video_title}.mp4",
                "evidence": {
                    "visual_score": None,
                    "text_score": float(score),
                    "ocr_score": None,
                    "asr_score": None
                }
            })
            
        return results
