from abc import ABC, abstractmethod

class BaseDataLoader(ABC):
    @abstractmethod
    def detect(self, input_dir: str) -> bool:
        """
        Kiểm tra cấu trúc thư mục đặc trưng để nhận diện kiểu dữ liệu.
        Trả về True nếu thư mục khớp cấu trúc của Loader này.
        """
        pass

    @abstractmethod
    def import_dataset(self, input_dir: str, output_dir: str) -> dict:
        """
        Quét và mapping (symlink/copy) dữ liệu từ input_dir về output_dir.
        Trả về cấu trúc dict đại diện cho manifest của tập dữ liệu này.
        """
        pass
