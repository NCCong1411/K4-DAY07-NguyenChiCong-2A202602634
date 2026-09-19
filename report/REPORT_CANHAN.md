# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Nguyễn Chí Công  
**Nhóm:** Akatsuki  
**Ngày:** 2026-09-19

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**

> Độ tương tự cosine cao nghĩa là hai embedding có hướng gần nhau trong không gian vector. Với văn bản, điều này thường cho thấy hai câu có nội dung hoặc ý nghĩa gần nhau, kể cả khi chúng không dùng đúng các từ giống nhau.

**Ví dụ có độ tương tự CAO:**

- Câu A: Sinh viên cần đăng ký học phần trước khi bắt đầu học kỳ.
- Câu B: Trước mỗi học kỳ, người học phải hoàn tất việc ghi danh các môn học.
- Tại sao tương đồng: Hai câu cùng diễn đạt yêu cầu hoàn tất đăng ký môn học trước học kỳ, nhưng dùng từ vựng khác nhau.

**Ví dụ có độ tương tự THẤP:**

- Câu A: Sinh viên cần đăng ký học phần trước khi bắt đầu học kỳ.
- Câu B: Thư viện cho mượn máy tính bảng trong bảy ngày.
- Tại sao khác: Một câu nói về quy trình đăng ký môn học, câu còn lại nói về dịch vụ mượn thiết bị của thư viện; mục đích và thông tin chính không liên quan.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**

> Cosine so sánh hướng của embedding nên tập trung vào mức độ giống nhau về ngữ nghĩa, ít bị ảnh hưởng bởi độ lớn vector hoặc độ dài câu. Khoảng cách Euclid đo độ xa tuyệt đối, vì vậy có thể nhạy hơn với độ lớn vector dù hai văn bản có hướng ngữ nghĩa tương tự.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**

> Trình bày phép tính: ceil((10,000 - 50) / (500 - 50)) = ceil(9,950 / 450) = ceil(22.11...) = 23.  
> Đáp án: 23 chunks. Đã kiểm chứng bằng `FixedSizeChunker(chunk_size=500, overlap=50).chunk('a' * 10000)`, kết quả là 23.

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**

> Khi overlap là 100: ceil((10,000 - 100) / (500 - 100)) = ceil(9,900 / 400) = ceil(24.75) = 25 chunks. Overlap lớn hơn giữ được ngữ cảnh ở ranh giới giữa hai chunk, nhưng làm tăng số chunk, chi phí lưu trữ và khả năng kết quả truy xuất bị trùng lặp.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:

> Tôi dùng regex `(?<=[.!?])\s+` để tách tại khoảng trắng sau dấu kết thúc câu, nhờ đó dấu `.`, `!`, `?` vẫn được giữ lại trong chunk. Text rỗng hoặc chỉ có khoảng trắng trả về `[]`; tuy nhiên cách này chưa phân biệt được chữ viết tắt như `TS.` hoặc số thập phân như `3.14`, nên các trường hợp đó có thể bị tách sai.

**`RecursiveChunker.chunk` / `_split**` — hướng tiếp cận:

> Thuật toán thử separator theo thứ tự `\n\n`, `\n`, `. `, dấu cách rồi chuỗi rỗng để ưu tiên ranh giới có ý nghĩa. Mảnh quá `chunk_size` được đệ quy với separator còn lại; mảnh nhỏ liền kề được gom lại sát ngưỡng để tránh sinh hàng trăm chunk vụn. Base case là mảnh đã đủ ngắn, hoặc hết separator thì cắt theo ký tự với độ dài tối đa `chunk_size`.

### Lớp EmbeddingStore

**`add_documents` + `search**` — hướng tiếp cận:

> Chunking diễn ra bên ngoài store; mỗi `Document` đầu vào trở thành đúng một record in-memory gồm id, content, bản sao metadata và embedding. `search()` embedding query rồi tính dot product với vector đã chuẩn hoá, nên tương đương cosine similarity, sắp xếp giảm dần và trả tối đa `top_k` record không kèm vector dài.

**`search_with_filter` + `delete_document**` — hướng tiếp cận:

> `search_with_filter()` lọc metadata **trước** rồi mới tính similarity, tránh để top-k bị chiếm bởi chunk sai audience. `delete_document(doc_id)` loại toàn bộ record có `metadata['doc_id']` trùng id file gốc và trả `True` khi thực sự xoá được ít nhất một chunk.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:

