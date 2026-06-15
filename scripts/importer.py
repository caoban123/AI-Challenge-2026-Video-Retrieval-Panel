import os
import sys
import argparse

# Thêm thư mục gốc của repo vào sys.path để python nhận diện backend package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.loaders.factory import ImporterRegistry

def main():
    parser = argparse.ArgumentParser(description="ThunderRetrieve - Flexible Dataset Importer Engine")
    parser.add_argument(
        "--input_dir",
        required=True,
        help="Đường dẫn tới thư mục dữ liệu thô (raw dataset)"
    )
    parser.add_argument(
        "--output_dir",
        default="data/processed",
        help="Đường dẫn thư mục đích làm việc của Backend (mặc định: data/processed)"
    )
    
    args = parser.parse_args()
    
    input_dir = args.input_dir
    output_dir = args.output_dir
    
    if not os.path.exists(input_dir):
        print(f"[Error] Thu muc dau vao khong ton tai: {input_dir}")
        sys.exit(1)
        
    print(f"[Info] Bat dau quet thu muc dau vao: {input_dir}")
    print(f"[Info] Thu muc dich chuan hoa: {output_dir}")
    
    registry = ImporterRegistry()
    registry.auto_detect_and_run(input_dir, output_dir)
    
if __name__ == "__main__":
    main()
