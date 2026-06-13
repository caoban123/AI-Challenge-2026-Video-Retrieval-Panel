import os
import json
import numpy as np
import faiss

def build_faiss_index():
    MANIFEST_PATH = "data/processed/manifest.json"
    INDEX_OUTPUT_PATH = "data/processed/index.bin"
    
    if not os.path.exists(MANIFEST_PATH):
        print("❌ Không tìm thấy file manifest.json! Hãy chạy các bước trước.")
        return

    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    all_vectors = []
    metadata = []  # Lưu danh bạ: Vector thứ i thuộc về video nào, khung hình thứ mấy

    print("⏳ Đang gom các vector đặc trưng từ file .npy...")
    
    for video_key, video_info in manifest.items():
        feature_path = video_info.get("feature_path")
        
        if not feature_path or not os.path.exists(feature_path):
            print(f"⚠️ Bỏ qua {video_key} do chưa có file vector.")
            continue
            
        # Nạp ma trận vector của video này lên RAM
        video_matrix = np.load(feature_path) # Kích thước: (Số_ảnh, 512)
        
        for frame_idx in range(len(video_matrix)):
            all_vectors.append(video_matrix[frame_idx])
            
            # Chuẩn hóa đường dẫn thư mục về dạng gạch xuôi trước khi nối chuỗi
            clean_frame_dir = video_info['frame_dir_path'].replace("\\", "/")
            clean_thumb_dir = video_info['thumb_dir_path'].replace("\\", "/")
            
            # Lưu metadata sạch
            metadata.append({
                "video_title": video_info["video_title"],
                "frame_id": f"{frame_idx:04d}",
                "frame_path": f"{clean_frame_dir}/{frame_idx:04d}.jpg",
                "thumb_path": f"{clean_thumb_dir}/{frame_idx:04d}.jpg"
            })

    if not all_vectors:
        print("❌ Không có dữ liệu vector nào để lập chỉ mục!")
        return

    # Chuyển thành ma trận numpy chuẩn float32 để FAISS xử lý
    index_matrix = np.array(all_vectors, dtype=np.float32)
    dimension = index_matrix.shape[1] # Kích thước vector (CLIP ViT-B/32 luôn là 512)

    print(f"📦 Tổng số lượng khung hình nạp vào Index: {len(index_matrix)}")
    print(f"📐 Số chiều không gian vector: {dimension}")

    # Khởi tạo Index phẳng tính khoảng cách bằng tích vô hướng (Inner Product) 
    # Do vector đã được chuẩn hóa L2 ở Card 4, Inner Product chính là Cosine Similarity!
    index = faiss.IndexFlatIP(dimension)
    
    # Nạp toàn bộ ma trận dữ liệu vào cấu trúc tìm kiếm của FAISS
    index.add(index_matrix)

    # Lưu file chỉ mục nhị phân xuống ổ cứng
    faiss.write_index(index, INDEX_OUTPUT_PATH)
    
    # Lưu kèm file metadata để Backend tra cứu thông tin hiển thị UI
    METADATA_PATH = "data/processed/metadata.json"
    with open(METADATA_PATH, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=4, ensure_ascii=False)

    print(f"✅ HOÀN THÀNH XUẤT SẮC CARD 5!")
    print(f"📁 File chỉ mục lưu tại: {INDEX_OUTPUT_PATH}")
    print(f"📁 File bản đồ tra cứu lưu tại: {METADATA_PATH}")

if __name__ == "__main__":
    build_faiss_index()