import os
import glob
import shutil
from backend.app.loaders.base import BaseDataLoader

class V3cDataLoader(BaseDataLoader):
    def detect(self, input_dir: str) -> bool:
        """
        Nhận diện định dạng V3C: có thư mục tên "keyframes" nằm lồng ở các tầng dưới.
        """
        if not os.path.exists(input_dir) or not os.path.isdir(input_dir):
            return False
            
        for root, dirs, files in os.walk(input_dir):
            depth = root.replace(input_dir, "").count(os.sep)
            if depth > 3:
                # Tránh đi quá sâu
                continue
            if "keyframes" in [d.lower() for d in dirs]:
                return True
        return False

    def import_dataset(self, input_dir: str, output_dir: str) -> dict:
        manifest = {}
        
        # Đi tìm tất cả các thư mục tên là "keyframes"
        for root, dirs, files in os.walk(input_dir):
            for d in dirs:
                if d.lower() == "keyframes":
                    keyframes_path = os.path.join(root, d)
                    
                    # Quét các thư mục video con nằm bên trong thư mục keyframes này
                    for video_dir_name in os.listdir(keyframes_path):
                        video_dir = os.path.join(keyframes_path, video_dir_name)
                        if not os.path.isdir(video_dir):
                            continue
                            
                        # Lấy tất cả ảnh keyframes của video này
                        images = sorted(
                            glob.glob(os.path.join(video_dir, "*.jpg")) +
                            glob.glob(os.path.join(video_dir, "*.png"))
                        )
                        
                        if not images:
                            continue
                            
                        # Đặt tên video
                        video_name = video_dir_name
                        target_frames_dir = os.path.join(output_dir, "frames", video_name)
                        target_thumbs_dir = os.path.join(output_dir, "thumbs", video_name)
                        
                        os.makedirs(target_frames_dir, exist_ok=True)
                        os.makedirs(target_thumbs_dir, exist_ok=True)
                        
                        # Map từng ảnh sang processed
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
