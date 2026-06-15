# Lộ Trình Phát Triển & Chuẩn Bị Hệ Thống Trước Cuộc Thi (Pre-Contest Roadmap)

Tài liệu này tổng hợp 4 hướng đi chiến lược nhằm tối ưu hóa hạ tầng và thuật toán của hệ thống **Video Evidence Retrieval** (ThunderRetrieve) trong thời gian chờ Ban tổ chức (BTC) công bố tập dữ liệu chính thức.

---

## 1. Hướng 1: Tái Cấu Trúc Backend Theo Adapter/OOP Pattern (Card 17)

### Rationale (Lý do thực hiện)
Hiện tại, file `backend/app/services/search.py` đang kết nối trực tiếp (tight coupling) với thư viện Qdrant và mô hình CLIP. Điều này vi phạm nguyên tắc thiết kế được đề xuất trong tài liệu thiết kế hệ thống. Để hệ thống có thể dễ dàng hoán đổi mô hình học máy (CLIP ↔ SigLIP) hoặc cơ sở dữ liệu vector (Qdrant ↔ FAISS/Milvus), backend cần được tái cấu trúc theo mô hình OOP/Adapter.

### Danh sách nhiệm vụ
*   **Tạo cấu trúc thư mục mới:**
    *   `backend/app/embeddings/`: Chứa các lớp mã hóa dữ liệu văn bản và hình ảnh.
    *   `backend/app/indexes/`: Chứa các lớp tương tác với cơ sở dữ liệu chỉ mục (FAISS, Qdrant).
    *   `backend/app/retrievers/`: Chứa các bộ trích xuất dữ liệu kết hợp.
    *   `backend/app/strategies/`: Chứa các chiến lược xử lý câu hỏi chuyên biệt (KIS, QA, TRAKE).
*   **Định nghĩa các lớp Interface (Base Class):**
    *   `EmbeddingModel`: Khai báo phương thức `encode_text` và `encode_images`.
    *   `VectorIndex`: Khai báo phương thức `build`, `search`, `save`, và `load`.
    *   `TextSearchIndex`: Khai báo phương thức `build` và `search` dành cho BM25.
    *   `TaskStrategy`: Khai báo các phương thức `retrieve`, `rerank`, `build_ui_payload`, và `format_submission`.
*   **Viết các lớp Adapter cụ thể:**
    *   `ClipEmbeddingModel` kế thừa từ `EmbeddingModel`.
    *   `QdrantVectorIndex` kế thừa từ `VectorIndex`.
    *   `FaissVectorIndex` kế thừa từ `VectorIndex`.
    *   `TextualKisStrategy` kế thừa từ `TaskStrategy`.

---

## 2. Hướng 2: Triển Khai Hybrid Search (BM25 + Dense) & Fusion (RRF)

### Rationale (Lý do thực hiện)
Tìm kiếm bằng Vector ngữ nghĩa (Dense Search) rất mạnh trong việc hiểu ngữ cảnh chung nhưng rất yếu khi truy vấn các thực thể chính xác như số áo cầu thủ, tên biển hiệu, logo hoặc thương hiệu xuất hiện trong video. Bằng cách kết hợp **BM25 Text Search** (dành cho OCR/Transcript) và xếp hạng lại bằng thuật toán **RRF (Reciprocal Rank Fusion)**, ta sẽ tối ưu hóa được Recall và độ chính xác của hệ thống.

### Danh sách nhiệm vụ
*   **Cài đặt thư viện phụ thuộc:** Thêm thư viện `rank-bm25` vào môi trường ảo Python.
*   **Xây dựng bộ tìm kiếm văn bản:**
    *   Viết lớp `Bm25TextSearchIndex` kế thừa từ `TextSearchIndex`.
    *   Trong khi chưa có dữ liệu OCR/Transcript chính thức, thực hiện index tạm tiêu đề video (`video_title`) hoặc tên file ảnh mẫu từ file `manifest.json`.
*   **Xây dựng bộ Hybrid Retriever:**
    *   Tạo lớp `HybridRetriever` nhận hai chỉ mục: `VectorIndex` và `TextSearchIndex`.
    *   Gọi song song kết quả tìm kiếm từ cả hai chỉ mục cho mỗi câu truy vấn.
*   **Triển khai thuật toán RRF:**
    *   Gộp kết quả tìm kiếm và tính điểm số mới theo công thức:
        $$RRF(d) = \sum_{m \in M} \frac{1}{k + r_m(d)}$$
        *(Trong đó $r_m(d)$ là thứ hạng của tài liệu $d$ trong danh sách kết quả thứ $m$, mặc định $k = 60$).*
    *   Xếp hạng lại toàn bộ danh sách kết quả dựa trên điểm số RRF và trả về Top-K cho UI.

---

## 3. Hướng 3: Hoàn Thiện Stubs & UI Routing Cho Mọi Dạng Câu Hỏi

### Rationale (Lý do thực hiện)
Cuộc thi AI Challenge có nhiều dạng câu hỏi thi đấu khác nhau (KIS văn bản, KIS hình ảnh, QA trích xuất câu trả lời, TRAKE truy vết chuỗi hành động). Hiện tại giao diện đã hỗ trợ đổi chế độ nhưng backend chưa có luồng xử lý tương ứng dẫn tới lỗi hệ thống khi chuyển chế độ tìm kiếm.

### Danh sách nhiệm vụ
*   **Xây dựng Query Classifier:**
    *   Viết lớp `QueryClassifier` phân tích câu truy vấn để tự động dự đoán chiến lược tìm kiếm phù hợp.
*   **Xây dựng các lớp Strategy Stubs:**
    *   `QaStrategy`: Thiết lập chế độ trả về có thuộc tính `answer_required: true` giúp giao diện hiển thị ô điền câu trả lời text.
    *   `TrakeStrategy`: Thiết lập chế độ trả về có thuộc tính `sequence_required: true` phục vụ việc hiển thị timeline sự kiện liên tục.
    *   `VisualKisStrategy`: Thiết lập fallback và hỗ trợ tìm kiếm bằng ảnh tải lên.
*   **Cập nhật API Endpoint:** Cập nhật route `/api/v1/search` để nhận tham số `query_type`, tự động định tuyến qua các Strategy tương ứng.

---

## 4. Hướng 4: Thiết Kế Bộ Importer Mềm Dẻo Cho Dataset Mới

### Rationale (Lý do thực hiện)
Định dạng thư mục dữ liệu thi đấu chính thức của BTC có thể thay đổi bất ngờ vào ngày công bố (25/06). Hệ thống cần một bộ nạp dữ liệu (Importer) linh hoạt để ánh xạ bất kỳ cấu trúc thư mục nào thành tệp tin cấu trúc xương sống `manifest.jsonl`.

### Danh sách nhiệm vụ
*   **Xây dựng BaseDataLoader:**
    *   Định nghĩa interface đọc dữ liệu.
*   **Xây dựng các DataLoader Adapters:**
    *   `V3cDataLoader`: Đọc cấu trúc thư mục V3C (videos, keyframes, thumbnails, msb, info).
    *   `AicDataLoader`: Đọc cấu trúc thư mục theo dự kiến của BTC (Videos, Keyframes, Objects, Metadata).
*   **Tạo script nạp dữ liệu tự động:**
    *   Viết script `importer.py` tự động phát hiện định dạng thư mục dữ liệu đầu vào.
    *   Quét và xuất ra file `manifest.jsonl` chuẩn hóa đường dẫn để Backend và Frontend bốc tách thông tin mượt mà.