> Agent lấy top-k chunk trước, đánh số `[1]`, `[2]`, ... và đưa cả `doc_id` lẫn nội dung vào context của prompt. Prompt bắt buộc chỉ dùng context, yêu cầu trích dẫn số nguồn và nói rõ không tìm thấy khi thiếu thông tin. Nếu store rỗng, agent trả thông báo ngay thay vì gọi LLM vô ích.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
$ pytest tests/ -v
============================= test session starts =============================
tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED
tests/test_solution.py::TestProjectStructure::test_src_package_exists PASSED
tests/test_solution.py::TestClassBasedInterfaces::test_chunker_classes_exist PASSED
tests/test_solution.py::TestClassBasedInterfaces::test_mock_embedder_exists PASSED
tests/test_solution.py::TestFixedSizeChunker::test_chunks_respect_size PASSED
tests/test_solution.py::TestFixedSizeChunker::test_correct_number_of_chunks_no_overlap PASSED
tests/test_solution.py::TestFixedSizeChunker::test_empty_text_returns_empty_list PASSED
tests/test_solution.py::TestFixedSizeChunker::test_no_overlap_no_shared_content PASSED
tests/test_solution.py::TestFixedSizeChunker::test_overlap_creates_shared_content PASSED
tests/test_solution.py::TestFixedSizeChunker::test_returns_list PASSED
tests/test_solution.py::TestFixedSizeChunker::test_single_chunk_if_text_shorter PASSED
tests/test_solution.py::TestSentenceChunker::test_chunks_are_strings PASSED
tests/test_solution.py::TestSentenceChunker::test_respects_max_sentences PASSED
tests/test_solution.py::TestSentenceChunker::test_returns_list PASSED
tests/test_solution.py::TestSentenceChunker::test_single_sentence_max_gives_many_chunks PASSED
tests/test_solution.py::TestRecursiveChunker::test_chunks_within_size_when_possible PASSED
tests/test_solution.py::TestRecursiveChunker::test_empty_separators_falls_back_gracefully PASSED
tests/test_solution.py::TestRecursiveChunker::test_handles_double_newline_separator PASSED
tests/test_solution.py::TestRecursiveChunker::test_returns_list PASSED
tests/test_solution.py::TestEmbeddingStore::test_add_documents_increases_size PASSED
tests/test_solution.py::TestEmbeddingStore::test_add_more_increases_further PASSED
tests/test_solution.py::TestEmbeddingStore::test_initial_size_is_zero PASSED
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_content_key PASSED
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_score_key PASSED
tests/test_solution.py::TestEmbeddingStore::test_search_results_sorted_by_score_descending PASSED
tests/test_solution.py::TestEmbeddingStore::test_search_returns_at_most_top_k PASSED
tests/test_solution.py::TestEmbeddingStore::test_search_returns_list PASSED
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_non_empty PASSED
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_returns_string PASSED
tests/test_solution.py::TestComputeSimilarity::test_identical_vectors_return_1 PASSED
tests/test_solution.py::TestComputeSimilarity::test_opposite_vectors_return_minus_1 PASSED
tests/test_solution.py::TestComputeSimilarity::test_orthogonal_vectors_return_0 PASSED
tests/test_solution.py::TestComputeSimilarity::test_zero_vector_returns_0 PASSED
tests/test_solution.py::TestCompareChunkingStrategies::test_counts_are_positive PASSED
tests/test_solution.py::TestCompareChunkingStrategies::test_each_strategy_has_count_and_avg_length PASSED
tests/test_solution.py::TestCompareChunkingStrategies::test_returns_three_strategies PASSED
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_filter_by_department PASSED
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_no_filter_returns_all_candidates PASSED
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_returns_at_most_top_k PASSED
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_reduces_collection_size PASSED
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_false_for_nonexistent_doc PASSED
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED
============================== 42 passed in 0.06s ==============================
```

**Số lượng bài test vượt qua (pass):** 42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A | Câu B | Dự đoán    | Điểm thực tế | Đúng? |
| --- | ----- | ----- | ---------- | ------------ | ----- |
| 1 | Students submit a Course Time Conflict Request through SIO. | To enroll in overlapping classes, a student files a time-conflict request in SIO. | cao | 0.769 | Đúng |
| 2 | Undergraduate students may use three vouchers during their career. | First-year undergraduate students register on Friday. | trung bình | 0.413 | Đúng |
| 3 | Registration start times are shown on the SIO Registration page. | Students should consult their academic advisor before using a voucher. | thấp | 0.186 | Đúng |
| 4 | Faculty must submit a non-degree petition by the first day of classes. | Staff must submit a non-degree petition by the first day of classes. | cao | 0.933 | Đúng |
| 5 | Dropped courses before the add/drop deadline do not appear on the transcript. | A course withdrawal produces a W grade on the transcript. | trung bình | 0.594 | Đúng |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**

> Cặp 4 cao nhất (0.933) dù đổi `Faculty` thành `Staff`: embedding nhận ra cấu trúc quy định, hành động và hạn chót gần như giống nhau. Cặp 5 đạt 0.594 thay vì thấp vì cả hai đều nói về thay đổi học phần và ảnh hưởng lên transcript, nhưng kết quả quy định khác nhau (không hiện môn học so với điểm W).

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

| #   | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
| --- | --------------- | ------------------------------------ | ---------- | ------------------------------ | ------------------------------- |
| 1 | Quy trình đăng ký hai lớp trùng giờ? | `course-registration`: Course Time Conflict Request trên SIO, điều kiện và hạn gửi. | 0.764 | Có, top-1 chứa request; top-2 chứa chấp nhận điều kiện/đăng ký. | Agent: gửi request trên SIO, đáp ứng prerequisites/reservations, chấp nhận điều kiện rồi đăng ký; gửi trước hạn add ít nhất 5 ngày `[1][2]`. |
| 2 | Sinh viên năm nhất đăng ký ngày nào? | `registration-start-times`: lịch đăng ký theo năm học. | 0.760 | Có, top-1 nêu “first-years register on Friday”. | Agent: Thứ Sáu trong kỳ thu và xuân `[1]`. |
| 3 | Cần làm gì trước khi dùng voucher? | `course-changes`: advisor và voucher process. | 0.783 | Có, top-1 chứa thao tác trước khi dùng. | Agent: phải trao đổi với primary academic advisor trước `[1][2]`. |
| 4 | Undergraduate có bao nhiêu voucher? | `course-changes`: “three vouchers” và “one voucher per semester”. | 0.842 | Có, top-1 chứa cả hai con số. | Agent: ba voucher toàn khóa; tối đa một voucher mỗi kỳ, kể cả hè `[1]`. |
| 5 | Tôi có giờ bắt đầu đăng ký cụ thể không? | `registration-start-times`: start time ở Registration/Plan Schedule trong SIO. | 0.618 | Có, top-1 chứa đáp án sinh viên. | Agent: Có; giờ được gán theo ba số cuối ID Card và xem trên Registration/Plan Schedule trong SIO `[1][3]`. |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** 5 / 5

**Thiết lập & kiểm tra A/B:** Tôi dùng `HeadingChunker → RecursiveChunker`, `text-embedding-3-small`, 75 chunks và top_k=3. Với query 3–5, tôi đã chạy cả `metadata_filter={"audience": "student"}` và không filter; output đầy đủ ở `ket_qua_benchmark.txt`. Tôi cũng chạy `python bench.py --chunker heading --filter-mode on --with-agent`; agent OpenAI trả lời có citation `[1]`, `[2]`, ... như bảng trên. Filter được áp dụng trước retrieval, nhưng top-3 quan sát được chưa đổi vì các chunk `student` đã có điểm semantic cao nhất. Đây là giới hạn của bộ query hiện tại: để chứng minh lợi ích thứ hạng rõ hơn, nhóm cần một query mơ hồ hơn giữa `student` và `faculty/staff` có đáp án khác nhau.

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**

> Chunk theo heading giúp giữ các mục quy định như Voucher Process hoặc Start Time Assignments trọn nghĩa; khi section dài, heading vẫn được lặp lại trong các mảnh con. Tôi cũng học được rằng kiểm tra đúng `doc_id` là chưa đủ: phải đọc nội dung chunk để chắc rằng nó thật sự chứa câu trả lời, đặc biệt với tài liệu dài có nhiều section cùng chủ đề.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí                                        | Điểm tự đánh giá |
| ----------------------------------------------- | ---------------- |
| Khởi động (Warm-up)                             | 5 / 5            |
| Hướng tiếp cận của tôi (My Approach)            | 10 / 10          |
| Hoàn thiện code (Core Implementation — tests)   | 30 / 30          |
| Dự đoán độ tương tự (Similarity Predictions)    | 5 / 5            |
| Kết quả truy xuất của tôi (Competition Results) | 10 / 10          |
| **Tổng phần cá nhân**                           | **60 / 60**      |
