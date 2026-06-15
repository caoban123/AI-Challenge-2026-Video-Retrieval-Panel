from abc import ABC, abstractmethod
import numpy as np

class EmbeddingModel(ABC):
    @abstractmethod
    def encode_text(self, texts: list[str]) -> np.ndarray:
        """
        Mã hóa danh sách văn bản sang mảng numpy vector đặc trưng.
        Kích thước trả về: (số lượng câu, chiều vector)
        """
        pass

    @abstractmethod
    def encode_images(self, image_paths: list[str]) -> np.ndarray:
        """
        Mã hóa danh sách đường dẫn ảnh sang mảng numpy vector đặc trưng.
        Kích thước trả về: (số lượng ảnh, chiều vector)
        """
        pass
