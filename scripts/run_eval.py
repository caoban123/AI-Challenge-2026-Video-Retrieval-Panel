import json
import requests
import time
import os

API_SEARCH_URL = "http://127.0.0.1:8000/api/v1/search"
EVAL_SET_PATH = r"D:\AIC\eval\eval_set.jsonl"

def calculate_recall_at_k(results, ground_truth, k):
    """
    Tính xem đáp án đúng (Ground Truth) có nằm trong Top K kết quả trả về hay không.
    """
    top_k_results = results[:k]
    for item in top_k_results:
        if item["video_id"] == ground_truth["video_id"] and item["frame_id"] == ground_truth["frame_id"]:
            return 1 # Tìm thấy
    return 0 # Thất bại

def main():
    if not os.path.exists(EVAL_SET_PATH):
        print(f"❌ Không tìm thấy file bộ đề đánh giá tại: {EVAL_SET_PATH}")
        return

    print("📊 [Eval Engine] Đang khởi động trạm chấm điểm thuật toán Baseline P0...")
    
    total_queries = 0
    success_at_1 = 0
    success_at_10 = 0
    success_at_50 = 0
    total_latency_ms = 0

    with open(EVAL_SET_PATH, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            
            data = json.loads(line)
            query_id = data["query_id"]
            query_text = data["query_text"]
            gt = data["ground_truth"]
            
            total_queries += 1
            
            # Giả lập hành vi bắn API giống hệt như trên Frontend React UI
            try:
                start_time = time.time()
                response = requests.post(API_SEARCH_URL, json={"query": query_text, "top_k": 50})
                latency_ms = int((time.time() - start_time) * 1000)
                total_latency_ms += latency_ms
                
                if response.status_code == 200:
                    search_results = response.json().get("results", [])
                    
                    # Tính toán Recall tại các mốc chí mạng: @1, @10, @50
                    rec_1 = calculate_recall_at_k(search_results, gt, 1)
                    rec_10 = calculate_recall_at_k(search_results, gt, 10)
                    rec_50 = calculate_recall_at_k(search_results, gt, 50)
                    
                    success_at_1 += rec_1
                    success_at_10 += rec_10
                    success_at_50 += rec_50
                    
                    print(f"✅ [{query_id}] Latency: {latency_ms}ms | Found in Top-1: {bool(rec_1)} | Top-10: {bool(rec_10)} | Top-50: {bool(rec_50)}")
                else:
                    print(f"⚠️ [{query_id}] API Backend báo lỗi Status: {response.status_code}")
            except Exception as e:
                print(f"❌ [{query_id}] Không thể kết nối đến API Server FastAPI. Hãy chắc chắn Server đang chạy!")
                return

    if total_queries == 0:
        print("Mảng câu hỏi trống rỗng!")
        return

    # --- ĐỔ ĐÁP ÁN THỐNG KÊ TOÁN HỌC ---
    mean_latency = total_latency_ms / total_queries
    recall_at_1 = (success_at_1 / total_queries) * 100
    recall_at_10 = (success_at_10 / total_queries) * 100
    recall_at_50 = (success_at_50 / total_queries) * 100

    print("\n" + "="*50)
    print("🏆 BÁO CÁO CHỈ SỐ SỨC MẠNH THUẬT TOÁN P0 BASELINE")
    print("="*50)
    print(f"🔹 Tổng số câu hỏi giải đề  : {total_queries}")
    print(f"⏱️ Độ trễ phản hồi trung bình : {mean_latency:.2f} ms")
    print(f"🎯 Recall@1  (Chính xác tuyệt đối) : {recall_at_1:.2f}%")
    print(f"🎯 Recall@10 (Nằm trên trang đầu)  : {recall_at_10:.2f}%")
    print(f"🎯 Recall@50 (Lọt vào danh sách vớt): {recall_at_50:.2f}%")
    print("="*50)
    print("💡 Nhận xét chiến thuật: Để cải thiện Recall@1, giai đoạn P1 team cần bổ sung nhãn OCR và thực hiện kỹ thuật Query Expansion bằng LLM.")

if __name__ == "__main__":
    main()