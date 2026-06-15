import torch
import numpy as np
from PIL import Image
from transformers import CLIPProcessor, CLIPModel
from backend.app.embeddings.base import EmbeddingModel

from functools import lru_cache

class ClipEmbeddingModel(EmbeddingModel):
    def __init__(self, model_id: str = "openai/clip-vit-base-patch32"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"[ClipEmbedding] Dang tai mo hinh CLIP ({model_id}) tren {self.device.upper()}...")
        self.model = CLIPModel.from_pretrained(model_id).to(self.device)
        self.processor = CLIPProcessor.from_pretrained(model_id)
        self.model.eval()
        print(f"[ClipEmbedding] Da nap mo hinh CLIP thanh cong!")

    @lru_cache(maxsize=512)
    def _encode_single_text_cached(self, text: str) -> bytes:
        with torch.no_grad():
            inputs = self.processor(text=[text], return_tensors="pt", padding=True).to(self.device)
            text_outputs = self.model.text_model(
                input_ids=inputs["input_ids"],
                attention_mask=inputs.get("attention_mask")
            )
            pooled_output = text_outputs.pooler_output
            text_features = self.model.text_projection(pooled_output)
            # L2 Normalize
            text_features = text_features / text_features.norm(p=2, dim=-1, keepdim=True)
            return text_features.cpu().numpy().astype("float32").tobytes()

    def encode_text(self, texts: list[str]) -> np.ndarray:
        if len(texts) == 1:
            # Tối ưu hóa: Lấy kết quả từ LRU cache nếu chỉ mã hóa 1 câu truy vấn
            vector_bytes = self._encode_single_text_cached(texts[0])
            return np.frombuffer(vector_bytes, dtype=np.float32).reshape(1, -1)

        with torch.no_grad():
            inputs = self.processor(text=texts, return_tensors="pt", padding=True).to(self.device)
            text_outputs = self.model.text_model(
                input_ids=inputs["input_ids"],
                attention_mask=inputs.get("attention_mask")
            )
            pooled_output = text_outputs.pooler_output
            text_features = self.model.text_projection(pooled_output)
            # L2 Normalize
            text_features = text_features / text_features.norm(p=2, dim=-1, keepdim=True)
            return text_features.cpu().numpy().astype("float32")

    def encode_images(self, image_paths: list[str]) -> np.ndarray:
        embeddings = []
        with torch.no_grad():
            for path in image_paths:
                image = Image.open(path).convert("RGB")
                inputs = self.processor(images=image, return_tensors="pt").to(self.device)
                vision_outputs = self.model.vision_model(pixel_values=inputs["pixel_values"])
                pooled_output = vision_outputs.pooler_output
                image_features = self.model.visual_projection(pooled_output)
                # L2 Normalize
                image_features = image_features / image_features.norm(p=2, dim=-1, keepdim=True)
                embeddings.append(image_features.cpu().numpy().flatten())
        return np.array(embeddings, dtype=np.float32)
