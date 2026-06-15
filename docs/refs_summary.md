# Tóm Tắt Nội Dung Thư Mục Refs — AI Challenge 2026

Thư mục `Refs` (`d:\AIC\Refs`) chứa 6 tài liệu PDF cực kỳ quan trọng định hình toàn bộ chiến lược phát triển, kiến trúc hệ thống, kế hoạch phân chia công việc, và lộ trình huấn luyện cho dự án **Video Evidence Retrieval** tại cuộc thi **AI Challenge 2026**.

Dưới đây là tóm tắt chi tiết của từng tài liệu đã được trích xuất thành công:

---

## 1. [AIC.pdf](file:///d:/AIC/Refs/AIC.pdf)
### *Chiến Lược Triển Khai Hệ Thống Video Evidence Retrieval — AI Challenge 2026*
Tài liệu này vạch ra kiến trúc tổng quan của hệ thống tìm kiếm video evidence theo mô hình đa phương thức (multimodal) và lộ trình phát triển qua 4 giai đoạn chính.

*   **Sơ đồ Kiến trúc Tổng quan:**
    *   **Frontend:** React + Vite (hiển thị grid thumbnail, video/frame viewer, nhập giọng nói, phím tắt, submit panel).
    *   **API Gateway:** FastAPI (async REST / WebSocket).
    *   **Các module xử lý truy vấn:** Speech-to-Text (PhoWhisper/Whisper), Query Agent (viết lại/mở rộng câu truy vấn), Entity Grounding (Wikidata, InfoSeek).
    *   **Stage 1 - Hybrid Retrieval:** Kết hợp BM25 (trên OCR/transcript/metadata) và Dense Vector (CLIP/SigLIP/BGE-M3) qua thuật toán xếp hạng dung hợp **RRF (Reciprocal Rank Fusion)** lưu trữ trên Vector DB (Qdrant).
    *   **Stage 2 - Reranking:** Lọc và xếp hạng lại candidate bằng Cross-Encoder (BGE-reranker) + LVLM scoring (Gemini Flash / Qwen2-VL) + đối chiếu đối tượng JSON (Faster R-CNN).
    *   **Stage 3 - Agentic RAG Layer (LangGraph):** Điều phối luồng xử lý tự sửa lỗi (CRAG Reflection) và tự động xác thực (Verifier Agent) để giảm thiểu penalty khi submit sai.
    *   **Stage 4 - Temporal Clustering + UI Ranking:** Gom nhóm các frame lân cận và hiển thị kết quả trực quan cho người dùng cuối.
*   **Lộ trình phát triển 4 giai đoạn:**
    1.  *Giai đoạn 1 (Trước 25/06/2026):* Xây dựng hạ tầng & Text Retrieval (FastAPI, React UI, Qdrant/HNSW, BM25, RRF).
    2.  *Giai đoạn 2:* Tìm kiếm đa phương thức (Visual Search bằng CLIP) & Reranking hai giai đoạn (Gemini Flash + BGE-reranker).
    3.  *Giai đoạn 3:* Phân tích ngữ cảnh nâng cao, Agentic RAG (LangGraph + CRAG) & Verifier Agent dựa trên dữ liệu Object JSON.
    4.  *Giai đoạn 4:* Tối ưu hệ thống (Docker hóa, tối ưu độ trễ < 500ms), hỗ trợ cả Fully Auto (M2M) và Semi-Auto (Human-in-the-loop).

---

## 2. [execution_backlog.pdf](file:///d:/AIC/Refs/execution_backlog.pdf)
### *Execution Backlog cho AI Challenge 2026*
Bản danh sách công việc (Backlog) chi tiết, được phân loại theo mức độ ưu tiên từ P0 đến P2 và phân bổ vai trò cho nhóm 5 thành viên.

*   **Phân chia thứ tự ưu tiên (Priority):**
    *   **P0 (Trước khi có dataset chính thức):** Tập trung dựng bộ khung dữ liệu (manifest chuẩn), tìm kiếm baseline (visual embedding trên FAISS/Qdrant), xây dựng FastAPI Endpoint (`/search`, `/submit/dry-run`), và dựng UI cơ bản (Result Grid, Preview, Neighbor Strip).
    *   **P1 (Ngay sau khi có dataset chính thức):** Tích hợp OCR keyframe, ASR transcript tiếng Việt, thuật toán Fusion điểm số (Visual + Caption + OCR + ASR), công thức Sequence heuristic cho TRAKE, và VLM answer extractor cho QA.
    *   **P2 (Tối ưu nâng cao):** Hỗ trợ structured caption, voice-to-text query, HyDE query expansion, local VLM reranking top-20, và tích hợp auto-submit kết nối với DRES server của BTC.
