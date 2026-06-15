import os
import json
import time
from backend.app.core.config import settings
from backend.app.embeddings.clip import ClipEmbeddingModel
from backend.app.indexes.qdrant import QdrantVectorIndex
from backend.app.indexes.faiss import FaissVectorIndex
from backend.app.indexes.bm25 import Bm25TextSearchIndex
from backend.app.retrievers.visual import VisualRetriever
from backend.app.retrievers.hybrid import HybridRetriever
from backend.app.strategies.hybrid_kis import HybridKisStrategy
from backend.app.strategies.qa import QaStrategy
from backend.app.strategies.trake import TrakeStrategy

class SearchService:
    def __init__(self):
        # 1. Khởi tạo mô hình trích xuất đặc trưng (Embedding Model)
        self.embedding_model = ClipEmbeddingModel(settings.CLIP_MODEL_ID)
        
        # 2. Khởi tạo cơ sở dữ liệu Vector (Vector Index) dựa trên cấu hình settings
        index_type = settings.VECTOR_INDEX_TYPE.lower()
        if index_type == "qdrant":
            self.vector_index = QdrantVectorIndex(
                url=settings.QDRANT_URL,
                api_key=settings.QDRANT_API_KEY,
                collection_name=settings.COLLECTION_NAME
            )
        elif index_type == "faiss":
            self.vector_index = FaissVectorIndex(
                index_path=settings.FAISS_INDEX_PATH,
                metadata_path=settings.FAISS_METADATA_PATH
            )
        else:
            raise ValueError(f"Loại Vector Index không hợp lệ: {settings.VECTOR_INDEX_TYPE}")

        # 3. Khởi tạo bộ trích xuất Dense (Visual Retriever)
        self.visual_retriever = VisualRetriever(
            embedding_model=self.embedding_model,
            vector_index=self.vector_index
        )
        
        # 4. Khởi tạo chỉ mục văn bản cục bộ BM25
        self.text_index = Bm25TextSearchIndex()
        self._build_bm25_index()

        # 5. Khởi tạo bộ trích xuất lai ghép (Hybrid Retriever)
        self.hybrid_retriever = HybridRetriever(
            visual_retriever=self.visual_retriever,
            text_index=self.text_index
        )
        
        # 6. Thiết lập chiến lược lai ghép Hybrid Kis làm chiến lược chính
        self.strategy = HybridKisStrategy(hybrid_retriever=self.hybrid_retriever)
        self.qa_strategy = QaStrategy(retriever=self.hybrid_retriever)
        self.trake_strategy = TrakeStrategy(retriever=self.hybrid_retriever)
        print(f"[SearchService] [Success] Da khoi tao cau truc Hybrid Search (BM25 + {index_type.upper()}) thanh cong!")

    def _build_bm25_index(self):
        """
        Đọc file manifest.json để nạp dữ liệu text mock xây dựng chỉ mục BM25Okapi
        """
        manifest_path = settings.MANIFEST_PATH
        if not os.path.exists(manifest_path):
            print(f"[SearchService] [Warning] Khong tim thay manifest tai: {manifest_path}. Bo qua chi muc BM25.")
            return

        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)

        bm25_docs = []
        for video_key, video_info in manifest.items():
            video_title = video_info.get("video_title", "")
            total_frames = video_info.get("total_frames", 0)
            
            # Đóng gói từng frame của video thành một tài liệu văn bản
            for frame_idx in range(total_frames):
                frame_id = f"{frame_idx:04d}"
                # Mock text: Dùng tiêu đề video + số frame làm nội dung văn bản cho frame
                text_content = f"{video_title} frame {frame_id} keyframe"
                bm25_docs.append({
                    "text": text_content,
                    "metadata": {
                        "video_title": video_title,
                        "frame_id": frame_id,
                        "timestamp_seconds": float(frame_idx)
                    }
                })
        
        self.text_index.build(bm25_docs)

    def execute_textual_search(self, query_text: str, top_k: int = 100):
        start_time = time.time()
        
        # Ngữ cảnh tìm kiếm
        query_context = {
            "query": query_text,
            "top_k": top_k
        }
        
        # Chạy qua các giai đoạn xử lý của Hybrid Strategy (bao gồm RRF Fusion)
        candidates = self.strategy.retrieve(query_context)
        ranked_results = self.strategy.rerank(candidates, query_context)
        
        took_ms = int((time.time() - start_time) * 1000)
        
        # Đóng gói kết quả trả về cho UI
        payload = self.strategy.build_ui_payload(ranked_results, took_ms)
        payload["query"] = query_text
        
        return payload

    def execute_qa_search(self, query_text: str, top_k: int = 100):
        start_time = time.time()
        query_context = {"query": query_text, "top_k": top_k}
        candidates = self.qa_strategy.retrieve(query_context)
        ranked_results = self.qa_strategy.rerank(candidates, query_context)
        took_ms = int((time.time() - start_time) * 1000)
        payload = self.qa_strategy.build_ui_payload(ranked_results, took_ms)
        payload["query"] = query_text
        payload["answer"] = f"[QA Engine Mock] Dựa trên phân tích hình ảnh và từ khóa, câu trả lời cho câu hỏi '{query_text}' được định vị tại các khung hình bằng chứng bên dưới."
        return payload

    def execute_trake_search(self, query_text: str, top_k: int = 100):
        start_time = time.time()
        query_context = {"query": query_text, "top_k": top_k}
        candidates = self.trake_strategy.retrieve(query_context)
        ranked_results = self.trake_strategy.rerank(candidates, query_context)
        took_ms = int((time.time() - start_time) * 1000)
        payload = self.trake_strategy.build_ui_payload(ranked_results, took_ms)
        payload["query"] = query_text
        return payload

    def get_frame_neighbors(self, video_title: str, current_frame_id: str, window_size: int = 5):
        """
        Lấy các khung hình lân cận trước và sau của frame hiện tại để làm thanh Timeline cho UI.
        Do cắt chuẩn 1 FPS nên frame_id chính là số thứ tự index.
        """
        try:
            current_idx = int(current_frame_id)
        except ValueError:
            return {"error": "Invalid frame_id format"}

        # Tạo danh sách các index lân cận (ví dụ window=5 thì lấy trước 5 và sau 5 frame)
        start_idx = max(0, current_idx - window_size)
        end_idx = current_idx + window_size + 1 # +1 để lấy đối xứng

        neighbors = []
        for idx in range(start_idx, end_idx):
            frame_str = f"{idx:04d}"
            neighbors.append({
                "frame_id": frame_str,
                "timestamp": float(idx),
                "thumb_url": f"/media/thumbs/{video_title}/{frame_str}.jpg",
                "frame_url": f"/media/frames/{video_title}/{frame_str}.jpg",
                "is_current": (idx == current_idx)
            })

        return {
            "video_id": video_title,
            "current_frame_id": current_frame_id,
            "neighbors": neighbors
        }