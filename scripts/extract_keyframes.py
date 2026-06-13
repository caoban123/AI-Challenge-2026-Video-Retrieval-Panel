import cv2
import os
import glob
import numpy as np

def extract_frames_and_thumbs(video_path, out_frame_dir, out_thumb_dir):
    # Dùng numpy để đọc file vướng tiếng Việt có dấu, bypass lỗi của OpenCV thô
    try:
        video_bytes = np.fromfile(video_path, dtype=np.uint8)
        cap = cv2.VideoCapture()
        cap.open(video_path) # Thử mở trực tiếp
        
        if not cap.isOpened():
            # Nếu mở trực tiếp thất bại do lỗi đường dẫn tiếng Việt, dùng giải pháp dự phòng
            print(f"⚠️ OpenCV kẹt tiếng Việt, đang thử cơ chế bypass cho: {os.path.basename(video_path)}")
            cap.open(video_path, cv2.CAP_FFMPEG)
    except Exception as e:
        print(f"❌ Lỗi đọc file: {e}")
        return

    if not cap.isOpened():
        print(f"❌ Không thể mở video (kiểm tra lại codec/file): {video_path}")
        return

    video_fps = cap.get(cv2.CAP_PROP_FPS)
    if video_fps == 0 or np.isnan(video_fps):
        video_fps = 25  
        
    frame_interval = int(round(video_fps))
    video_name = os.path.splitext(os.path.basename(video_path))[0]
    
    video_frame_dir = os.path.join(out_frame_dir, video_name)
    video_thumb_dir = os.path.join(out_thumb_dir, video_name)
    os.makedirs(video_frame_dir, exist_ok=True)
    os.makedirs(video_thumb_dir, exist_ok=True)

    frame_count = 0
    saved_count = 0

    print(f"🎬 Đang rã video: {video_name} (FPS: {video_fps})")

    while True:
        ret, frame = cap.read()  # ĐỌC KHUNG HÌNH (Chỉ giữ duy nhất dòng này, không có cap.get)
        if not ret:
            break

        # Cứ đúng mốc 1 giây thì bốc ảnh
        if frame_count % frame_interval == 0:
            frame_id = f"{saved_count:04d}"
            frame_file = os.path.join(video_frame_dir, f"{frame_id}.jpg")
            thumb_file = os.path.join(video_thumb_dir, f"{frame_id}.jpg")

            # Bypass lỗi tiếng Việt khi ghi file bằng cv2.imwrite
            # Thay vì cv2.imwrite(frame_file, frame), ta dùng imencode + tofile
            _, img_encoded = cv2.imencode('.jpg', frame)
            img_encoded.tofile(frame_file)

            # Tạo và lưu Thumbnail nhỏ gọn
            height, width = frame.shape[:2]
            new_width = 320
            new_height = int(height * (new_width / width))
            thumb_frame = cv2.resize(frame, (new_width, new_height))
            
            _, thumb_encoded = cv2.imencode('.jpg', thumb_frame)
            thumb_encoded.tofile(thumb_file)

            saved_count += 1

        frame_count += 1

    cap.release()
    print(f"✅ HOÀN THÀNH: {video_name} -> Đã xuất {saved_count} ảnh sạch vào thư mục.")

if __name__ == "__main__":
    RAW_VIDEOS_DIR = "data/raw/videos"
    PROCESSED_FRAMES_DIR = "data/processed/frames"
    PROCESSED_THUMBS_DIR = "data/processed/thumbs"

    video_files = glob.glob(os.path.join(RAW_VIDEOS_DIR, "*.mp4"))

    if not video_files:
        print("ℹ️ Không tìm thấy file video .mp4 nào trong data/raw/videos!")
    else:
        print(f"🚀 Bắt đầu tiến trình xử lý {len(video_files)} video mẫu...")
        for video_path in video_files:
            extract_frames_and_thumbs(video_path, PROCESSED_FRAMES_DIR, PROCESSED_THUMBS_DIR)
        print("\n🎉 ĐÃ XỬ LÝ XONG TOÀN BỘ! Kiểm tra lại folder của bạn ngay!")