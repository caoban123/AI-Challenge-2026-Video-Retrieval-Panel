import os
import shutil
import json
import subprocess

def create_mock_files():
    # 1. Tạo mock AIC raw
    aic_raw = "data/mock_aic_raw"
    os.makedirs(os.path.join(aic_raw, "video_aic_1"), exist_ok=True)
    os.makedirs(os.path.join(aic_raw, "video_aic_2"), exist_ok=True)
    
    with open(os.path.join(aic_raw, "video_aic_1", "0000.jpg"), "w") as f:
        f.write("mock image data")
    with open(os.path.join(aic_raw, "video_aic_1", "0001.jpg"), "w") as f:
        f.write("mock image data")
    with open(os.path.join(aic_raw, "video_aic_2", "0000.jpg"), "w") as f:
        f.write("mock image data")
        
    # 2. Tạo mock V3C raw
    v3c_raw = "data/mock_v3c_raw"
    os.makedirs(os.path.join(v3c_raw, "v3c_subset", "keyframes", "v3c_video_1"), exist_ok=True)
    os.makedirs(os.path.join(v3c_raw, "v3c_subset", "keyframes", "v3c_video_2"), exist_ok=True)
    
    with open(os.path.join(v3c_raw, "v3c_subset", "keyframes", "v3c_video_1", "0001.jpg"), "w") as f:
        f.write("mock image data")
    with open(os.path.join(v3c_raw, "v3c_subset", "keyframes", "v3c_video_2", "0001.jpg"), "w") as f:
        f.write("mock image data")
        
    return aic_raw, v3c_raw

def clean_up():
    for d in ["data/mock_aic_raw", "data/mock_v3c_raw", "data/mock_processed_aic", "data/mock_processed_v3c"]:
        if os.path.exists(d):
            try:
                shutil.rmtree(d)
            except Exception as e:
                print(f"Error cleaning up {d}: {e}")

def main():
    print("[Clean] Cleaning up old mock data...")
    clean_up()
    
    print("[Mock] Creating mock datasets...")
    aic_raw, v3c_raw = create_mock_files()
    
    # Test AIC Import
    print("\n--- TEST IMPORT AIC FORMAT ---")
    cmd_aic = [
        ".venv/Scripts/python",
        "scripts/importer.py",
        "--input_dir", aic_raw,
        "--output_dir", "data/mock_processed_aic"
    ]
    subprocess.run(cmd_aic, check=True)
    
    # Verify AIC manifest
    manifest_aic_path = "data/mock_processed_aic/manifest.json"
    assert os.path.exists(manifest_aic_path), "AIC manifest.json does not exist!"
    with open(manifest_aic_path, "r", encoding="utf-8") as f:
        manifest_aic = json.load(f)
    print("AIC Manifest Content:", json.dumps(manifest_aic, indent=2, ensure_ascii=False))
    assert "video_aic_1" in manifest_aic, "video_aic_1 missing from AIC manifest!"
    assert manifest_aic["video_aic_1"]["total_frames"] == 2, "video_aic_1 total_frames should be 2!"
    print("Success: AIC Import Test Passed!")
    
    # Test V3C Import
    print("\n--- TEST IMPORT V3C FORMAT ---")
    cmd_v3c = [
        ".venv/Scripts/python",
        "scripts/importer.py",
        "--input_dir", v3c_raw,
        "--output_dir", "data/mock_processed_v3c"
    ]
    subprocess.run(cmd_v3c, check=True)
    
    # Verify V3C manifest
    manifest_v3c_path = "data/mock_processed_v3c/manifest.json"
    assert os.path.exists(manifest_v3c_path), "V3C manifest.json does not exist!"
    with open(manifest_v3c_path, "r", encoding="utf-8") as f:
        manifest_v3c = json.load(f)
    print("V3C Manifest Content:", json.dumps(manifest_v3c, indent=2, ensure_ascii=False))
    assert "v3c_video_1" in manifest_v3c, "v3c_video_1 missing from V3C manifest!"
    assert manifest_v3c["v3c_video_1"]["total_frames"] == 1, "v3c_video_1 total_frames should be 1!"
    print("Success: V3C Import Test Passed!")
    
    print("\n[Clean] Cleaning up test output...")
    clean_up()
    print("ALL TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    main()
