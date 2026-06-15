# Hướng Dẫn Vận Hành & Nạp Dữ Liệu Thi Đấu Mới (Dataset Import Guide)

Tài liệu này hướng dẫn chi tiết quy trình chạy hệ thống khi bạn nhận được tập dữ liệu mới từ Ban tổ chức (BTC) cuộc thi AI Challenge.

---

## 1. Quy Trình 3 Bước Khi Nhận Dữ Liệu Mới

Khi nhận được thư mục dữ liệu thi đấu (chứa video hoặc ảnh keyframes thô), hãy thực hiện tuần tự các bước sau:

### Bước 1: Nạp và chuẩn hóa cấu trúc dữ liệu (`importer.py`)
Mở terminal và chạy script importer để tự động nhận dạng định dạng dữ liệu (AIC hoặc V3C), tạo liên kết tượng trưng (symlinks/hardlinks) và sinh file `manifest.json`:
```bash
# Sử dụng môi trường ảo Python của dự án
.venv\Scripts\python.exe scripts\importer.py --input_dir <DUONG_DAN_THU_MUC_BTC_CAP>
```
*Kết quả:* Các ảnh keyframes sẽ được ánh xạ về `data/processed/frames/` và `data/processed/thumbs/`, đồng thời tạo ra file `data/processed/manifest.json`.

### Bước 2: Trích xuất các vector đặc trưng ảnh (`extract_features.py`)
Chạy script của hệ thống để gọi mô hình CLIP trích xuất các vector đặc trưng (dimension = 512) cho từng frame ảnh và lưu thành các file `.npy`:
```bash
.venv\Scripts\python.exe scripts\extract_features.py
```

### Bước 3: Lập chỉ mục Vector Index (`build_index.py`)
Chạy script lập chỉ mục FAISS cục bộ để đóng gói toàn bộ vector `.npy` thành file nhị phân tìm kiếm siêu tốc:
```bash
.venv\Scripts\python.exe scripts\build_index.py
```
*Kết quả:* Tạo ra file chỉ mục `data/processed/index.bin` và file bản đồ tra cứu `data/processed/metadata.json`.

Lúc này, bạn chỉ cần khởi động lại Backend và bắt đầu tìm kiếm!

---

## 2. Giải Đáp Thắc Mắc & Xử Lý Tình Huống Thực Tế

### Câu hỏi: Nếu thư mục dữ liệu của BTC khác với thiết kế hoặc có thêm các tệp tin/trường thông tin mới thì hệ thống có chạy không?

#### 1. Trường hợp có thêm các file/thư mục phụ (ví dụ: file thông tin, kết quả OCR, file đối tượng .json...)
*   **Có chạy bình thường!** Hệ thống được thiết kế để chỉ quét và lọc ra các tệp tin hình ảnh (`.jpg`, `.png`). Mọi thư mục con hoặc tệp tin rác khác không liên quan sẽ tự động bị bỏ qua và **không gây lỗi hệ thống**.

#### 2. Trường hợp cấu trúc thư mục của BTC thay đổi hoàn toàn (không phải dạng phẳng AIC và cũng không phải dạng phân cấp V3C)
Nếu cấu trúc thư mục bị đảo lộn hoàn toàn, bộ Importer của hệ thống có tính mở rộng cực cao. Bạn chỉ cần làm theo các bước sau để hỗ trợ cấu trúc mới trong vòng 5 phút:

1.  **Tạo một Loader mới:** Mở thư mục `backend/app/loaders/` và tạo file loader mới (ví dụ: `new_format.py` kế thừa từ `BaseDataLoader`):
    ```python
    from backend.app.loaders.base import BaseDataLoader
    
    class NewFormatDataLoader(BaseDataLoader):
        def detect(self, input_dir: str) -> bool:
            # Viết logic nhận diện cấu trúc thư mục mới ở đây (Trả về True/False)
            return True 
            
        def import_dataset(self, input_dir: str, output_dir: str) -> dict:
            # Viết logic quét file và map về output_dir ở đây
            # Trả về manifest dạng dict giống AicDataLoader
            return manifest
    ```
2.  **Đăng ký Loader:** Mở file [factory.py](file:///d:/AIC/backend/app/loaders/factory.py) và thêm class mới vào danh sách `self.loaders`:
    ```diff
    + from backend.app.loaders.new_format import NewFormatDataLoader
      
      class ImporterRegistry:
          def __init__(self):
              self.loaders = [
    +             NewFormatDataLoader(),
                  V3cDataLoader(),
                  AicDataLoader()
              ]
    ```
    Hệ thống sẽ tự động ưu tiên chạy Loader mới này khi quét thư mục.

#### 3. Trường hợp manifest cần ghi nhận thêm các trường thông tin mới (như văn bản OCR, thông tin Object...)
Khi BTC cung cấp thêm các tệp dữ liệu đi kèm, bạn chỉ cần mở rộng phương thức `import_dataset` của Loader tương ứng để đọc các tệp đó và nạp thêm các trường đó vào manifest:
```python
# Ví dụ nạp thêm thông tin ocr
manifest[video_name] = {
    "video_title": video_name,
    "total_frames": len(images),
    "frame_dir_path": f"data/processed/frames/{video_name}",
    "thumb_dir_path": f"data/processed/thumbs/{video_name}",
    "ocr_data": read_ocr_json(video_dir)  # Thêm trường động mới
}
```
Các trường thông tin mới này sẽ được lưu trữ an toàn trong file `manifest.json` và sẵn sàng phục vụ cho việc nâng cấp các thuật toán tìm kiếm kết hợp (Hybrid Search) tiếp theo.
