# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** Akatsuki
**Thành viên:**
- Vũ Đình Đăng — 2A202602946
- Nguyễn Chí Công — 2A202602634
- Hoàng Trung Anh — 2A202602521
**Ngày:** 2026-09-19

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Chủ đề (Domain) & Lý Do Chọn

**Chủ đề:** Dịch vụ và quy định đăng ký học phần đại học

**Tại sao nhóm chọn chủ đề này?**
> *Viết 2-3 câu:*

> Bản nháp dữ liệu đã chuẩn bị: nhóm sử dụng các hướng dẫn công khai của
> University Registrar (CMU) về đăng ký học phần, lịch đăng ký và thay đổi học
> phần. Chủ đề có các quy định rõ ràng, truy vết được nguồn và phù hợp để thử
> metadata `audience`.

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|------------|--------------------|----------|-----------------|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |
| 5 | | | | | |

Corpus hiện có **9 tài liệu** tại `data/university_services/`; danh mục nguồn,
ngày lấy và quyền sử dụng nằm trong `data/university_services/sources.csv`.

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [ ] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [ ] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|----------------|------|---------------|-------------------------------|
| | | | |
| | | | |

Metadata đang dùng: `doc_id`, `title`, `source_url`, `retrieved_at`,
`document_version`, `audience`, `department`, `category`, `language`.
`audience` hỗ trợ tách nội dung student/faculty/staff; `category` hỗ trợ giới
hạn truy xuất theo đăng ký học phần hoặc thay đổi học phần.

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

> Mỗi thành viên thử **một chiến lược khác nhau** trên cùng bộ tài liệu; nhóm tổng hợp và so sánh ở đây.

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare()` trên 2-3 tài liệu:

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|-----------|----------|-------------|------------|-------------------|
| | FixedSizeChunker (`fixed_size`) | | | |
| | SentenceChunker (`by_sentences`) | | | |
| | RecursiveChunker (`recursive`) | | | |

Kết quả baseline với `chunk_size=900`:

| Tài liệu | Fixed (count/avg) | Sentence (count/avg) | Recursive (count/avg) |
|---|---:|---:|---:|
| `course-registration.md` | 5 / 813.0 | 10 / 384.0 | 5 / 771.4 |
| `course-changes.md` | 9 / 826.9 | 19 / 366.2 | 9 / 779.9 |
| `registration-four-steps.md` | 6 / 824.2 | 8 / 584.8 | 6 / 780.8 |

Chiến lược bổ sung đã thử: `scripts/evaluate_benchmarks.py` chia theo heading
Markdown trước, rồi dùng `RecursiveChunker` cho section dài; lần chạy hiện tại
tạo 42 chunks có thể truy vết theo `source_file` và `chunk_index`.

### Chiến lược của từng thành viên

> Mỗi thành viên điền một khối dưới đây (copy thêm nếu nhóm có nhiều hơn 3 người).

**Thành viên 1 — Vũ Đình Đăng (2A202602946)**
- **Loại chiến lược:** Heading-aware + `RecursiveChunker(chunk_size=900)`
- **Mô tả & lý do chọn:** Tách theo heading giữ các bước/quy định trong cùng mục Markdown; section quá dài được tách tiếp theo paragraph/câu.
- **Code:** `scripts/evaluate_benchmarks.py:chunk_by_heading`.

**Thành viên 2 — Nguyễn Chí Công (2A202602634)**
- **Loại chiến lược:** [Cần xác nhận chiến lược đã chạy]
- **Mô tả & lý do chọn:** [Cần bổ sung kết quả thực nghiệm cá nhân]

**Thành viên 3 — Hoàng Trung Anh (2A202602521)**
- **Loại chiến lược:** [Cần xác nhận chiến lược đã chạy]
- **Mô tả & lý do chọn:** [Cần bổ sung kết quả thực nghiệm cá nhân]

### So Sánh Giữa Các Thành Viên

| Thành viên | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| | | | | |
| | | | | |
| | | | | |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> *Viết 2-3 câu — đây là phần được đánh giá cao nhất (khả năng suy nghĩ & giải thích):*

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

> **Đúng 5 câu hỏi**, đa dạng, có thể kiểm chứng; **ít nhất 1 câu** cần lọc metadata mới trả lời tốt. Đây là bộ câu hỏi chung cho mọi thành viên chạy.

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|--------------------------|
| 1 | How many units make an undergraduate student full time? | 36 or more units. | `course-registration` |
| 2 | What must a student do to request a course-time conflict? | Submit in SIO; advisor/instructors approve; accept conditions. | `course-registration` |
| 3 | What happens on the transcript after a course withdrawal? | A W grade appears. | `course-changes` |
| 4 | How are undergraduate registration start times assigned? | Last three ID-card digits; four rotating time blocks. | `registration-start-times` |
| 5 | When must a non-degree staff member submit a petition, and can they receive drop vouchers? | By first day of classes; no Drop Vouchers. | `staff-non-degree-registration` |

Bộ benchmark được định nghĩa có thể chạy lại trong
`scripts/evaluate_benchmarks.py`:

| # | Câu hỏi | Gold answer | Nguồn |
|---|---|---|---|
| 1 | How many units make an undergraduate student full time? | 36 or more units. | `course-registration` |
| 2 | What must a student do to request a course-time conflict? | Submit the request in SIO; advisor and instructors approve; student accepts conditions. | `course-registration` |
| 3 | What happens on the transcript after a course withdrawal? | A W grade appears. | `course-changes` |
| 4 | How are undergraduate registration start times assigned? | Randomly from the last three ID-card digits, rotating through four blocks. | `registration-start-times` + `audience=student` |
| 5 | When must a non-degree staff member submit a petition, and can they receive drop vouchers? | By first day of classes; no Drop Vouchers. | `staff-non-degree-registration` |

### Tổng hợp chất lượng truy xuất của nhóm

> Cách chấm (theo `docs/SCORING.md`): **2 điểm/câu** — top-3 chứa chunk liên quan + agent trả lời đúng (2), có liên quan nhưng thiếu/không ở top-1 (1), không có trong top-3 (0).

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
|---|---------|-------------------------------|-------------------------------|---------|
| 1 | Full-time units | Heading-aware + Recursive + OpenAI | Có, top-1 | `course-registration`, score 0.5258 |
| 2 | Course-time conflict | Heading-aware + Recursive + OpenAI | Có, top-1 | `course-registration`, score 0.7587 |
| 3 | Withdrawal transcript | Heading-aware + Recursive + OpenAI | Có, top-1 | `course-changes`, score 0.6432 |
| 4 | Undergraduate start times | Heading-aware + Recursive + OpenAI | Có, top-1 | Filter `audience=student`; score 0.7868 |
| 5 | Staff petition and vouchers | Heading-aware + Recursive + OpenAI | Có, top-1 | `staff-non-degree-registration`, score 0.6542 |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> Có. Q4 dùng `metadata_filter={"audience": "student"}`, loại các tài liệu
> dành cho faculty/staff trước khi xếp hạng và trả về đúng `registration-start-times`
> ở top-1. Với corpus lớn hơn hoặc có nội dung giống nhau cho nhiều đối tượng,
> filter này sẽ giảm nhiễu rõ hơn.

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

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) | / 10 |
| Thiết kế chiến lược (Strategy Design) | / 15 |
| Chất lượng truy xuất (Retrieval Quality) | / 10 |
| Thuyết trình (Demo) | / 5 |
| **Tổng phần nhóm** | **/ 40** |
