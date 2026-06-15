import os
import sys
import time

# Thêm thư mục gốc vào sys.path để nhận diện gói backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Thiết lập cache HF
os.environ["HF_HOME"] = r"D:\AIC\.cache\huggingface"

from backend.app.services.search import SearchService

def main():
    # Ep vector index sang FAISS de test chay offline cuc bo
    from backend.app.core.config import settings
    settings.VECTOR_INDEX_TYPE = "faiss"

    print("[Info] Khoi tao SearchService (Tai CLIP model, index.bin, BM25) dung FAISS...")
    service = SearchService()
    
    query = "soccer match stadium"
    
    # Lần chạy 1: Cold start (chưa có cache)
    start_1 = time.perf_counter()
    res_1 = service.execute_textual_search(query, top_k=5)
    took_1 = (time.perf_counter() - start_1) * 1000
    print(f"\n[Run 1 - Cold] Query: '{query}' -> Took: {took_1:.2f} ms")
    
    # Lần chạy 2: Hot start (đã có cache)
    start_2 = time.perf_counter()
    res_2 = service.execute_textual_search(query, top_k=5)
    took_2 = (time.perf_counter() - start_2) * 1000
    print(f"[Run 2 - Hot] Query: '{query}' -> Took: {took_2:.2f} ms")
    
    # Xác thực kết quả
    assert took_2 < took_1, "Hot run phai nhanh hon Cold run khi co cache!"
    assert len(res_1["results"]) == len(res_2["results"]), "Du lieu ket qua khong khop!"
    
    print("\n[Success] Xac thuc cache hoat dong hoan hao!")
    print(f"Cold run: {took_1:.2f} ms")
    print(f"Hot run: {took_2:.2f} ms (Nhanh hon gap {took_1 / took_2:.1f} lan!)")

if __name__ == "__main__":
    main()
