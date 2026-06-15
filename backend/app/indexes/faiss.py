import os
import json
import numpy as np
import faiss
from backend.app.indexes.base import VectorIndex

class FaissVectorIndex(VectorIndex):
    def __init__(self, index_path: str = None, metadata_path: str = None):
        self.index_path = index_path
        self.metadata_path = metadata_path
        self.index = None
        self.metadata = []
        if index_path and metadata_path:
            self.load(index_path, metadata_path)

    def build(self, vectors, metadata: list[dict]) -> None:
        dimension = len(vectors[0]) if len(vectors) > 0 else 512
        index_matrix = np.array(vectors, dtype=np.float32)
        self.index = faiss.IndexFlatIP(dimension)
        self.index.add(index_matrix)
        self.metadata = metadata

    def search(self, query_vector: list[float], top_k: int) -> list[dict]:
        if self.index is None:
            raise ValueError("Chỉ mục FAISS chưa được xây dựng hoặc nạp!")
            
        query_vector_np = np.array([query_vector], dtype=np.float32)
        scores, indices = self.index.search(query_vector_np, top_k)
        
        results = []
        for i in range(top_k):
            idx = indices[0][i]
            score = scores[0][i]
            if 0 <= idx < len(self.metadata):
                meta = self.metadata[idx]
                results.append({
                    "rank": i + 1,
                    "video_id": meta.get("video_title"),
                    "frame_id": meta.get("frame_id"),
                    "timestamp": float(meta.get("frame_id")), # Trong FAISS 1 FPS thì frame_id là số thứ tự giây
                    "score": float(score),
                    "thumb_url": f"/media/thumbs/{meta.get('video_title')}/{meta.get('frame_id')}.jpg",
                    "frame_url": f"/media/frames/{meta.get('video_title')}/{meta.get('frame_id')}.jpg",
                    "video_url": f"/media/videos/{meta.get('video_title')}.mp4",
                    "evidence": {
                        "visual_score": float(score),
                        "text_score": None,
                        "ocr_score": None,
                        "asr_score": None
                    }
                })
        return results

    def save(self, path: str) -> None:
        if self.index is None:
            raise ValueError("Không có chỉ mục để lưu!")
        faiss.write_index(self.index, path)
        meta_path = os.path.splitext(path)[0] + "_meta.json"
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(self.metadata, f, indent=4, ensure_ascii=False)

    def load(self, path: str, metadata_path: str = None) -> None:
        print(f"[FaissIndex] Dang nap chi muc FAISS tu: {path}...")
        self.index = faiss.read_index(path)
        
        if not metadata_path:
            metadata_path = os.path.splitext(path)[0] + "_meta.json"
            
        print(f"[FaissIndex] Dang nap danh ba metadata tu: {metadata_path}...")
        with open(metadata_path, "r", encoding="utf-8") as f:
            self.metadata = json.load(f)
        print("[FaissIndex] [Success] Nap chi muc FAISS thanh cong!")
