# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** Akatsuki

**Thành viên:**

- Vũ Đình Đăng — 2A202602946
- Nguyễn Chí Công — 2A202602634
- Hoàng Trung Anh — 2A202602521

**Ngày:** 2026-09-19

**Ngày lập báo cáo:** 19/09/2026

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Chủ đề (Domain) & Lý Do Chọn

**Chủ đề:** Quy định và dịch vụ đăng ký học phần của Carnegie Mellon University (CMU).

**Tại sao nhóm chọn chủ đề này?**

> Chín tài liệu công khai từ University Registrar cùng xoay quanh lập lịch, đăng ký học phần, giờ bắt đầu đăng ký, thay đổi học phần và voucher. Các quy trình này có mốc thời gian, điều kiện và đối tượng áp dụng cụ thể, nên phù hợp để kiểm tra liệu hệ thống có truy xuất đúng đoạn làm căn cứ cho câu trả lời. Bộ tài liệu có bốn giá trị `audience` (`student`, `faculty`, `staff`, `all`), cho phép thử lọc metadata theo người dùng.

### Danh sách tài liệu (Data Inventory)

Số ký tự được tính trên phần nội dung sau YAML frontmatter của từng file `.md` (gồm tiêu đề trong nội dung, không tính metadata). Cả 9 tài liệu đều có `department=registrar`, `language=en`, `retrieved_at=2026-09-19` và `document_version=not-stated`.

