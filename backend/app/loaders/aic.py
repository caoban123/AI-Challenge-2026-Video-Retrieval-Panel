import os
import glob
import shutil
from backend.app.loaders.base import BaseDataLoader

class AicDataLoader(BaseDataLoader):
    def detect(self, input_dir: str) -> bool:
        """
        Nhận diện định dạng AIC: có các thư mục con trực tiếp chứa ảnh .jpg hoặc .png.
        """
        if not os.path.exists(input_dir) or not os.path.isdir(input_dir):
            return False
            
        # Tìm thử xem có thư mục con nào chứa ảnh trực tiếp không
        for entry in os.listdir(input_dir):
            subpath = os.path.join(input_dir, entry)
            if os.path.isdir(subpath):
                # Kiểm tra xem có file ảnh nào ở đây không
                imgs = glob.glob(os.path.join(subpath, "*.jpg")) + glob.glob(os.path.join(subpath, "*.png"))
                if imgs:
                    return True
        return False

    def import_dataset(self, input_dir: str, output_dir: str) -> dict:
        manifest = {}
        
        # Quét các thư mục con trong input_dir
        for entry in os.listdir(input_dir):
            video_dir = os.path.join(input_dir, entry)
            if not os.path.isdir(video_dir):
                continue
                
            # Quét tất cả file ảnh trong thư mục video con
            images = sorted(
                glob.glob(os.path.join(video_dir, "*.jpg")) + 
                glob.glob(os.path.join(video_dir, "*.png"))
            )
            
            if not images:
                continue
                
            video_name = entry
            target_frames_dir = os.path.join(output_dir, "frames", video_name)
            target_thumbs_dir = os.path.join(output_dir, "thumbs", video_name)
            
            os.makedirs(target_frames_dir, exist_ok=True)
            os.makedirs(target_thumbs_dir, exist_ok=True)
            
            # Map từng ảnh
            for img_path in images:
                img_name = os.path.basename(img_path)
                
                # Tạo liên kết cho frames
                dst_frame = os.path.join(target_frames_dir, img_name)
                self._link_or_copy(img_path, dst_frame)
                
                # Tạo liên kết cho thumbs
                dst_thumb = os.path.join(target_thumbs_dir, img_name)
                self._link_or_copy(img_path, dst_thumb)
                
            manifest[video_name] = {
                "video_title": video_name,
                "total_frames": len(images),
                "frame_dir_path": f"data/processed/frames/{video_name}",
                "thumb_dir_path": f"data/processed/thumbs/{video_name}"
            }
            
        return manifest

    def _link_or_copy(self, src: str, dst: str):
        if os.path.exists(dst):
            return
        try:
            os.symlink(os.path.abspath(src), dst)
        except (OSError, PermissionError):
            try:
                os.link(src, dst)
            except (OSError, PermissionError):
                shutil.copy2(src, dst)
