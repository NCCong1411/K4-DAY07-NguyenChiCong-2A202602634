# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** [Tên nhóm]  
**Thành viên:** [Họ tên từng thành viên]  
**Ngày:** [Ngày nộp]

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Chủ đề (Domain) & Lý Do Chọn

**Chủ đề:** Quy định và dịch vụ đăng ký học phần của Carnegie Mellon University (CMU).

**Tại sao nhóm chọn chủ đề này?**

> Corpus trả lời các câu hỏi thực tế của người học về đăng ký, đổi/rút học phần, thời điểm đăng ký và voucher. Nguồn là các trang công khai của University Registrar CMU; dữ liệu không có thông tin cá nhân hay nội dung cần đăng nhập. Chủ đề đáp ứng biến thể L3A về dịch vụ/quy định đại học và có nhiều `audience` để kiểm tra metadata filtering.

### Danh sách tài liệu (Data Inventory)

| #   | Tên tài liệu                           | Nguồn (Source URL)                                                                                                                             | Ngày lấy / Phiên bản    | Số ký tự | Metadata đã gán                        |
| --- | -------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------- | -------- | -------------------------------------- |
| 1   | Course Adds Drops and Withdrawals      | [https://www.cmu.edu/hub/registrar/course-changes/index.html](https://www.cmu.edu/hub/registrar/course-changes/index.html)                     | 2026-09-19 / not-stated | 7508     | student, registrar, course-changes, en |
| 2   | Course Registration                    | [https://www.cmu.edu/hub/registrar/registration/](https://www.cmu.edu/hub/registrar/registration/)                                             | 2026-09-19 / not-stated | 4200     | student, registrar, registration, en   |
| 3   | Non-Degree Faculty Registration        | [https://www.cmu.edu/hub/registrar/registration/vnd/faculty-staff.html](https://www.cmu.edu/hub/registrar/registration/vnd/faculty-staff.html) | 2026-09-19 / not-stated | 5299     | faculty, registrar, registration, en   |
| 4   | Plan Course Schedule                   | [https://www.cmu.edu/hub/registrar/courses-and-scheduling/index.html](https://www.cmu.edu/hub/registrar/courses-and-scheduling/index.html)     | 2026-09-19 / not-stated | 2116     | student, registrar, registration, en   |
| 5   | University Registrar Services Overview | [https://www.cmu.edu/hub/registrar/](https://www.cmu.edu/hub/registrar/)                                                                       | 2026-09-19 / not-stated | 1022     | all, registrar, overview, en           |
| 6   | Register for Courses in 4 Easy Steps   | [https://www.cmu.edu/hub/registrar/registration/steps/](https://www.cmu.edu/hub/registrar/registration/steps/)                                 | 2026-09-19 / not-stated | 5075     | student, registrar, registration, en   |
| 7   | Registration Start Time Assignments    | [https://www.cmu.edu/hub/registrar/registration/start-times.html](https://www.cmu.edu/hub/registrar/registration/start-times.html)             | 2026-09-19 / not-stated | 2879     | student, registrar, registration, en   |
| 8   | Non-Degree Staff Registration          | [https://www.cmu.edu/hub/registrar/registration/vnd/faculty-staff.html](https://www.cmu.edu/hub/registrar/registration/vnd/faculty-staff.html) | 2026-09-19 / not-stated | 1429     | staff, registrar, registration, en     |
| 9   | Voucher Process FAQ                    | [https://www.cmu.edu/hub/registrar/course-changes/faq.html](https://www.cmu.edu/hub/registrar/course-changes/faq.html)                         | 2026-09-19 / not-stated | 2897     | student, registrar, course-changes, en |

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**

- [x] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata                              | Kiểu   | Ví dụ giá trị                         | Tại sao hữu ích cho truy xuất (retrieval)?            |
| -------------------------------------------- | ------ | ------------------------------------- | ----------------------------------------------------- |
| doc_id                                       | string | `course-changes`                      | Liên kết mọi chunk với file gốc và nguồn gold answer. |
| title                                        | string | `Course Adds Drops and Withdrawals`   | Tên dễ đọc khi hiển thị kết quả.                      |
| audience                                     | enum   | `student`, `faculty`, `staff`, `all`  | Lọc đúng đối tượng trước retrieval.                   |
| category                                     | string | `registration`                        | Thu hẹp theo loại quy định.                           |
| department                                   | string | `registrar`                           | Hỗ trợ lọc theo đơn vị ban hành.                      |
| source_url / retrieved_at / document_version | string | URL CMU / `2026-09-19` / `not-stated` | Truy vết nguồn, thời điểm lấy và minh bạch phiên bản. |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

> Mỗi thành viên thử **một chiến lược khác nhau** trên cùng bộ tài liệu; nhóm tổng hợp và so sánh ở đây.

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare()` trên 2-3 tài liệu:

| Tài liệu                          | Chiến lược (Strategy)            | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không?            |
| --------------------------------- | -------------------------------- | -------------- | ----------------- | ----------------------------------- |
| Course Adds Drops and Withdrawals | FixedSizeChunker (`fixed_size`)  | 47             | 198.8             | Có overlap nhưng thường cắt giữa ý. |
| Course Adds Drops and Withdrawals | SentenceChunker (`by_sentences`) | 19             | 366.2             | Giữ câu, nhưng chunk khá dài.       |
| Course Adds Drops and Withdrawals | RecursiveChunker (`recursive`)   | 45             | 154.7             | Tôn trọng xuống dòng tốt hơn.       |
| Course Registration               | FixedSizeChunker (`fixed_size`)  | 26             | 196.8             | Có overlap nhưng có thể cắt giữa ý. |
| Course Registration               | SentenceChunker (`by_sentences`) | 10             | 384.0             | Giữ câu, nhưng chunk khá dài.       |
| Course Registration               | RecursiveChunker (`recursive`)   | 26             | 147.1             | Tôn trọng xuống dòng tốt hơn.       |
| Non-Degree Faculty Registration   | FixedSizeChunker (`fixed_size`)  | 33             | 197.1             | Có overlap nhưng có thể cắt giữa ý. |
| Non-Degree Faculty Registration   | SentenceChunker (`by_sentences`) | 13             | 374.2             | Giữ câu, nhưng chunk khá dài.       |
| Non-Degree Faculty Registration   | RecursiveChunker (`recursive`)   | 32             | 151.3             | Tôn trọng xuống dòng tốt hơn.       |

### Chiến lược của từng thành viên

> Mỗi thành viên điền một khối dưới đây (copy thêm nếu nhóm có nhiều hơn 3 người).

**Thành viên 1 — Nguyễn Chí Công**

- **Loại chiến lược:** custom `HeadingChunker` → `RecursiveChunker`
- **Mô tả & lý do chọn cho chủ đề này:** Trang quy định CMU có heading/mục sẵn, nên mỗi heading là đơn vị ngữ nghĩa tự nhiên. Chiến lược tách trước heading; nếu mục vượt 500 ký tự thì dùng recursive để cắt phần thân và lặp lại heading ở từng mảnh con, nhờ vậy chunk sau vẫn biết mình đang nói về mục nào.
- **Code snippet (nếu custom):**

```python
class HeadingChunker:
    # split at Markdown headings; long sections use RecursiveChunker
    # and prefix the original heading to every child chunk
```

**Thành viên 2 — [Tên]**

- **Loại chiến lược:**
- **Mô tả & lý do chọn:**
- **Code snippet (nếu custom):**

**Thành viên 3 — [Hoàng Trung Anh]**

- **Loại chiến lược:** `SentenceChunker(max_sentences_per_chunk=3)`.
- **Mô tả & lý do chọn:** Tách theo dấu kết thúc câu rồi gom tối đa ba câu liên tiếp thành một chunk. Cách này giữ nguyên câu và các bước hướng dẫn ngắn trong tài liệu đăng ký, voucher và FAQ. Ranh giới có thể cắt giữa một quy trình nhiều câu, và chunk dài không bị giới hạn theo số ký tự; cần đối chiếu top-3 với đáp án chuẩn để đánh giá.
- **Code snippet:** Dùng lớp có sẵn trong `src/chunking.py`; dòng chọn chiến lược trong `bench.py` là:

```python
CHUNKER = SentenceChunker(max_sentences_per_chunk=3)
```

### So Sánh Giữa Các Thành Viên

| Thành viên | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
| ---------- | --------------------- | -------------------- | --------- | -------- |
|            |                       |                      |           |          |
|            |                       |                      |           |          |
|            |                       |                      |           |          |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**

> *Viết 2-3 câu — đây là phần được đánh giá cao nhất (khả năng suy nghĩ & giải thích):*

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

> **Đúng 5 câu hỏi**, đa dạng, có thể kiểm chứng; **ít nhất 1 câu** cần lọc metadata mới trả lời tốt. Đây là bộ câu hỏi chung cho mọi thành viên chạy.

| #   | Câu hỏi (Query)                                                         | Câu trả lời chuẩn (Gold Answer)                                                                                                      | Chunk nào chứa thông tin?  |
| --- | ----------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ | -------------------------- |
| 1   | Quy trình đăng ký hai lớp trùng giờ là gì?                              | Gửi Course Time Conflict Request trên SIO; advisor và hai giảng viên phê duyệt, sau đó sinh viên chấp nhận điều kiện và đăng ký.     | `course-registration`      |
| 2   | Sinh viên đại học năm nhất đăng ký vào ngày nào trong kỳ thu/xuân?      | Thứ Sáu.                                                                                                                             | `registration-start-times` |
| 3   | Trước khi dùng voucher sau hạn drop/P/NP, sinh viên phải làm gì?        | Trao đổi với primary academic advisor; advisor nhập voucher vào S3, sinh viên xác nhận trong 24 giờ.                                 | `course-changes`           |
| 4   | Sinh viên đại học có bao nhiêu voucher trong toàn khóa và trong một kỳ? | Ba voucher toàn khóa; tối đa một voucher mỗi kỳ (kể cả hè).                                                                          | `course-changes`           |
| 5   | Tôi có giờ bắt đầu đăng ký cụ thể không?                                | Với sinh viên, giờ được gán và xem ở trang Registration hoặc Plan Schedule trong SIO; undergraduate dùng ba chữ số cuối của ID Card. | `registration-start-times` |

### Tổng hợp chất lượng truy xuất của nhóm

> Cách chấm (theo `docs/SCORING.md`): **2 điểm/câu** — top-3 chứa chunk liên quan + agent trả lời đúng (2), có liên quan nhưng thiếu/không ở top-1 (1), không có trong top-3 (0).

| #   | Câu hỏi                             | Chiến lược tốt nhất cho câu này                 | Có chunk liên quan trong top-3?                    | Ghi chú                                                           |
| --- | ----------------------------------- | ----------------------------------------------- | -------------------------------------------------- | ----------------------------------------------------------------- |
| 1   | Quy trình đăng ký lớp trùng giờ     | HeadingChunker + Recursive                      | Có, top-1: `course-registration`, score 0.764      | Chunk mô tả đúng Course Time Conflict Request và chuỗi phê duyệt. |
| 2   | Ngày đăng ký của sinh viên năm nhất | HeadingChunker + Recursive                      | Có, top-1: `registration-start-times`, score 0.760 | Chunk nêu rõ Friday.                                              |
| 3   | Thao tác trước khi dùng voucher     | HeadingChunker + Recursive + `audience=student` | Có, top-1: `course-changes`, score 0.783           | Lọc bỏ chunk faculty/staff trước xếp hạng.                        |
| 4   | Số voucher của undergraduate        | HeadingChunker + Recursive + `audience=student` | Có, top-1: `course-changes`, score 0.842           | Chunk chứa chính xác ba voucher và một mỗi kỳ.                    |
| 5   | Vị trí xem start time trong SIO     | HeadingChunker + Recursive + `audience=student` | Có, top-1: `registration-four-steps`, score 0.821  | Chunk chứa đúng Registration page / Course Schedule tab.          |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**

> Có. Query 3, 4 và 5 gọi `search_with_filter(..., metadata_filter={"audience": "student"})`, nên các chunk faculty/staff/all bị loại **trước** khi xếp hạng. Điều này đặc biệt cần khi các tài liệu cùng nói về registration nhưng quy tắc áp dụng cho các đối tượng khác nhau; không lọc, top-k có thể bị chiếm bởi chunk sai đối tượng.

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**

> *Liệt kê 2-3 ý:*

**Bài học rút ra khi so sánh trong nhóm:**

> *Viết 2-3 câu — cùng tài liệu nhưng chiến lược khác nhau dẫn tới khác biệt gì?*

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**

> *Viết 2-3 câu:*

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí                                 | Điểm tự đánh giá |
| ---------------------------------------- | ---------------- |
| Lựa chọn tài liệu (Document Set Quality) | / 10             |
| Thiết kế chiến lược (Strategy Design)    | / 15             |
| Chất lượng truy xuất (Retrieval Quality) | / 10             |
| Thuyết trình (Demo)                      | / 5              |
| **Tổng phần nhóm**                       | **/ 40**         |
