# Kế Hoạch Triển Khai Hybrid Search (BM25 + Dense) & RRF Fusion (Hướng 2)

Mục tiêu của kế hoạch này là tích hợp tìm kiếm từ khóa cục bộ qua chỉ mục **BM25** (cho văn bản/OCR/Transcript) song song với tìm kiếm ngữ nghĩa **Dense Vector** (CLIP), sau đó áp dụng thuật toán **RRF (Reciprocal Rank Fusion)** để dung hợp điểm và sắp xếp lại kết quả tối ưu trước khi trả về cho UI.

## User Review Required

> [!IMPORTANT]
> **Thư viện mới:** Cần cài đặt thư viện `rank-bm25` vào môi trường ảo Python.
> **Dữ liệu Mock cho BM25:** Do chưa có tệp tin OCR/Transcript chính thức từ BTC, chúng ta sẽ lập chỉ mục văn bản tạm thời dựa trên `video_title` và thông tin metadata trong `manifest.json`. Khi BTC phát dữ liệu thật, ta chỉ cần thay đổi nguồn cấp văn bản đầu vào cho BM25.

## Proposed Changes

Chúng ta sẽ tạo các file mới và sửa đổi `SearchService` như sau:

---

### 1. Phân hệ Index (Chỉ mục văn bản BM25)

#### [NEW] [bm25.py](file:///d:/AIC/backend/app/indexes/bm25.py)
*   Triển khai lớp `Bm25TextSearchIndex` kế thừa từ `TextSearchIndex`.
*   Sử dụng thư viện `rank_bm25.BM25Okapi`.
*   Hàm `build(self, docs: list[dict])`: Nhận danh sách tài liệu chứa `text` (văn bản) và `metadata` (ví dụ: `video_title`, `frame_id`). Thực hiện tách từ (tokenize) bằng chữ thường (lowercase) và khoảng trắng, sau đó huấn luyện chỉ mục BM25Okapi.
*   Hàm `search(self, query: str, top_k: int)`: Tách từ câu query, tính toán điểm BM25 cho toàn bộ corpus, chọn ra Top-K kết quả cao nhất và ánh xạ ngược lại metadata của frame.

---

### 2. Phân hệ Retriever (Hybrid Retriever)

#### [NEW] [hybrid.py](file:///d:/AIC/backend/app/retrievers/hybrid.py)
*   Triển khai lớp `HybridRetriever` kế thừa từ `Retriever`.
*   Constructor nhận vào:
    *   `visual_retriever: Retriever` (Bộ trích xuất Dense Vector).
    *   `text_index: TextSearchIndex` (Bộ chỉ mục văn bản BM25).
*   Hàm `retrieve(self, query_context: dict, top_k: int) -> dict`:
    *   Gọi song song hoặc tuần tự:
        *   `visual_results` từ `visual_retriever.retrieve(query_context, top_k)`
        *   `text_results` từ `text_index.search(query, top_k)`
    *   Trả về một dictionary chứa cả 2 danh sách kết quả thô: `{"visual": visual_results, "text": text_results}`.

---

### 3. Phân hệ Strategies (Hybrid KIS Strategy & RRF Fusion)

#### [NEW] [hybrid_kis.py](file:///d:/AIC/backend/app/strategies/hybrid_kis.py)
*   Triển khai lớp `HybridKisStrategy` kế thừa từ `TaskStrategy`.
*   Constructor nhận vào `hybrid_retriever: HybridRetriever`.
*   Hàm `retrieve(self, query_context: dict) -> dict`: Gọi `hybrid_retriever.retrieve(...)` để bốc dữ liệu thô từ cả 2 nhánh.
*   Hàm `rerank(self, candidates: dict, query_context: dict) -> list[dict]`:
    *   Áp dụng thuật toán **RRF (Reciprocal Rank Fusion)** với hằng số $k = 60$.
    *   Mỗi ứng viên được nhận dạng duy nhất bằng khóa `(video_id, frame_id)`.
    *   Tính điểm số RRF cho từng ứng viên xuất hiện trong danh sách `visual` và `text`:
        $$Score_{RRF}(d) = \frac{1}{60 + Rank_{visual}(d)} + \frac{1}{60 + Rank_{text}(d)}$$
    *   Sắp xếp lại toàn bộ ứng viên theo điểm $Score_{RRF}$ giảm dần.
    *   Cập nhật điểm số dung hợp vào trường `score` của kết quả và ghi nhận các trọng số đóng góp (`visual_score`, `text_score`) trong cấu trúc `evidence`.
*   Hàm `build_ui_payload(self, results: list[dict], took_ms: int) -> dict`: Đóng gói payload chuẩn trả về cho UI.

---

### 4. Phân hệ Dịch vụ & Cấu hình (Service & Config)

#### [MODIFY] [config.py](file:///d:/AIC/backend/app/core/config.py)
*   Bổ sung cấu hình đường dẫn tới tệp tin manifest dùng để dựng corpus BM25: `MANIFEST_PATH = r"D:\AIC\data\processed\manifest.json"`.

#### [MODIFY] [search.py](file:///d:/AIC/backend/app/services/search.py)
*   Trong constructor `__init__`:
    *   Đọc file `manifest.json` để chuẩn bị danh sách văn bản mock cho BM25 (dùng tiêu đề video kết hợp thông tin frame làm mô tả).
    *   Khởi tạo `Bm25TextSearchIndex` và build chỉ mục BM25.
    *   Khởi tạo `HybridRetriever` (bọc `VisualRetriever` và `Bm25TextSearchIndex`).
    *   Khởi tạo chiến lược `HybridKisStrategy` làm chiến lược tìm kiếm chính.
*   Hàm `execute_textual_search` sẽ sử dụng luồng xử lý mới của `HybridKisStrategy`.

---

## Verification Plan

### Automated Tests
1.  **Cài đặt thư viện:** `.venv\Scripts\python.exe -m pip install rank-bm25`.
2.  **Khởi động lại server:** `.venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload`

### Manual Verification
*   Truy cập Web UI tại `http://localhost:5173`.
*   Gõ thử từ khóa xuất hiện trong tiêu đề video (ví dụ: *"Canada"* hoặc *"Hàn Quốc"*).
*   **Tiêu chí đạt:** Kết quả tìm kiếm theo từ khóa chính xác từ BM25 phải xuất hiện ở thứ hạng rất cao nhờ RRF Fusion, cải thiện rõ rệt so với việc chỉ tìm kiếm bằng Dense Vector CLIP.
