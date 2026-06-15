# Kế Hoạch Triển Khai Hoàn Thiện Stubs & Giao Diện Định Hướng Cho QA/TRAKE/Visual KIS (Hướng 3)

Mục tiêu của kế hoạch này là mở rộng hệ thống để hỗ trợ các thể thức thi đấu khác bên cạnh Visual KIS (Tìm kiếm hình ảnh), cụ thể là:
1.  **Question Answering (QA):** Trả lời câu hỏi dựa trên nội dung video + bằng chứng frame.
2.  **Object Tracking / Trajectory Retrieval (TRAKE):** Truy vết đối tượng và dựng lộ trình/dòng thời gian chuyển động.

Chúng ta sẽ xây dựng các bộ định tuyến Backend (stubs) và giao diện tab tương tác trên Frontend React UI.

## User Review Required

> [!NOTE]
> **Tương thích giao thức:** Các API mới sẽ dùng chung cấu trúc request/response chuẩn để tối đa hóa khả năng tái sử dụng cấu trúc hiển thị sẵn có của Frontend, đồng thời bổ sung các trường dữ liệu đặc thù (`answer` cho QA và `trajectory` cho TRAKE).
> **Lưu tên file kế hoạch:** Bản kế hoạch này được lưu trữ trực tiếp trong thư mục dự án tại đường dẫn `docs/huong3.md`.

## Proposed Changes

Chúng ta sẽ tạo các file mới và sửa đổi hệ thống như sau:

---

### 1. Phân hệ Strategies & Router (Backend)

#### [NEW] [qa.py](file:///d:/AIC/backend/app/strategies/qa.py)
*   Triển khai lớp `QaStrategy` kế thừa từ `TaskStrategy`.
*   Constructor nhận vào `Retriever` (sử dụng `HybridRetriever`).
*   Hàm `build_ui_payload(self, results: list[dict], took_ms: int) -> dict`:
    *   Sinh câu trả lời mock dựa trên câu query: `"answer": f"[QA Engine Mock] Dựa trên phân tích bằng chứng, đây là thời điểm xảy ra sự việc: '{query}'..."`.
    *   Trả về payload chứa `"answer"` và danh sách `"results"` (các bằng chứng chứng minh).

#### [NEW] [trake.py](file:///d:/AIC/backend/app/strategies/trake.py)
*   Triển khai lớp `TrakeStrategy` kế thừa từ `TaskStrategy`.
*   Constructor nhận vào `Retriever`.
*   Hàm `build_ui_payload(self, results: list[dict], took_ms: int) -> dict`:
    *   Sinh danh sách lộ trình mock `"trajectory"` (chọn ra chuỗi 3-5 frame liên tục có điểm tương đồng cao nhất để biểu diễn quỹ đạo di chuyển của đối tượng).

#### [MODIFY] [main.py](file:///d:/AIC/backend/app/main.py)
*   Bổ sung 2 endpoint mới:
    *   `@app.post("/api/v1/search/qa")`: Gọi dịch vụ `search_service.execute_qa_search(...)`.
    *   `@app.post("/api/v1/search/trake")`: Gọi dịch vụ `search_service.execute_trake_search(...)`.

#### [MODIFY] [search.py](file:///d:/AIC/backend/app/services/search.py)
*   Import và khởi tạo `QaStrategy` và `TrakeStrategy`.
*   Viết 2 hàm điều phối: `execute_qa_search` và `execute_trake_search` tương thích giao thức.

---

### 2. Giao diện Người dùng (Frontend React UI)

#### [MODIFY] [App.jsx](file:///d:/AIC/frontend/src/App.jsx)
*   Bổ sung thanh chuyển đổi Tab (Search Mode Selector) ở thanh Header:
    *   `VISUAL KIS`
    *   `QUESTION ANSWERING (QA)`
    *   `OBJECT TRACKING (TRAKE)`
*   Cập nhật hàm `handleSearch`: Tự động gọi đúng endpoint tương ứng với tab đang chọn.
*   Cập nhật Layout hiển thị kết quả:
    *   Nếu là chế độ **QA**: Hiển thị bảng màu Indigo nổi bật chứa câu trả lời văn bản `"answer"` ở phía trên danh sách bằng chứng.
    *   Nếu là chế độ **TRAKE**: Hiển thị chuỗi timeline quỹ đạo di chuyển nằm ngang đặc thù ở trên cùng, mô phỏng lộ trình di chuyển của đối tượng.

---

## Verification Plan

### Manual Verification
*   Khởi động hệ thống Backend và Frontend.
*   Chuyển sang tab **QA**, gõ tìm kiếm -> Kiểm tra xem câu trả lời Mock và danh sách ảnh có hiển thị đúng khu vực trực quan hay không.
*   Chuyển sang tab **TRAKE**, gõ tìm kiếm -> Kiểm tra xem dải timeline quỹ đạo di chuyển có kết nối mượt mà hay không.
