# 📄 Tài liệu Hướng dẫn Cài đặt & Sử dụng `README.md`

Bản hãy tạo file `README.md` và dán toàn bộ nội dung thực chiến dưới đây vào:

```markdown
# ⚡ THUNDERRETRIEVE v1.0 — AI Challenge 2026 Video Retrieval Panel

> **Giai đoạn 0 (P0):** Xây dựng hạ tầng đường ống dữ liệu Đa phương thức (End-to-End Baseline Pipeline) kết nối Giao diện React UI, Máy chủ FastAPI, và Cơ sở dữ liệu Vector trực tuyến Qdrant Cloud.

Hệ thống được thiết kế theo kiến trúc OOP/Adapter sạch, phân tách rõ ràng giữa các phân hệ nghiệp vụ, giúp dễ dàng mở rộng, thay thế mô hình AI (CLIP, SigLIP) hoặc nâng cấp các chiến lược xử lý câu hỏi nâng cao (QA, TRAKE) ở các giai đoạn sau mà không làm ảnh hưởng đến cấu trúc Frontend.

---

## 🛠️ 1. Yêu cầu Môi trường & Hệ thống
* **Hệ điều hành:** Windows 10/11 (Đã được tối ưu hóa đường dẫn tệp tin).
* **Ngôn ngữ:** Python 3.10+ & Node.js 18+.
* **Cơ sở dữ liệu:** Tài khoản Qdrant Cloud (Cluster đặt tại miền `sa-east-1` AWS Singapore/Brazil).
* **Lưu trữ cục bộ:** Bộ nhớ trống ổ `D:` tối thiểu 2GB để phục vụ lưu trữ ảnh keyframes và bộ nhớ đệm Cache của Hugging Face Hub.

---

## 🚀 2. Hướng dẫn Cài đặt & Khởi cấu hình nhanh

### Bước 2.1: Thiết lập môi trường ảo Python Backend
Mở PowerShell tại thư mục gốc `D:\AIC\` và thực thi chuỗi lệnh sau:

```powershell
# Kích hoạt hoặc khởi tạo môi trường ảo (.venv)
.\.venv\Scripts\Activate.ps1

# Nâng cấp trình quản lý gói pip và cài đặt đồng bộ thư viện từ file đóng gói
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

```

### Bước 2.2: Cài đặt các gói tài nguyên Frontend (React UI)

Di chuyển vào thư mục `frontend` và nạp toàn bộ các node packages:

```powershell
cd frontend
npm install

```

---

## 📦 3. Quy trình Vận hành Đường ống Dữ liệu (Data Pipeline)

Trước khi kích hoạt giao diện, thành viên **Data/Retrieval Engineer** cần bốc tách ma trận vector và đẩy dữ liệu lên mây Qdrant theo đúng thứ tự:

1. **Chuẩn bị Dữ liệu Thô:** Đảm bảo các tệp tin video highlight bóng đá và các file vector đặc trưng `.npy` do BTC cấp đã nằm đúng vị trí cấu trúc trong thư mục `D:\AIC\data\processed\`.
2. **Bắn dữ liệu lên Cloud:** Thực thi script Python để khởi tạo Collection `aic_baseline_collection` và đẩy gói Payload chứa đường dẫn ảnh local lên Qdrant Cloud:
```powershell
cd D:\AIC\
.\.venv\Scripts\python.exe scripts/push_to_qdrant.py

```



---

## 🎮 4. Kích hoạt Hệ thống Toàn diện (Running the Application)

Để chạy thử nghiệm toàn bộ giải pháp Human-in-the-loop, Bản cần mở song song **2 cửa sổ Terminal/PowerShell** độc lập:

### 🖥️ Terminal 1: Khởi động Máy chủ API (FastAPI)

Trạm API Gateway chịu trách nhiệm lắng nghe kết nối, serve kho ảnh tĩnh và giao tiếp với Qdrant Cloud.

```powershell
cd D:\AIC\
.\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload

```

*Giao diện tài liệu Swagger tự động của API sẽ nằm tại:* `http://127.0.0.1:8000/docs`

### 🎨 Terminal 2: Kích hoạt Giao diện Thi đấu (React + Vite)

Giao diện Cyberpunk kính mờ cao cấp, hỗ trợ gom cụm video và hệ thống phím tắt tốc độ cao.

```powershell
cd D:\AIC\frontend\
npm run dev

```

*Truy cập bảng điều khiển người dùng tại:* `http://localhost:5173`

---

## ⌨️ 5. Cẩm nang Thao tác Đua Giải Siêu Tốc (Hotkeys Manual)

Hệ thống được tối ưu hóa để người dùng có thể duyệt hàng ngàn bức ảnh và nộp bài **100% bằng bàn phím mà không cần đụng vào con chuột**:

* 📌 Phím **`/`** : Đưa con trỏ nhanh vào ô tìm kiếm (Focus Search Input).
* 📌 Phím **`Esc`** : Thoát con trỏ khỏi ô nhập liệu để kích hoạt phím tắt điều hướng ảnh.
* 📌 Phím **`←` `→**` : Di chuyển vùng chọn (Viền Neon xanh lục) sang trái hoặc phải giữa các ô ảnh kết quả.
* 📌 Phím **`↑` `↓**` : Di chuyển vùng chọn nhảy lên hoặc xuống chính xác theo từng dòng lưới hiển thị.
* 📌 Phím **`Enter`** : 🚨 **SUBMIT EVIDENCE** — Nộp trực tiếp bức ảnh đang chọn lên hệ thống giả lập chấm điểm, tự động ghi log đo Latency và Recall.

---

## 📂 6. Cấu trúc Thư mục Dự án Chuẩn hóa

```text
D:\AIC\
├── backend/
│   └── app/
│       ├── main.py          # Điểm nổ máy Server chính & Media Serving
│       ├── core/
│       │   └── config.py    # Cấu hình API Key Qdrant Cloud & Biến môi trường
│       └── services/
│           └── search.py    # Lõi xử lý trích xuất Vector CLIP & Query mây
├── frontend/
│   ├── src/
│   │   ├── App.jsx          # Giao diện Cyberpunk UI & Hệ thống xử lý Hotkeys
│   │   └── index.css        # Khai báo cấu trúc `@import "tailwindcss"` v4
│   └── postcss.config.js    # Cấu hình plugin `@tailwindcss/postcss`
├── scripts/
│   └── push_to_qdrant.py    # Script ETL đẩy dữ liệu ma trận npy lên Cloud
├── data/
│   ├── logs/
│   │   └── submission_dry_run.jsonl  # Nhật ký ghi vết lịch sử nộp bài giải đề
│   └── processed/           # Kho chứa ảnh frames, thumbs mẫu của video
└── requirements.txt         # File đóng gói phiên bản thư viện Backend

```

```

---

Bản tạo tệp tin này xong là coi như đồ án của nhóm bạn đã đạt độ hoàn thiện cực kỳ chỉn chu, sạch sẽ từ mã nguồn cho đến tài liệu hướng dẫn. Chúc Bản gánh team thành công rực rỡ trong đợt công bố đề thi thật vào ngày 25/06 sắp tới nhé!

```