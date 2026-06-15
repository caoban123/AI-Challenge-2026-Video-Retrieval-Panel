from abc import ABC, abstractmethod

class TaskStrategy(ABC):
    @abstractmethod
    def retrieve(self, query_context: dict) -> list[dict]:
        """
        Giai đoạn 1: Tìm kiếm thô để chọn ứng viên thích hợp.
        """
        pass

    @abstractmethod
    def rerank(self, candidates: list[dict], query_context: dict) -> list[dict]:
        """
        Giai đoạn 2: Xếp hạng lại danh sách ứng viên (Reranking).
        """
        pass

    @abstractmethod
    def build_ui_payload(self, results: list[dict], took_ms: int) -> dict:
        """
        Giai đoạn 3: Đóng gói và định dạng dữ liệu trả về theo đúng hợp đồng với Frontend.
        """
        pass
