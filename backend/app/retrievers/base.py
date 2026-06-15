from abc import ABC, abstractmethod

class Retriever(ABC):
    @abstractmethod
    def retrieve(self, query_context: dict, top_k: int) -> list[dict]:
        """
        Trích xuất dữ liệu thô ứng với ngữ cảnh câu truy vấn và trả về Top-K ứng viên.
        """
        pass