*   **Phân chia công việc theo 5 vai trò:**
    1.  *Model/Retrieval:* Xây dựng baseline embedding, thuật toán fusion/rerank, TRAKE sequence.
    2.  *Data/OCR/ASR:* Viết script extract keyframe, chạy OCR/ASR, chuẩn hóa metadata.
    3.  *Backend/Integration:* Dựng API (FastAPI), tích hợp Vector DB, DRES submit client, Docker.
    4.  *Frontend/UI:* Thiết kế giao diện tìm kiếm, grid, timeline, hotkeys, workflow submit.
    5.  *Eval/Product:* Tạo query set/ground truth giả lập để làm mock contest, theo dõi Recall@K, phân tích lỗi.
*   **Definition of Done (DoD) cho MVP:** Luồng dữ liệu chạy thông suốt end-to-end; tìm kiếm text trả top-100 trong < 1 giây; người dùng có thể preview và submit chỉ trong tối đa 2 click chuột.

---

## 3. [p0_build_resources.pdf](file:///d:/AIC/Refs/p0_build_resources.pdf)
### *Tài Liệu để Build P0*
Cung cấp định hướng thiết kế phần mềm cốt lõi cho P0, nhấn mạnh nguyên tắc lập trình hướng đối tượng (OOP) và sử dụng Adapter Pattern để hệ thống không bị phụ thuộc cứng vào bất kỳ model hay cơ sở dữ liệu nào.

*   **Kiến trúc Adapter / OOP đề xuất:**
    *   `QueryClassifier` (phân loại câu hỏi thành các dạng strategy).
    *   `TaskStrategy` (các chiến lược xử lý: `TextualKisStrategy`, `VisualKisStrategy`, `QaStrategy`, `TrakeStrategy`, `OcrHeavyStrategy`, `AsrHeavyStrategy`).
    *   `EmbeddingModel` (`ClipEmbeddingModel`, `SiglipEmbeddingModel`, `PrecomputedNpyEmbeddingModel`).
    *   `VectorIndex` (`FaissVectorIndex`, `QdrantVectorIndex`).
    *   `TextSearchIndex` (`Bm25TextSearchIndex`, `QdrantSparseTextSearchIndex`).
    *   `SubmissionClient` (`DryRunSubmitClient`, `DresSubmitClient`, `BtcSubmitClient`).
*   **Chiến lược cho từng dạng câu hỏi (Task Strategies):** Mỗi dạng truy vấn (KIS, QA, TRAKE) có cách xử lý riêng, cấu trúc kết quả riêng, và định dạng nộp bài (submission format) khác nhau.
*   **Thứ tự triển khai:**
    1.  Dataset + Manifest.
    2.  Visual Search Baseline (CLIP + FAISS/Qdrant).
    3.  Text Search (BM25).
    4.  FastAPI Backend.
    5.  Vite Frontend UI.
    6.  Submit/Mock Contest.

---

## 4. [p0_implementation_spec.pdf](file:///d:/AIC/Refs/p0_implementation_spec.pdf)
### *P0 Implementation Spec — Bản Vẽ Thi Công P0*
Tài liệu cực kỳ chi tiết quy định cấu trúc thư mục dự án, schema cho các file dữ liệu, hợp đồng API và các class interface cụ thể.

*   **Cấu trúc thư mục thống nhất:**
    *   `backend/app/`: chứa router, core config, service, strategy, retriever, index, và repository.
    *   `frontend/src/`: chứa api client, components (SearchBox, ResultGrid, CandidateDetail, FrameStrip, SubmitPanel), và trang tìm kiếm.
    *   `scripts/`: các script Python chính như `extract_keyframes.py`, `build_manifest.py`, `build_visual_index.py`, `run_eval.py`.
    *   `data/`: thư mục chứa video gốc, keyframe đã xử lý, và file manifest xương sống.
