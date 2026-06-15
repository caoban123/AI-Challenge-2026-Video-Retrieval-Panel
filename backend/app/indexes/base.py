from abc import ABC, abstractmethod

class VectorIndex(ABC):
    @abstractmethod
    def build(self, vectors, metadata: list[dict]) -> None:
        """
        Xây dựng chỉ mục vector từ ma trận vector và danh sách metadata tương ứng.
        """
        pass

    @abstractmethod
    def search(self, query_vector: list[float], top_k: int) -> list[dict]:
        """
        Tìm kiếm Top-K vector tương đồng gần nhất với query_vector.
        Trả về danh sách kết quả chứa payload/metadata và điểm tương đồng score.
        """
        pass

    @abstractmethod
    def save(self, path: str) -> None:
        """
        Lưu chỉ mục nhị phân xuống ổ cứng.
        """
        pass

    @abstractmethod
    def load(self, path: str) -> None:
        """
        Nạp chỉ mục nhị phân từ ổ cứng lên RAM.
        """
        pass


class TextSearchIndex(ABC):
    @abstractmethod
    def build(self, docs: list[dict]) -> None:
        """
        Xây dựng chỉ mục văn bản từ danh sách tài liệu.
        """
        pass

    @abstractmethod
    def search(self, query: str, top_k: int) -> list[dict]:
        """
        Tìm kiếm văn bản và trả về Top-K kết quả phù hợp nhất.
        """
        pass
