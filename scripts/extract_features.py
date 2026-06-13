import os
import json
import glob
import torch
from PIL import Image
import numpy as np
from transformers import CLIPProcessor, CLIPModel

def extract_all_features():
    # 1. Định nghĩa các đường dẫn cấu hình chuẩn P0
    MANIFEST_PATH = "data/processed/manifest.json"
    FEATURES_DIR = "data/processed/features"
    os.makedirs(FEATURES_DIR, exist_ok=True)

    # Kiểm tra xem file manifest.json (Card 3) đã tồn tại chưa
    if not os.path.exists(MANIFEST_PATH):
        print("❌ Không tìm thấy file manifest.json! Hãy chạy scripts/build_manifest.py trước.")
        return

    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    # 2. Khởi tạo mô hình CLIP (Tự động tải trọng số nhẹ từ Hugging Face nếu chạy lần đầu)
    print("⏳ Đang tải mô hình CLIP (ViT-B/32)...")
    model_id = "openai/clip-vit-base-patch32"
    device = "cuda" if torch.cuda.is_available() else "cpu"

    model = CLIPModel.from_pretrained(model_id).to(device)
    processor = CLIPProcessor.from_pretrained(model_id)
    model.eval()  # Chuyển mô hình sang chế độ Inference (đánh giá)
    print(f"🚀 Đã nạp mô hình thành công trên thiết bị: {device.upper()}")

    # 3. Duyệt qua từng video có trong sổ cái manifest
    for video_key, video_info in manifest.items():
        video_title = video_info["video_title"]
        frame_dir = video_info["frame_dir_path"]

        print(f"\n🎬 Đang xử lý trích xuất đặc trưng cho video: {video_title}")

        # Lấy danh sách tất cả ảnh .jpg được sắp xếp theo đúng thứ tự khung hình
        frame_files = sorted(glob.glob(os.path.join(frame_dir, "*.jpg")))

        if not frame_files:
            print(f"⚠️ Thư mục {frame_dir} rỗng, bỏ qua video này.")
            continue

        video_embeddings = []

        # Tiến hành trích xuất vector cho từng bức ảnh
        with torch.no_grad():  # Tắt tính toán gradient để giải phóng RAM/VRAM
            for frame_path in frame_files:
                try:
                    # Đọc ảnh bằng thư viện PIL (hỗ trợ đường dẫn Unicode tiếng Việt rất tốt)
                    image = Image.open(frame_path).convert("RGB")

                    # Tiền xử lý ảnh qua bộ chuẩn hóa của CLIP
                    inputs = processor(images=image, return_tensors="pt").to(device)

                    # Trích xuất tính năng hình ảnh thủ công (tránh phụ thuộc version transformers
                    # vì get_image_features() ở một số bản trả về object BaseModelOutputWithPooling
                    # thay vì Tensor trực tiếp)
                    vision_outputs = model.vision_model(pixel_values=inputs["pixel_values"])
                    pooled_output = vision_outputs.pooler_output
                    image_features = model.visual_projection(pooled_output)

                    # Chuẩn hóa vector về độ dài bằng 1 (L2 Normalization) để tính khoảng cách Cosine chuẩn xác hơn
                    image_features = image_features / image_features.norm(p=2, dim=-1, keepdim=True)

                    # Chuyển vector từ Tensor về dạng mảng numpy thông thường
                    embedding_np = image_features.cpu().numpy().flatten()
                    video_embeddings.append(embedding_np)

                except Exception as e:
                    print(f"❌ Lỗi khi xử lý ảnh {os.path.basename(frame_path)}: {e}")

        if video_embeddings:
            # Chuyển danh sách thành một ma trận numpy có kích thước: (Số_lượng_ảnh, 512)
            video_matrix = np.array(video_embeddings, dtype=np.float32)

            # Lưu ma trận vector này thành file nhị phân .npy để nạp cực nhanh vào Vector DB (Card 5)
            feature_file_path = os.path.join(FEATURES_DIR, f"{video_key}.npy")
            np.save(feature_file_path, video_matrix)

            # Cập nhật ngược lại đường dẫn file vector vào file manifest để Backend nắm thông tin
            manifest[video_key]["feature_path"] = feature_file_path.replace("\\", "/")
            print(f"✅ Đã lưu ma trận vector {video_matrix.shape} tại: {feature_file_path}")

    # Ghi đè lại manifest.json để cập nhật thêm trường "feature_path"
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=4, ensure_ascii=False)
    print("\n🎉 HOÀN THÀNH CARD 4: Toàn bộ ảnh mẫu đã được bẻ khóa thành Vector Đặc Trưng!")

if __name__ == "__main__":
    extract_all_features()