*   **Hợp đồng API (API Contracts):**
    *   `GET /health`: Kiểm tra trạng thái.
    *   `POST /search`: Nhận query và filters, trả về danh sách kết quả chứa thông tin chi tiết của candidate kèm các điểm số (visual, text, ocr, asr).
    *   `GET /frames/{frame_id}/neighbors`: Trả về các frame liền kề trước/sau để hiển thị dạng timeline trong UI.
    *   `GET /videos/{video_id}`: Lấy thông tin video.
    *   `POST /submit/dry-run`: Ghi nhận lượt submit giả lập vào file log `submissions.jsonl`.
*   **Xương sống hệ thống:** File `manifest.jsonl` mô tả chi tiết từng frame bao gồm: `video_id`, `frame_id`, `timestamp`, `frame_path`, `thumb_path`, `video_path`, `source`.

---

## 5. [p0_task_cards.pdf](file:///d:/AIC/Refs/p0_task_cards.pdf)
### *P0 Task Cards Cho Team*
Danh sách 18 Task Cards (từ Card 0 đến Card 17) được định nghĩa rõ ràng về người thực hiện (owner), dữ liệu đầu vào (input), kết quả đầu ra (output) và tiêu chí hoàn thành (done criteria).

*   **Danh sách Task Cards chính:**
    *   **Card 0:** Chốt contract chung (Cả team).
    *   **Card 1-3:** Thu thập data mẫu, extract keyframe/thumbnail, và build manifest.jsonl (Data person).
    *   **Card 4-5:** Xây dựng visual index (CLIP/FAISS) và text index (BM25) (Retrieval person).
    *   **Card 6-9:** Viết FastAPI skeleton, media serving, search API, và dry-run submit backend (Backend person).
    *   **Card 10-13:** Tạo Vite app skeleton, kết nối API thật, hiện candidate detail/neighbor strip, và làm submit panel (Frontend person).
    *   **Card 14-16:** Thiết lập bộ query đánh giá, viết script eval (`run_eval.py`), và tổ chức mock contest nội bộ (Eval person).
    *   **Card 17:** Tái cấu trúc OOP/stub clean up (Backend + Retrieval).
*   **Quy trình làm việc hàng ngày:** Standup trả lời đúng 3 câu hỏi (Hôm qua làm gì xong? Hôm nay giao gì? Đang bị block bởi gì?) nhằm tối ưu hiệu suất và tránh tình trạng chậm trễ.

---

## 6. [training_resources.pdf](file:///d:/AIC/Refs/training_resources.pdf)
### *Tài Liệu Luyện Nội Công Cho AI Challenge 2026*
Tổng hợp các tài liệu học thuật, đường link mã nguồn mở, và lộ trình 10 ngày để nâng cao kỹ năng xử lý cho cả đội.

*   **Các tài liệu đề xuất:**
    *   **VBS DRES & Server:** Hiểu cách thức hoạt động của server chấm thi.
    *   **Các paper từ đội vô địch các năm trước:** SOMHunter (VĐ VBS 2020), vitrivr, VISIONE.
    *   **Các paper viết trực tiếp về AI Challenge HCMC 2025:** MERVIN (dùng keyframes + transcripts + summaries + PE), U-CESE (giới thiệu DAKE và ReCap), Enhanced Multimodal Video Retrieval.
    *   **Mô hình/Thư viện cốt lõi:** CLIP, SigLIP, BGE-M3 (FlagEmbedding), InternVideo2, PaddleOCR, Whisper/PhoWhisper, FAISS, Qdrant.
*   **Lộ trình luyện tập 10 ngày:**
    *   *Ngày 1-2:* Đọc luật chơi, chuẩn bị 20 query mẫu & mock submit format.
    *   *Ngày 3-4:* Đọc các paper của AI Challenge HCMC để thiết kế kiến trúc.
    *   *Ngày 5-6:* Thử nghiệm CLIP/SigLIP/BGE-M3 và làm benchmark tìm kiếm.
    *   *Ngày 7:* Làm quen PaddleOCR, Whisper/PhoWhisper cho tiếng Việt.
    *   *Ngày 8:* So sánh kỹ thuật cắt keyframe (interval vs scene-based).
    *   *Ngày 9:* Thiết kế giao diện theo các hệ thống SOMHunter, vitrivr.
    *   *Ngày 10:* Chạy mock contest thử nghiệm thời gian nộp bài thực tế.
