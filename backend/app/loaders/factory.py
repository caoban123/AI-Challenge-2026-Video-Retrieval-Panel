import os
import json
from backend.app.loaders.base import BaseDataLoader
from backend.app.loaders.aic import AicDataLoader
from backend.app.loaders.v3c import V3cDataLoader

class ImporterRegistry:
    def __init__(self):
        # Ưu tiên V3cDataLoader trước vì nó có cấu trúc lồng nhau đặc thù hơn
        self.loaders = [
            V3cDataLoader(),
            AicDataLoader()
        ]

    def auto_detect_and_run(self, input_dir: str, output_dir: str) -> dict:
        chosen_loader = None
        for loader in self.loaders:
            if loader.detect(input_dir):
                chosen_loader = loader
                break
                
        if chosen_loader is None:
            print("[Warning] Khong tu dong nhan dien duoc kieu thu muc. Dung AicDataLoader lam mac dinh.")
            chosen_loader = AicDataLoader()
            
        print(f"[Info] Chon Loader: {chosen_loader.__class__.__name__} de xu ly...")
        manifest = chosen_loader.import_dataset(input_dir, output_dir)
        
        # Lưu file manifest.json vào thư mục đích
        manifest_path = os.path.join(output_dir, "manifest.json")
        os.makedirs(output_dir, exist_ok=True)
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=4, ensure_ascii=False)
            
        print(f"[Success] Da nap thanh cong! File manifest.json luu tai: {manifest_path}")
        print(f"[Summary] Tong so video ghi nhan: {len(manifest)} video.")
        return manifest
