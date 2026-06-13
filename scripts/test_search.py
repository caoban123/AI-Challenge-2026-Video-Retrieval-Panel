import os
os.environ["HF_HOME"] = r"D:\AIC\.cache\huggingface"
import json
import torch
import faiss
from transformers import CLIPProcessor, CLIPModel
from PIL import Image  # ◄ Thêm thư viện hiển thị ảnh chuyên dụng

def test_vector_search():
    INDEX_PATH = "data/processed/index.bin"
    METADATA_PATH = "data/processed/metadata.json"
    
    # 1. Kiểm tra xem đã có đủ dữ liệu lập chỉ mục chưa
    if not os.path.exists(INDEX_PATH) or not os.path.exists(METADATA_PATH):
        print("❌ Thiếu file index.bin hoặc metadata.json! Hãy chạy scripts/build_index.py trước.")
        return

    # 2. Đọc file chỉ mục FAISS và file danh bạ Metadata lên RAM
    print("⏳ Đang nạp cơ sở dữ liệu vector FAISS...")
    index = faiss.read_index(INDEX_PATH)
    
    with open(METADATA_PATH, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    # 3. Nạp mô hình CLIP để dịch câu chữ (Text Query) sang Vector
    print("⏳ Đang tải bộ não AI CLIP để dịch văn bản...")
    model_id = "openai/clip-vit-base-patch32"
    device = "cuda" if torch.cuda.is_available() else "cpu"
    
    model = CLIPModel.from_pretrained(model_id).to(device)
    processor = CLIPProcessor.from_pretrained(model_id)
    model.eval()

    print("\n🚀 HỆ THỐNG TÌM KIẾM SẴN SÀNG! (Gõ 'exit' để thoát)")
    
    while True:
        # Nhập từ khóa tìm kiếm bằng tiếng Anh để CLIP hiểu chuẩn nhất
        query_text = input("\n🔍 Nhập câu từ khóa tìm kiếm (Tiếng Anh): ").strip()
        if query_text.lower() == 'exit' or not query_text:
            break
            
        print(f"🧠 AI đang phân tích cú pháp: '{query_text}'...")
        
        # 4. Trích xuất Vector Đặc trưng của Văn bản (Text Embedding)
        with torch.no_grad():
            inputs = processor(text=[query_text], return_tensors="pt", padding=True).to(device)

            # Trích xuất thủ công, tránh phụ thuộc version transformers
            text_outputs = model.text_model(
                input_ids=inputs["input_ids"],
                attention_mask=inputs.get("attention_mask")
            )
            pooled_output = text_outputs.pooler_output
            text_features = model.text_projection(pooled_output)

            # Chuẩn hóa vector về độ dài bằng 1 (L2 Normalization)
            text_features = text_features / text_features.norm(p=2, dim=-1, keepdim=True)
            query_vector = text_features.cpu().numpy().astype("float32")

        # 5. Truy vấn vào FAISS để bốc ra Top 5 bức ảnh giống nhất
        TOP_K = 5
        scores, indices = index.search(query_vector, TOP_K)

        print(f"\n🎯 TOP {TOP_K} KẾT QUẢ PHÙ HỢP NHẤT:")
        print("-" * 60)
        
        best_image_path = None  # ◄ Biến tạm để ghi nhớ đường dẫn ảnh Top 1 khớp nhất
        
        for i in range(TOP_K):
            idx = indices[0][i]
            score = scores[0][i]
            
            if idx < len(metadata) and idx >= 0:
                res = metadata[idx]
                confidence = float(score) * 100
                
                print(f"Top {i+1} [Độ khớp: {confidence:.2f}%]")
                print(f"🎬 Video: {res['video_title']}")
                print(f"📸 Khung hình: {res['frame_id']} (Giây thứ {int(res['frame_id'])})")
                print(f"📁 Đường dẫn: {res['frame_path']}")
                print("-" * 60)

                # Ghi nhận lại đường dẫn của bức ảnh chuẩn nhất (Top 1)
                if i == 0:
                    best_image_path = res['frame_path']

        # 🚀 THẦN CHÚ TỰ ĐỘNG BẬT ẢNH TOP 1 LÊN MÀN HÌNH
        if best_image_path and os.path.exists(best_image_path):
            try:
                print(f"🖼️ Đang bật hiển thị ảnh kết quả tốt nhất: {os.path.basename(best_image_path)}")
                img = Image.open(best_image_path)
                img.show()  # Gọi ứng dụng xem ảnh mặc định của Windows (Photos) để hiển thị lên
            except Exception as e:
                print(f"❌ Không thể hiển thị ảnh tự động: {e}")

if __name__ == "__main__":
    test_vector_search()