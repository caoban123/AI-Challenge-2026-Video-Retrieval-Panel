# Kế Hoạch Tối Ưu Hóa Latency Hệ Thống

Tài liệu này chi tiết các giải pháp tối ưu hóa tốc độ phản hồi Backend và hiển thị Frontend cho hệ thống tìm kiếm ThunderRetrieve.

## 1. Tối Ưu Hóa Mô Hình CLIP (Backend)
*   **Giải pháp:** Tích hợp bộ nhớ đệm `lru_cache` ở mức hàm mã hóa văn bản (`encode_text`).
*   **Mục tiêu:** Giảm thời gian xử lý của mô hình học máy đối với các câu truy vấn lặp lại từ ~300ms xuống dưới 1ms.

## 2. Thiết Lập Bộ Nhớ Đệm Trình Duyệt (Browser Caching)
*   **Giải pháp:** Bọc thư viện `StaticFiles` của FastAPI để tự động trả về tiêu đề HTTP:
    ```http
    Cache-Control: public, max-age=31536000, immutable
    ```
*   **Mục tiêu:** Trình duyệt lưu ảnh keyframe trực tiếp ở đĩa máy khách, giảm tải hoàn toàn băng thông mạng nội bộ sau lượt tải đầu tiên.

## 3. Trì Hoãn Tải Ảnh (Lazy Loading)
*   **Giải pháp:** Bổ sung `loading="lazy"` cho các thẻ `<img>` của kết quả tìm kiếm trong `App.jsx`.
*   **Mục tiêu:** Trình duyệt chỉ gửi yêu cầu tải ảnh khi ảnh cuộn tới khung nhìn, loại bỏ nghẽn connection pool.
