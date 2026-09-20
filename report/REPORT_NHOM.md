# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** [Tên nhóm]
**Thành viên:** [Họ tên từng thành viên]
**Ngày:** [Ngày nộp]

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Chủ đề (Domain) & Lý Do Chọn

**Chủ đề:** Chính sách hậu mãi và quy định mua hàng của HACOM

**Tại sao nhóm chọn chủ đề này?**
> Nhóm chọn một nhà bán lẻ cụ thể để các điều khoản về bảo hành, đổi/trả, nhập lại và giao hàng có cùng ngữ cảnh, nguồn gốc rõ ràng. Corpus ưu tiên các chính sách công khai chính thức của HACOM và được làm sạch thủ công, chỉ giữ quy định, điều kiện, thời hạn và mức phí phục vụ truy xuất.
>
> Crawler mẫu đã kiểm tra `robots.txt` nhưng bị từ chối cho User-Agent của crawler; vì vậy nhóm không dùng nội dung crawl tự động. Các file là bản tóm lược thủ công từ trang công khai, có lưu URL nguồn và ngày lấy để kiểm chứng.

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|------------|--------------------|----------|-----------------|
| 1 | Chính sách bảo hành và đổi trả đặc biệt HACOM | https://hacom.vn/chinh-sach-bao-hanh-chi-tiet | 2026-09-20 / not-stated | 1,338 | `doc_id`, `audience=buyer`, `category=warranty-return-policy`, `language=vi` |
| 2 | Quy trình và điều kiện bảo hành HACOM | https://hacom.vn/chinh-sach-bao-hanh | 2026-09-20 / not-stated | 1,262 | `doc_id`, `audience=buyer`, `category=warranty-policy`, `language=vi` |
| 3 | Chính sách nhập lại hàng tính phí HACOM | https://hacom.vn/chinh-sach-nhap-lai-tinh-phi | 2026-09-20 / not-stated | 1,116 | `doc_id`, `audience=buyer`, `category=return-buyback-policy`, `language=vi` |
| 4 | Chính sách giao hàng HACOM | https://hacom.vn/chinh-sach-giao-hang | 2026-09-20 / not-stated | 1,037 | `doc_id`, `audience=buyer`, `category=delivery-policy`, `language=vi` |
| 5 | Chính sách và quy định chung HACOM | https://hacom.vn/chinh-sach-quy-dinh-chung | 2026-09-20 / not-stated | 912 | `doc_id`, `audience=both`, `category=website-terms`, `language=vi` |

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [x] Tập tài liệu chỉ có nguồn công khai, không có dữ liệu đăng nhập, dữ liệu cá nhân hay tài liệu nội bộ. Nội dung menu/footer và liên hệ không liên quan đã bị loại bỏ.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (`not-stated` vì nguồn không nêu phiên bản) trong metadata; `sources.csv` khớp một-một với 5 file.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|----------------|------|---------------|-------------------------------|
| `doc_id` | string | `hacom-paid-buyback` | Định danh ổn định, đối chiếu chính xác với file và `sources.csv`. |
| `title` | string | `Chính sách nhập lại hàng tính phí HACOM` | Hiển thị nguồn và ngữ cảnh của kết quả truy xuất. |
| `source_url` | URL | `https://hacom.vn/chinh-sach-nhap-lai-tinh-phi` | Kiểm chứng điều khoản từ trang gốc. |
| `retrieved_at` | date | `2026-09-20` | Biết thời điểm dữ liệu được lấy vì chính sách có thể thay đổi. |
| `document_version` | string | `not-stated` | Không bịa số phiên bản khi nguồn không công bố. |
| `audience` | enum | `buyer`, `both` | Cho phép lọc riêng chính sách hậu mãi của người mua. |
| `category` | string | `delivery-policy` | Thu hẹp truy xuất theo loại chính sách. |
| `language` | string | `vi` | Hỗ trợ lọc hoặc chọn embedding phù hợp tiếng Việt. |

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

### Chiến lược của từng thành viên

> Mỗi thành viên điền một khối dưới đây (copy thêm nếu nhóm có nhiều hơn 3 người).

**Thành viên 1 — [Tên]**
- **Loại chiến lược:** [FixedSize / Sentence / Recursive / custom]
- **Mô tả & lý do chọn cho chủ đề này:** *(2-3 câu)*
- **Code snippet (nếu custom):**
```python
# Dán mã nguồn (implementation) vào đây
```

**Thành viên 2 — [Tên]**
- **Loại chiến lược:**
- **Mô tả & lý do chọn:**
- **Code snippet (nếu custom):**

**Thành viên 3 — [Tên]**
- **Loại chiến lược:**
- **Mô tả & lý do chọn:**
- **Code snippet (nếu custom):**

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
| 1 | | | |
| 2 | | | |
| 3 | | | |
| 4 | | | |
| 5 | | | |

### Tổng hợp chất lượng truy xuất của nhóm

> Cách chấm (theo `docs/SCORING.md`): **2 điểm/câu** — top-3 chứa chunk liên quan + agent trả lời đúng (2), có liên quan nhưng thiếu/không ở top-1 (1), không có trong top-3 (0).

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
|---|---------|-------------------------------|-------------------------------|---------|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |
| 4 | | | | |
| 5 | | | | |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> *Viết 2-3 câu:*

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