| #   | Tên tài liệu                                                                                            | Nguồn (Source URL)                                                                     | Ngày lấy / Phiên bản    | Số ký tự | Metadata đã gán                                                                             |
| --- | ------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- | ----------------------- | -------- | ------------------------------------------------------------------------------------------- |
| 1   | [Course Adds Drops and Withdrawals](../data/university_services/course-changes.md)                      | [CMU Registrar](https://www.cmu.edu/hub/registrar/course-changes/index.html)           | 2026-09-19 / not-stated | 7.040    | `doc_id=course-changes`; `audience=student`; `category=course-changes`                      |
| 2   | [Course Registration](../data/university_services/course-registration.md)                               | [CMU Registrar](https://www.cmu.edu/hub/registrar/registration/)                       | 2026-09-19 / not-stated | 3.865    | `doc_id=course-registration`; `audience=student`; `category=registration`                   |
| 3   | [Non-Degree Faculty Registration](../data/university_services/faculty-staff-non-degree-registration.md) | [CMU Registrar](https://www.cmu.edu/hub/registrar/registration/vnd/faculty-staff.html) | 2026-09-19 / not-stated | 4.900    | `doc_id=faculty-staff-non-degree-registration`; `audience=faculty`; `category=registration` |
| 4   | [Non-Degree Staff Registration](../data/university_services/staff-non-degree-registration.md)           | [CMU Registrar](https://www.cmu.edu/hub/registrar/registration/vnd/faculty-staff.html) | 2026-09-19 / not-stated | 1.116    | `doc_id=staff-non-degree-registration`; `audience=staff`; `category=registration`           |
| 5   | [Plan Course Schedule](../data/university_services/plan-course-schedule.md)                             | [CMU Registrar](https://www.cmu.edu/hub/registrar/courses-and-scheduling/index.html)   | 2026-09-19 / not-stated | 1.775    | `doc_id=plan-course-schedule`; `audience=student`; `category=registration-planning`         |
| 6   | [University Registrar Services Overview](../data/university_services/registrar-services-overview.md)    | [CMU Registrar](https://www.cmu.edu/hub/registrar/)                                    | 2026-09-19 / not-stated | 711      | `doc_id=registrar-services-overview`; `audience=all`; `category=registration-services`      |
| 7   | [Register for Courses in 4 Easy Steps](../data/university_services/registration-four-steps.md)          | [CMU Registrar](https://www.cmu.edu/hub/registrar/registration/steps/)                 | 2026-09-19 / not-stated | 4.695    | `doc_id=registration-four-steps`; `audience=student`; `category=registration`               |
| 8   | [Registration Start Time Assignments](../data/university_services/registration-start-times.md)          | [CMU Registrar](https://www.cmu.edu/hub/registrar/registration/start-times.html)       | 2026-09-19 / not-stated | 2.515    | `doc_id=registration-start-times`; `audience=student`; `category=registration`              |
| 9   | [Voucher Process Frequently Asked Questions](../data/university_services/voucher-process-faq.md)        | [CMU Registrar](https://www.cmu.edu/hub/registrar/course-changes/faq.html)             | 2026-09-19 / not-stated | 2.540    | `doc_id=voucher-process-faq`; `audience=student`; `category=course-changes`                 |

Hai file về đăng ký học không cấp bằng cho giảng viên và nhân viên cùng trích từ một URL, nhưng được tách theo `audience`. `sources.csv` ghi một dòng cho mỗi file.

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**

- [x] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata    | Kiểu                                           | Ví dụ giá trị                                     | Tại sao hữu ích cho truy xuất (retrieval)?                                                                                 |
| ------------------ | ---------------------------------------------- | ------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| `doc_id`           | Chuỗi, duy nhất                                | `course-registration`                             | Gắn các chunk với tài liệu gốc để truy vết và xóa theo tài liệu.                                                           |
| `title`            | Chuỗi                                          | `Course Registration`                             | Hiển thị tên tài liệu trong kết quả và giúp nhận diện nội dung nguồn.                                                      |
| `source_url`       | URL                                            | `https://www.cmu.edu/hub/registrar/registration/` | Dẫn về trang nguồn để kiểm chứng câu trả lời.                                                                              |
| `retrieved_at`     | Ngày `YYYY-MM-DD`                              | `2026-09-19`                                      | Cho biết thời điểm nhóm lấy nội dung, hỗ trợ kiểm tra độ mới.                                                              |
| `document_version` | Chuỗi                                          | `not-stated`                                      | Ghi phiên bản hoặc ngày hiệu lực để đối chiếu quy định; các file hiện đang ghi `not-stated`.                               |
| `audience`         | Một trong `student`, `faculty`, `staff`, `all` | `student`                                         | Lọc đúng nhóm người được áp dụng quy định; corpus hiện có cả bốn giá trị.                                                  |
| `department`       | Chuỗi                                          | `registrar`                                       | Xác định đơn vị phụ trách; hiện tất cả tài liệu cùng giá trị nên trường này chưa phân biệt được các tài liệu trong corpus. |
| `category`         | Chuỗi                                          | `registration`, `course-changes`                  | Giới hạn tìm kiếm theo loại dịch vụ/quy trình khi cần.                                                                     |
| `language`         | Mã ngôn ngữ                                    | `en`                                              | Cho biết ngôn ngữ tài liệu; hiện tất cả tài liệu là tiếng Anh nên trường này chưa có tác dụng lọc trong corpus hiện tại.   |

Trường `license_or_permission=public-source` được lưu trong `sources.csv` để ghi căn cứ sử dụng nguồn, không nằm trong YAML frontmatter của các file `.md`.

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

> Mỗi thành viên thử **một chiến lược khác nhau** trên cùng bộ tài liệu; nhóm tổng hợp và so sánh ở đây.

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare(body, chunk_size=200)` trên ba tài liệu dưới đây. `body` là nội dung sau YAML frontmatter (`text.split("---", 2)[2].strip()`), vì metadata không phải phần cần chia chunk. Trong comparator, `fixed_size` dùng `overlap=0`, còn `by_sentences` gom tối đa ba câu nên có thể tạo chunk dài hơn 200 ký tự. Nhận xét ngữ cảnh dựa trên việc đọc ranh giới các chunk, không phải điểm benchmark truy xuất.

| Tài liệu                           | Chiến lược (Strategy)            | Số lượng Chunk | Độ dài trung bình (ký tự) | Giữ được ngữ cảnh không?                           |
| ---------------------------------- | -------------------------------- | -------------- | ------------------------- | -------------------------------------------------- |
| `course-registration.md`           | FixedSizeChunker (`fixed_size`)  | 20             | 193,2                     | Không tốt: có ranh giới cắt giữa từ.               |
| `course-registration.md`           | SentenceChunker (`by_sentences`) | 10             | 384,0                     | Giữ trọn câu, nhưng chunk khá dài.                 |
| `course-registration.md`           | RecursiveChunker (`recursive`)   | 26             | 148,7                     | Tương đối tốt ở ranh giới câu và đoạn.             |
| `staff-non-degree-registration.md` | FixedSizeChunker (`fixed_size`)  | 6              | 186,0                     | Không tốt: cắt giữa “Staff” và “members”.          |
| `staff-non-degree-registration.md` | SentenceChunker (`by_sentences`) | 3              | 370,3                     | Giữ trọn câu nhưng không giữ rõ cấu trúc heading.  |
| `staff-non-degree-registration.md` | RecursiveChunker (`recursive`)   | 7              | 159,4                     | Tương đối: có heading tách khỏi nội dung ngay sau. |
| `course-changes.md`                | FixedSizeChunker (`fixed_size`)  | 36             | 195,6                     | Không tốt: có ranh giới cắt giữa từ.               |
| `course-changes.md`                | SentenceChunker (`by_sentences`) | 19             | 366,1                     | Giữ trọn câu, nhưng chunk dài hơn 200 ký tự.       |
| `course-changes.md`                | RecursiveChunker (`recursive`)   | 44             | 160,0                     | Tương đối: chunk đầu chỉ chứa tiêu đề.             |

### Chiến lược của từng thành viên

Thông tin thành viên và mã sinh viên lấy từ phần nhóm đã bổ sung. Nguyễn Chí Công có log chạy embedding và agent cho chiến lược Heading → Recursive; Vũ Đình Đăng chưa có log trong dự án, nên không tự suy đoán điểm cho thành viên này.

**Thành viên 1 — Nguyễn Chí Công**

- **Loại chiến lược:** custom `HeadingChunker` → `RecursiveChunker(chunk_size=500)`
- **Mô tả & lý do chọn cho chủ đề này:** Trang quy định CMU có heading/mục sẵn, nên mỗi heading là đơn vị ngữ nghĩa tự nhiên. Chiến lược tách trước heading; nếu mục vượt 500 ký tự thì dùng recursive để cắt phần thân và lặp lại heading ở từng mảnh con, nhờ vậy chunk sau vẫn biết mình đang nói về mục nào.
- **Mã thực thi & checkpoint:** `src/chunking.py:HeadingChunker`; chọn bằng `bench.py --chunker heading`. Hai test xác minh tách ở Markdown heading và lặp heading khi section dài; hai test benchmark chung kiểm tra đầy đủ cụm từ gold trong top-3. Toàn bộ `pytest tests/ -v` đạt 46/46. Trên corpus đã đồng bộ với nhóm, chiến lược tạo 81 chunks, chunk dài nhất 498 ký tự, không chunk nào vượt 500. Chạy `text-embedding-3-small`, `top_k=3` và agent có citation: 6/10 (Q2, Q4, Q5 đúng; Q1 không có gold trong top-3; Q3 thiếu S3/24 giờ).

**Thành viên 2 — Vũ Đình Đăng (2A202602946)**

- **Loại chiến lược:** Heading-aware + `RecursiveChunker(chunk_size=900)`
- **Mô tả & lý do chọn:** Tách theo heading giữ các bước/quy định trong cùng mục Markdown; section quá dài được tách tiếp theo paragraph/câu.
- **Code:** `scripts/evaluate_benchmarks.py:chunk_by_heading`.

**Thành viên 3 — Hoàng Trung Anh**

- **Loại chiến lược:** `SentenceChunker(max_sentences_per_chunk=3)`.
- **Mô tả & lý do chọn:** Tách theo dấu kết thúc câu rồi gom tối đa ba câu liên tiếp thành một chunk. Cách này giữ nguyên câu và các bước hướng dẫn ngắn trong tài liệu đăng ký, voucher và FAQ. Ranh giới có thể cắt giữa một quy trình nhiều câu, và chunk dài không bị giới hạn theo số ký tự; cần đối chiếu top-3 với đáp án chuẩn để đánh giá.
- **Code snippet:** Dùng lớp có sẵn trong `src/chunking.py`; dòng chọn chiến lược trong `bench.py` là:

```python
CHUNKER = SentenceChunker(max_sentences_per_chunk=3)
```

### So Sánh Giữa Các Thành Viên

| Thành viên      | Chiến lược                                   | Kết quả hiện có                                                                                                                                            | Điểm mạnh                                                    | Điểm yếu / giới hạn                                                           |
| --------------- | -------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------ | ----------------------------------------------------------------------------- |
| Nguyễn Chí Công | Heading → Recursive (`chunk_size=500`)       | 81 chunks, tối đa 498 ký tự, 46/46 tests; `text-embedding-3-small` + agent: 6/10.                                                                      | Giữ heading ở mỗi mảnh của section dài.                      | Corpus ít heading phụ; Q1 không có gold top-3, Q3 thiếu bước S3/24 giờ.      |
| Vũ Đình Đăng    | Heading-aware + Recursive (`chunk_size=900`) | Đã có mô tả chiến lược và đường dẫn code `scripts/evaluate_benchmarks.py`, nhưng file/log không có trong working tree nên chưa thể chạy lại hoặc chấm /10. | Giữ section và giảm việc cắt giữa các mục.                   | Chưa có kết quả top-3, backend và log để đối chiếu.                           |
| Hoàng Trung Anh | SentenceChunker, 3 câu/chunk                 | 75 chunk; gold `doc_id` 5/5, có đủ nội dung đáp án 2/5, 4/10 điểm retrieval tạm; câu 5 tăng từ 0/2 lên 2/2 nhờ lọc student.                                | Không cắt giữa câu; filter đã lấy được đoạn ID Card ở câu 5. | Quy trình nhiều bước có thể trải qua nhiều chunk; chunk dài nhất 1.148 ký tự. |

**Đối chứng có thể chạy lại trên cùng corpus, năm câu hỏi, `top_k=3` và mô hình local đa ngữ:** [`ket_qua_cp6.txt`](../ket_qua_cp6.txt). FixedSize và Recursive trong bảng sau là đường cơ sở kỹ thuật để nhóm tham khảo; chúng không thay cho log Heading-aware của Nguyễn Chí Công hoặc Vũ Đình Đăng.

| Chiến lược                      | Số chunk | Độ dài TB / tối đa (ký tự) | Gold `doc_id` trong top-3 | Đủ chuỗi đáp án trong top-3 | Điểm retrieval tạm, không lọc |
| ------------------------------- | -------- | -------------------------- | ------------------------- | --------------------------- | ----------------------------- |
| FixedSize (`500`, overlap `50`) | 68       | 472,2 / 500                | 5/5                       | 2/5                         | 4/10                          |
| Sentence (`3` câu)              | 75       | 385,8 / 1.148              | 5/5                       | 2/5                         | 4/10                          |
| Recursive (`500`)               | 75       | 388,8 / 499                | 4/5                       | 3/5                         | 6/10                          |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**

> Trong ba đường cơ sở có thể tái lập, Recursive dẫn đầu về số câu có đủ dữ kiện trong top-3 (3/5, 6/10 điểm retrieval tạm), còn FixedSize và Sentence cùng 2/5, 4/10. Chưa thể xếp hạng ba thành viên vì hai log Heading-aware chưa có trong dự án. Đây chỉ là điểm truy xuất; rubric đầy đủ còn yêu cầu kiểm tra câu trả lời agent.

**Failure case (câu 3, SentenceChunker):** Top-3 là `course-changes#14` (0,788), `#16` (0,747) và `#1` (0,668), đều đúng `doc_id` nhưng không có `primary academic advisor`, `Student Services Suite (S3)` và `within 24 hours`; ba dữ kiện nằm ở `#17–#18`. Các chunk về voucher hoặc course changes giống chủ đề câu hỏi nên có cosine cao, trong khi thông tin thao tác bị chia qua hai chunk và không có overlap. Cách sửa cần thử là gộp mục Voucher Instructions thành một đơn vị hoặc thêm chồng lấp một câu giữa các chunk, rồi chạy lại cùng mô hình để kiểm tra top-3 và câu trả lời agent.

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

Năm câu hỏi dùng chung đều có căn cứ trong corpus. Cột cuối giữ `doc_id` của tài liệu nguồn để `bench.py` đọc đúng bộ câu hỏi. Điều kiện “ít nhất một câu cần lọc `audience=student` mới trả lời đúng” chưa được chứng minh bằng lượt chạy hiện có (xem đối chiếu câu 5 bên dưới).

| #   | Câu hỏi (Query)                                                                                          | Câu trả lời chuẩn (Gold Answer)                                                                                                                         | Tài liệu nguồn (`doc_id`)  |
| --- | -------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------- |
| 1   | Quy trình đăng ký hai lớp trùng giờ là gì?                                                               | Gửi Course Time Conflict Request trên SIO; advisor và hai giảng viên phê duyệt, sau đó sinh viên chấp nhận điều kiện và đăng ký.                        | `course-registration`      |
| 2   | Sinh viên đại học năm nhất đăng ký vào ngày nào trong kỳ thu/xuân?                                       | Thứ Sáu.                                                                                                                                                | `registration-start-times` |
| 3   | Trước khi dùng voucher sau hạn drop/P/NP, sinh viên phải làm gì?                                         | Trao đổi với primary academic advisor; advisor nhập voucher vào S3, sinh viên xác nhận trong 24 giờ.                                                    | `course-changes`           |
| 4   | Sinh viên đại học có bao nhiêu voucher trong toàn khóa và trong một kỳ?                                  | Ba voucher toàn khóa; tối đa một voucher mỗi kỳ (kể cả hè).                                                                                             | `course-changes`           |
| 5   | Nếu là sinh viên đại học, giờ đăng ký học phần được xếp theo ID Card hay phải đợi hết Registration Week? | Giờ đăng ký của undergraduate được gán dựa trên ba chữ số cuối ID Card; sinh viên có thể đăng ký từ giờ được gán, không phải đợi hết Registration Week. | `registration-start-times` |

Trong lượt SentenceChunker hiện tại, các đoạn chứa dữ kiện tương ứng là: câu 1 `course-registration#5–#7`; câu 2 `registration-start-times#2`; câu 3 `course-changes#17–#18`; câu 4 `course-changes#15`; câu 5 `registration-start-times#1` và `#3`. Việc một đáp án nằm ở nhiều chunk là giới hạn cần tính khi đánh giá top-3.

### Tổng hợp chất lượng truy xuất của nhóm

Theo `docs/SCORING.md`, mỗi câu có tối đa 2 điểm nếu top-3 chứa căn cứ liên quan và câu trả lời của agent chính xác. Kết quả có thể tái lập lấy từ [`ket_qua_cp6.txt`](../ket_qua_cp6.txt), dùng `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`, `top_k=3`, và có A/B cho câu 5. Chưa có câu trả lời agent trong dự án, nên các điểm dưới đây là điểm retrieval tạm, chưa phải điểm rubric đầy đủ.

| #   | Heading → Recursive (OpenAI + agent) | SentenceChunker (đã chạy)                                                       | Đối chiếu với đáp án chuẩn                                                  |
| --- | ---------------------------------------------- | ---------------------------------------------------------------------------------- | --------------------------------------------------------------------------- |
| 1   | Gold `doc_id` không có trong top-3; agent nói không tìm thấy; 0/2 | `course-registration` hạng 3 nhưng thiếu chuỗi đáp án                              | Gold doc đúng chủ đề nhưng top-3 không chứa đủ quy trình.                   |
| 2   | `registration-start-times#3` hạng 1, agent trả lời Friday `[1]`; 2/2 | `registration-start-times` hạng 1, đủ “Friday”                                     | Đạt mức nội dung ở top-1.                                                   |
| 3   | `course-changes#12` hạng 1 nhưng top-3 thiếu S3/24 giờ; agent chỉ nêu advisor; 0/2 | `course-changes` hạng 1 nhưng thiếu S3 và 24 giờ                                   | Failure do các bước thao tác nằm ở chunk khác.                              |
| 4   | `course-changes#14` hạng 1; agent trả lời đúng ba/một voucher `[1]`; 2/2 | `course-changes` hạng 1, đủ ba voucher và một mỗi kỳ                               | Đạt mức nội dung ở top-1.                                                   |
| 5   | `registration-start-times#3`/`#0` trong top-3; agent trả lời đúng ID Card/có thể đăng ký `[3]`; 2/2 | Không lọc: gold hạng 1 nhưng thiếu ID Card; lọc student: gold hạng 1 và đủ ID Card | A/B cho thấy filter loại chunk faculty và đưa đoạn undergraduate vào top-3. |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**

> Có. Với SentenceChunker và embedding local, câu 5 không lọc đưa `faculty-staff-non-degree-registration#12` vào top-3 và thiếu dữ kiện ID Card; khi lọc `audience=student`, chunk faculty bị loại, `registration-start-times#1` vào top-3 và nội dung trả lời đủ. Đây là A/B hợp lệ vì top-3 và kết quả nội dung thay đổi.

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**

- Corpus có 9 tài liệu chính thức về đăng ký học phần, gồm 6 tài liệu `student`, 1 `faculty`, 1 `staff` và 1 `all`; metadata cho phép lọc theo đối tượng trước khi xếp hạng.
- Với `course-registration.md` ở baseline `chunk_size=200`, SentenceChunker tạo 10 chunk, FixedSizeChunker 20 và RecursiveChunker 26. Sentence giữ nguyên câu nhưng không bảo đảm giữ trọn quy trình: đáp án câu 1 nằm ở ba chunk `#5–#7`.
- Benchmark CP6 dùng backend local đa ngữ trên 75 chunk của SentenceChunker; kiểm tra theo `doc_id` cho 5/5 câu nhưng kiểm tra theo chuỗi đáp án chỉ cho 2/5 câu, 4/10 điểm retrieval tạm. A/B câu 5 cho thấy metadata `audience=student` có tác động thực tế.

**Bài học rút ra khi so sánh trong nhóm:**

> Cùng một tài liệu, ranh giới chunk quyết định agent nhìn thấy cả quy trình hay chỉ một bước. SentenceChunker giữ câu nhưng có chunk dài tới 1.148 ký tự; Recursive giới hạn dưới 500 ký tự và đạt 3/5 câu có đủ dữ kiện trong top-3. Việc kiểm `doc_id` riêng lẻ sẽ thổi phồng kết quả, vì câu 3 có cả top-3 cùng `course-changes` nhưng vẫn thiếu bước S3 và 24 giờ.

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**

> Nhóm sẽ cố định một phiên bản corpus cho mọi thành viên, giữ cấu trúc Markdown heading nếu cần thử chiến lược theo mục, và lưu log gồm cấu hình embedding, chunk ID cùng top-3 của cả năm câu. Sau đó chạy lại bằng cùng một mô hình embedding có hỗ trợ tiếng Việt–Anh, thử cả lượt có/không lọc `audience=student`, và kiểm tra câu trả lời agent với đáp án chuẩn. Với các quy trình nhiều bước, nhóm sẽ thử kích thước hoặc độ chồng lấp câu để giảm việc đáp án nằm rải trên nhiều chunk.

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí                                 | Điểm tự đánh giá                                                                            |
| ---------------------------------------- | ------------------------------------------------------------------------------------------- |
| Lựa chọn tài liệu (Document Set Quality) | 10/ 10; đã có 9 tài liệu và metadata, còn thiếu bằng chứng câu hỏi cần lọc để trả lời đúng. |
| Thiết kế chiến lược (Strategy Design)    | 14/ 15; đã ghi đủ ba chiến lược, nhưng còn thiếu hai log chạy để so sánh công bằng.         |
| Chất lượng truy xuất (Retrieval Quality) | 4/10 retrieval tạm cho Sentence; chưa có câu trả lời agent để chấm đủ rubric / 10.          |
| Thuyết trình (Demo)                      | 2 / 5; chưa có thông tin buổi demo.                                                         |
| **Tổng phần nhóm**                       | **30 / 40**                                                                                 |
