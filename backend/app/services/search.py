import torch
import time
from qdrant_client import QdrantClient
from transformers import CLIPProcessor, CLIPModel
from backend.app.core.config import settings

class SearchService:
    def __init__(self):
        print("⏳ [Backend] Đang kết nối Qdrant Cloud...")
        self.client = QdrantClient(url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY)
        
        print("⏳ [Backend] Đang nạp mô hình CLIP bẻ khóa văn bản...")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = CLIPModel.from_pretrained(settings.CLIP_MODEL_ID).to(self.device)
        self.processor = CLIPProcessor.from_pretrained(settings.CLIP_MODEL_ID)
        self.model.eval()
        print(f"🚀 [Backend] Hệ thống AI sẵn sàng trên: {self.device.upper()}")

    def execute_textual_search(self, query_text: str, top_k: int = 100):
        start_time = time.time()
        
        # 1. Trích xuất Vector của Văn bản (Text Embedding) thủ công chống lỗi version
        with torch.no_grad():
            inputs = self.processor(text=[query_text], return_tensors="pt", padding=True).to(self.device)
            text_outputs = self.model.text_model(
                input_ids=inputs["input_ids"],
                attention_mask=inputs.get("attention_mask")
            )
            pooled_output = text_outputs.pooler_output
            text_features = self.model.text_projection(pooled_output)

            # Chuẩn hóa L2 Normalization
            text_features = text_features / text_features.norm(p=2, dim=-1, keepdim=True)
            query_vector = text_features.cpu().numpy().astype("float32").flatten().tolist()

        # 2. Gọi API query_points thế hệ mới của Qdrant Cloud
        response = self.client.query_points(
            collection_name=settings.COLLECTION_NAME,
            query=query_vector,
            limit=top_k
        )
        
        # 3. Đóng gói dữ liệu trả về theo đúng Schema chuẩn của đồ án P0 Spec
        formatted_results = []
        for idx, hit in enumerate(response.points):
            payload = hit.payload
            confidence = float(hit.score) * 100
            
            formatted_results.append({
                "rank": idx + 1,
                "video_id": payload.get("video_title"),  # Map map id/title chuẩn
                "frame_id": payload.get("frame_id"),
                "timestamp": float(payload.get("timestamp_seconds", 0)),
                "score": float(hit.score),
                # Các URL tĩnh này sau này FastAPI sẽ serve để Frontend bốc ảnh hiển thị
                "thumb_url": f"/media/thumbs/{payload.get('video_title')}/{payload.get('frame_id')}.jpg",
                "frame_url": f"/media/frames/{payload.get('video_title')}/{payload.get('frame_id')}.jpg",
                "video_url": f"/media/videos/{payload.get('video_title')}.mp4",
                "evidence": {
                    "visual_score": float(hit.score),
                    "text_score": None,
                    "ocr_score": None,
                    "asr_score": None
                }
            })
            
        took_ms = int((time.time() - start_time) * 1000)
        
        return {
            "query": query_text,
            "query_type": "textual_kis",
            "strategy": "TextualKisStrategy",
            "took_ms": took_ms,
            "results": formatted_results
        }
    # (Giữ nguyên các hàm cũ, thêm hàm này vào cuối class SearchService)

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