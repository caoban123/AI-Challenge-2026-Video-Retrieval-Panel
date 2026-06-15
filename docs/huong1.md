# Kế Hoạch Tái Cấu Trúc Backend Theo Adapter/OOP Pattern (Hướng 1)

Mục tiêu của kế hoạch này là tái cấu trúc hệ thống tìm kiếm backend của ThunderRetrieve theo mô hình hướng đối tượng (OOP) và mẫu thiết kế Adapter (Adapter Pattern). Việc này giúp tách rời (decouple) logic nghiệp vụ khỏi các công cụ cụ thể như Qdrant Cloud và mô hình CLIP, đảm bảo tính cắm-và-chạy khi nâng cấp hệ thống trong tương lai.

## User Review Required

> [!IMPORTANT]
> **Giữ nguyên API Contract:** Toàn bộ quá trình tái cấu trúc này sẽ không làm thay đổi định dạng dữ liệu đầu vào hoặc đầu ra của các endpoint API (`/api/v1/search`, `/api/v1/frame/neighbors`). Điều này đảm bảo Frontend React UI hiện tại hoạt động bình thường mà không cần sửa đổi bất kỳ dòng mã nào.

## Proposed Changes

Chúng ta sẽ tạo các thư mục mới trong `backend/app/` và triển khai các file tương ứng.

---

### 1. Phân hệ Embedding (Mã hóa tính năng)

Tách phần xử lý mô hình AI bẻ khóa hình ảnh/văn bản thành các adapter.

#### [NEW] [base.py](file:///d:/AIC/backend/app/embeddings/base.py)
*   Định nghĩa interface trừu tượng `EmbeddingModel` với 2 phương thức:
    *   `encode_text(self, texts: list[str]) -> np.ndarray`
    *   `encode_images(self, image_paths: list[str]) -> np.ndarray`

#### [NEW] [clip.py](file:///d:/AIC/backend/app/embeddings/clip.py)
*   Triển khai lớp `ClipEmbeddingModel` kế thừa từ `EmbeddingModel`.
*   Nạp mô hình `openai/clip-vit-base-patch32` và thực hiện trích xuất vector đặc trưng trên CPU/GPU.

---

### 2. Phân hệ Index (Chỉ mục cơ sở dữ liệu)

Tách phần lưu trữ và truy vấn tương đồng vector.

#### [NEW] [base.py](file:///d:/AIC/backend/app/indexes/base.py)
*   Định nghĩa interface trừu tượng `VectorIndex` với các phương thức:
    *   `build(self, vectors, metadata: list[dict]) -> None`
    *   `search(self, query_vector, top_k: int) -> list[dict]`
    *   `save(self, path: str) -> None`
    *   `load(self, path: str) -> None`

#### [NEW] [qdrant.py](file:///d:/AIC/backend/app/indexes/qdrant.py)
*   Triển khai lớp `QdrantVectorIndex` kế thừa từ `VectorIndex`.
*   Sử dụng `QdrantClient` để thực hiện truy vấn `query_points` trên đám mây Qdrant Cloud.

#### [NEW] [faiss.py](file:///d:/AIC/backend/app/indexes/faiss.py)
*   Triển khai lớp `FaissVectorIndex` kế thừa từ `VectorIndex` để hỗ trợ tìm kiếm offline cục bộ qua file `index.bin` và `metadata.json`.

---

### 3. Phân hệ Retriever (Bộ trích xuất dữ liệu)

#### [NEW] [base.py](file:///d:/AIC/backend/app/retrievers/base.py)
*   Định nghĩa interface trừu tượng `Retriever` với phương thức:
    *   `retrieve(self, query_context: dict, top_k: int) -> list[dict]`

#### [NEW] [visual.py](file:///d:/AIC/backend/app/retrievers/visual.py)
*   Triển khai `VisualRetriever` kế thừa từ `Retriever`.
*   Nhận đối tượng `EmbeddingModel` và `VectorIndex` qua Constructor (Dependency Injection).
*   Thực hiện mã hóa câu truy vấn văn bản và gọi hàm tìm kiếm trên VectorIndex.

---

### 4. Phân hệ Strategies (Chiến lược xử lý câu hỏi)

Tách biệt các thuật toán xếp hạng và phản hồi kết quả riêng cho từng dạng đề bài.

#### [NEW] [base.py](file:///d:/AIC/backend/app/strategies/base.py)
*   Định nghĩa interface trừu tượng `TaskStrategy` với các phương thức:
    *   `retrieve(self, query_context: dict) -> list[dict]`
    *   `rerank(self, candidates: list[dict], query_context: dict) -> list[dict]`
    *   `build_ui_payload(self, results: list[dict], took_ms: int) -> dict`

#### [NEW] [textual_kis.py](file:///d:/AIC/backend/app/strategies/textual_kis.py)
*   Triển khai lớp `TextualKisStrategy` kế thừa từ `TaskStrategy`.
*   Sử dụng `VisualRetriever` để bốc dữ liệu mẫu, xếp hạng thô, và chuẩn hóa cấu trúc payload trả về cho UI.

---

### 5. Phân hệ Dịch vụ & Cấu hình (Service & Config)

#### [MODIFY] [config.py](file:///d:/AIC/backend/app/core/config.py)
*   Bổ sung thêm cấu hình quyết định loại Index nào sẽ được nạp: `VECTOR_INDEX_TYPE = "qdrant"` (hoặc `"faiss"`).

#### [MODIFY] [search.py](file:///d:/AIC/backend/app/services/search.py)
*   Tái cấu trúc lớp `SearchService` thành bộ điều phối (Orchestrator):
    *   Khởi tạo Adapter tương ứng dựa trên `settings.VECTOR_INDEX_TYPE`.
    *   Nạp chiến lược `TextualKisStrategy` mặc định.
    *   Phương thức `execute_textual_search` sẽ gọi qua chiến lược `strategy.retrieve(...)` -> `strategy.rerank(...)` -> `strategy.build_ui_payload(...)`.
    *   Giữ lại hàm bổ trợ `get_frame_neighbors` như cũ để không làm gãy giao diện timeline.

---

## Verification Plan

### Automated Tests
*   **Chạy đánh giá Recall (`run_eval.py`):**
    *   Kích hoạt server FastAPI bằng lệnh:
        ```powershell
        .venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
        ```
    *   Chạy script đánh giá:
        ```powershell
        .venv\Scripts\python.exe scripts/run_eval.py
        ```
    *   **Tiêu chí đạt:** Kết quả Recall@1, Recall@10, Recall@50 và Latency phải trả ra bình thường, không xảy ra bất kỳ lỗi Crash hay lỗi kết nối API nào. Chỉ số Recall phải khớp chính xác 100% so với chỉ số trước khi tái cấu trúc.

### Manual Verification
*   **Mở giao diện UI React:**
    *   Truy cập `http://localhost:5173`.
    *   Thực hiện gõ truy vấn tìm kiếm tiếng Anh (ví dụ: *"a football player celebrating"*).
    *   Kiểm tra việc hiển thị kết quả Grid, thanh Timeline Neighbors khi chọn ảnh, và nút bấm Submit (Dry-run) bằng bàn phím.
