import os
import json
import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

def push_data_to_qdrant():
    MANIFEST_PATH = "data/processed/manifest.json"
    
    # Cấu hình thông tin Qdrant Cloud của Bản
    QDRANT_URL = "https://9fd23c68-a180-4539-936d-0b1da06d5271.sa-east-1-0.aws.cloud.qdrant.io"
    QDRANT_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIiwic3ViamVjdCI6ImFwaS1rZXk6NDVlZDM0NzEtMzc4My00MzMwLTk3YzItZjI4YzNlZTAxNzY3In0.F18gYg4KdSDHdU3Zx6X9X6OZ75tTjmk5sjff3jkK18E"
    COLLECTION_NAME = "aic_baseline_collection"

    if not os.path.exists(MANIFEST_PATH):
        print("❌ Không tìm thấy file manifest.json! Hãy chạy scripts/build_manifest.py trước.")
        return

    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    # Khởi tạo kết nối bảo mật tới Qdrant Cloud
    print("⏳ Đang kết nối tới Qdrant Cloud...")
    client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

    # Khởi tạo hoặc làm sạch Collection cũ (Vector 512 chiều, đo khoảng cách bằng Cosine)
    print(f"📦 Đang khởi tạo Collection '{COLLECTION_NAME}' trên Cloud...")
    client.recreate_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=512, distance=Distance.COSINE),
    )

    points = []
    global_id = 0  

    print("⏳ Đang bốc tách dữ liệu vector và đóng gói Payload...")
    for video_key, video_info in manifest.items():
        feature_path = video_info.get("feature_path")
        if not feature_path or not os.path.exists(feature_path):
            print(f"⚠️ Bỏ qua {video_key} do chưa trích xuất file vector .npy")
            continue
            
        video_matrix = np.load(feature_path)  
        
        for frame_idx in range(len(video_matrix)):
            vector = video_matrix[frame_idx].tolist()  
            
            # Chuẩn hóa đường dẫn về gạch xuôi sạch sẽ
            clean_frame_path = f"{video_info['frame_dir_path']}/{frame_idx:04d}.jpg".replace("\\", "/")
            clean_thumb_path = f"{video_info['thumb_dir_path']}/{frame_idx:04d}.jpg".replace("\\", "/")
            
            # Khởi tạo gói Payload chứa thông tin tra cứu thông minh
            payload = {
                "video_title": video_info["video_title"],
                "frame_id": f"{frame_idx:04d}",
                "timestamp_seconds": frame_idx, # Do cắt chuẩn 1 fps nên frame_idx chính là số giây
                "frame_path": clean_frame_path,
                "thumb_path": clean_thumb_path
            }
            
            points.append(PointStruct(id=global_id, vector=vector, payload=payload))
            global_id += 1

    if not points:
        print("❌ Không có dữ liệu để upload.")
        return

    print(f"🚀 Bắt đầu bắn {len(points)} điểm dữ liệu lên Qdrant Cloud...")
    
    # Chia nhỏ dữ liệu thành các Batch 50 phần tử để đẩy qua internet cho ổn định
    BATCH_SIZE = 50
    for i in range(0, len(points), BATCH_SIZE):
        batch = points[i:i + BATCH_SIZE]
        client.upsert(collection_name=COLLECTION_NAME, points=batch)
        print(f"✅ Đã upload thành công cấu trúc points từ {i} đến {i + len(batch) - 1}")

    print(f"\n🎉 THÀNH CÔNG! Toàn bộ kho vector đã nằm an toàn trên Qdrant Cloud.")

if __name__ == "__main__":
    push_data_to_qdrant()