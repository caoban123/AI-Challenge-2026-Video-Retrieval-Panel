import os

class Settings:
    # Ép Hugging Face lưu bộ não AI vào ổ D rộng rãi
    os.environ["HF_HOME"] = r"D:\AIC\.cache\huggingface"
    
    # Cấu hình loại cơ sở dữ liệu Vector Index ("qdrant" hoặc "faiss")
    VECTOR_INDEX_TYPE: str = "faiss"
    
    # Thông tin kết nối Qdrant Cloud
    QDRANT_URL: str = "https://9fd23c68-a180-4539-936d-0b1da06d5271.sa-east-1-0.aws.cloud.qdrant.io"
    QDRANT_API_KEY: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIiwic3ViamVjdCI6ImFwaS1rZXk6NDVlZDM0NzEtMzc4My00MzMwLTk3YzItZjI4YzNlZTAxNzY3In0.F18gYg4KdSDHdU3Zx6X9X6OZ75tTjmk5sjff3jkK18E"
    COLLECTION_NAME: str = "aic_baseline_collection"
    
    # Cấu hình FAISS Index cục bộ
    FAISS_INDEX_PATH: str = r"D:\AIC\data\processed\index.bin"
    FAISS_METADATA_PATH: str = r"D:\AIC\data\processed\metadata.json"
    
    # Cấu hình file manifest cho BM25
    MANIFEST_PATH: str = r"D:\AIC\data\processed\manifest.json"
    
    # Mô hình AI bẻ chữ thành vector
    CLIP_MODEL_ID: str = "openai/clip-vit-base-patch32"

settings = Settings()