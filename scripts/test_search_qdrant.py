import os
os.environ["HF_HOME"] = r"D:\AIC\.cache\huggingface"

import torch
from qdrant_client import QdrantClient
from transformers import CLIPProcessor, CLIPModel
from PIL import Image

def search_on_qdrant_cloud():
    # Cấu hình thông tin kết nối mây của Bản
    QDRANT_URL = "https://9fd23c68-a180-4539-936d-0b1da06d5271.sa-east-1-0.aws.cloud.qdrant.io"
    QDRANT_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIiwic3ViamVjdCI6ImFwaS1rZXk6NDVlZDM0NzEtMzc4My00MzMwLTk3YzItZjI4YzNlZTAxNzY3In0.F18gYg4KdSDHdU3Zx6X9X6OZ75tTjmk5sjff3jkK18E"
    COLLECTION_NAME = "aic_baseline_collection"

    print("⏳ Đang kết nối tới máy chủ Qdrant Cloud...")
    client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

    print("⏳ Đang tải mô hình CLIP bẻ khóa văn bản...")
    model_id = "openai/clip-vit-base-patch32"
    device = "cuda" if torch.cuda.is_available() else "cpu"
    
    model = CLIPModel.from_pretrained(model_id).to(device)
    processor = CLIPProcessor.from_pretrained(model_id)
    model.eval()

    print("\n🚀 LÕI TÌM KIẾM MÂY QDRANT SẴN SÀNG! (Gõ 'exit' để thoát)")
    
    while True:
        query_text = input("\n🔍 Nhập từ khóa tìm kiếm (Tiếng Anh): ").strip()
        if query_text.lower() == 'exit' or not query_text:
            break
            
        print(f"🧠 AI đang phân tích ngữ nghĩa: '{query_text}'...")
        
        with torch.no_grad():
            inputs = processor(text=[query_text], return_tensors="pt", padding=True).to(device)
            text_outputs = model.text_model(input_ids=inputs["input_ids"], attention_mask=inputs.get("attention_mask"))
            pooled_output = text_outputs.pooler_output
            text_features = model.text_projection(pooled_output)
            
            # Chuẩn hóa L2
            text_features = text_features / text_features.norm(p=2, dim=-1, keepdim=True)
            query_vector = text_features.cpu().numpy().astype("float32").flatten().tolist()

        # Gọi API của Qdrant Cloud để thực hiện tìm kiếm Vector tương đồng
        # Gọi API query_points thế hệ mới của Qdrant Cloud
        TOP_K = 5
        response = client.query_points(
            collection_name=COLLECTION_NAME,
            query=query_vector,  # Truyền trực tiếp list vector vào
            limit=TOP_K
        )
        
        # Bốc tách danh sách kết quả trả về từ cấu trúc Response mới
        search_results = response.points

        print(f"\n🎯 TOP {TOP_K} KẾT QUẢ TỪ QDRANT CLOUD:")
        print("-" * 60)
        
        best_image_path = None

        for idx, hit in enumerate(search_results):
            # Qdrant tự động trả về toàn bộ thông tin nằm trong payload cực kỳ tiện lợi
            res = hit.payload 
            # Đổi khoảng cách Cosine Similarity về hệ phần trăm tương đồng
            confidence = float(hit.score) * 100
            
            print(f"Top {idx+1} [Độ khớp: {confidence:.2f}%]")
            print(f"🎬 Video: {res['video_title']}")
            print(f"📸 Khung hình: {res['frame_id']} (Vị trí giây thứ: {res['timestamp_seconds']}s)")
            print(f"📁 Đường dẫn ảnh local: {res['frame_path']}")
            print("-" * 60)

            if idx == 0:
                best_image_path = res['frame_path']

        # Bật hiển thị ảnh Top 1 lên màn hình Windows nếu file local tồn tại
        if best_image_path and os.path.exists(best_image_path):
            try:
                print(f"🖼️ Đang hiển thị trực quan ảnh tốt nhất...")
                img = Image.open(best_image_path)
                img.show()
            except Exception as e:
                print(f"❌ Không thể mở hiển thị ảnh: {e}")

if __name__ == "__main__":
    search_on_qdrant_cloud()