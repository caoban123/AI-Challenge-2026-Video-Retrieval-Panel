from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from backend.app.indexes.base import VectorIndex

class QdrantVectorIndex(VectorIndex):
    def __init__(self, url: str, api_key: str, collection_name: str):
        self.url = url
        self.api_key = api_key
        self.collection_name = collection_name
        print(f"[QdrantIndex] Dang ket noi toi Qdrant Cloud: {url}...")
        self.client = QdrantClient(url=url, api_key=api_key)
        print(f"[QdrantIndex] Ket noi Qdrant Cloud thanh cong!")

    def build(self, vectors, metadata: list[dict]) -> None:
        """
        Nạp ma trận vector và danh sách metadata lên Qdrant Cloud.
        """
        print(f"[QdrantIndex] Khoi tao hoac xoa sach Collection '{self.collection_name}'...")
        dimension = len(vectors[0]) if len(vectors) > 0 else 512
        self.client.recreate_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(size=dimension, distance=Distance.COSINE)
        )
        
        points = []
        for idx, (vector, meta) in enumerate(zip(vectors, metadata)):
            points.append(PointStruct(id=idx, vector=vector.tolist(), payload=meta))
            
        BATCH_SIZE = 50
        for i in range(0, len(points), BATCH_SIZE):
            batch = points[i:i + BATCH_SIZE]
            self.client.upsert(collection_name=self.collection_name, points=batch)
        print(f"[QdrantIndex] Da nap thanh cong {len(points)} points len Qdrant Cloud.")

    def search(self, query_vector: list[float], top_k: int) -> list[dict]:
        response = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            limit=top_k
        )
        
        results = []
        for idx, hit in enumerate(response.points):
            payload = hit.payload
            results.append({
                "rank": idx + 1,
                "video_id": payload.get("video_title"),
                "frame_id": payload.get("frame_id"),
                "timestamp": float(payload.get("timestamp_seconds", 0)),
                "score": float(hit.score),
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
        return results

    def save(self, path: str) -> None:
        # Qdrant Cloud lưu trực tiếp trên cloud, không cần lưu file cục bộ
        pass

    def load(self, path: str) -> None:
        # Qdrant Cloud tự load từ server, không cần load file cục bộ
        pass
