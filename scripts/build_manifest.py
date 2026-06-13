import os
import json
import glob

def generate_manifest():
    FRAMES_DIR = "data/processed/frames"
    MANIFEST_PATH = "data/processed/manifest.json"
    
    manifest = {}
    
    # Quét tất cả các thư mục con (chính là tên các video) trong thư mục frames
    video_folders = glob.glob(os.path.join(FRAMES_DIR, "*"))
    
    if not video_folders:
        print("ℹ️ Chưa tìm thấy thư mục ảnh nào trong data/processed/frames. Hãy chạy lại script cắt ảnh trước!")
        return

    for folder in video_folders:
        if os.path.isdir(folder):
            video_name = os.path.basename(folder)
            
            # Đếm xem thư mục này thực tế đang chứa bao nhiêu file ảnh .jpg
            num_frames = len(glob.glob(os.path.join(folder, "*.jpg")))
            
            # Khởi tạo thông tin lưu trữ cho video này vào sổ cái
            manifest[video_name] = {
                "video_title": video_name,
                "total_frames": num_frames,
                "frame_dir_path": f"data/processed/frames/{video_name}",
                "thumb_dir_path": f"data/processed/thumbs/{video_name}"
            }
            
    # Ghi toàn bộ cấu trúc dữ liệu thu được ra file manifest.json sạch sẽ
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=4, ensure_ascii=False)
        
    print(f"✅ Đã lập sổ cái thành công! File lưu tại: {MANIFEST_PATH}")
    print(f"📊 Tổng số video ghi nhận trong sổ cái: {len(manifest)} video.")

if __name__ == "__main__":
    generate_manifest()