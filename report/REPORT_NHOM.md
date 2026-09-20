# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** [Tên nhóm]
**Thành viên:** [Họ tên từng thành viên]
**Ngày:** [Ngày nộp]

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Chủ đề (Domain) & Lý Do Chọn

**Chủ đề:** Chính sách đổi trả, bảo hành và đồng kiểm trên các nền tảng thương mại điện tử

**Tại sao nhóm chọn chủ đề này?**
> Nhóm chọn các chính sách công khai về đổi trả, bảo hành và đồng kiểm của Shopee, Lazada, HACOM, Điện Máy Xanh và AVAKids. Những nguồn này có cùng miền bài toán nhưng khác đối tượng và điều kiện áp dụng, phù hợp để kiểm tra retrieval và hiệu quả của metadata.
>
> Corpus benchmark chọn 10 tài liệu trực tiếp liên quan từ `data/policies/`; `hacom-general-terms.md` được giữ ngoài corpus benchmark vì là điều khoản website chung, không phục vụ năm câu hỏi chính sách hậu mãi.

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|------------|--------------------|----------|-----------------|
| 1 | Đổi sản phẩm theo nhóm hàng AVAKids | https://www.avakids.com/bao-hanh-doi-tra | 2026-09-20 / not-stated | 3,580 | `audience=buyer`, `platform=AVAKids`, `category=exchange-policy` |
| 2 | Quy định đổi trả Sàn TMĐT Điện Máy Xanh | https://www.dienmayxanh.com/quy-che-san-dien-may-xanh | 2026-09-20 / not-stated | 3,939 | `audience=both`, `platform=Điện Máy Xanh`, `category=return-policy` |
| 3 | Đổi sản phẩm tại TGDĐ/Điện Máy Xanh | https://www.dienmayxanh.com/chinh-sach-bao-hanh-san-pham | 2026-09-20 / 2023-09-01 | 4,054 | `audience=buyer`, `platform=TGDĐ/Điện Máy Xanh`, `category=exchange-policy` |
| 4 | Quy trình và điều kiện bảo hành HACOM | https://hacom.vn/chinh-sach-bao-hanh | 2026-09-20 / not-stated | 1,606 | `audience=buyer`, `platform=hacom`, `category=warranty-policy` |
| 5 | Bảo hành và đổi trả đặc biệt HACOM | https://hacom.vn/chinh-sach-bao-hanh-chi-tiet | 2026-09-20 / not-stated | 1,705 | `audience=buyer`, `platform=hacom`, `category=warranty-return-policy` |
| 6 | Đồng kiểm Lazada — chung | URL Lazada trong `sources.csv` | 2026-09-20 / not-stated | 1,864 | `audience=both`, `platform=Lazada`, `category=joint-inspection-policy` |
| 7 | Đồng kiểm Lazada — người mua | URL Lazada trong `sources.csv` | 2026-09-20 / not-stated | 2,644 | `audience=buyer`, `platform=Lazada`, `category=joint-inspection-policy` |
| 8 | Đồng kiểm Lazada — Nhà Bán Hàng | URL Lazada trong `sources.csv` | 2026-09-20 / not-stated | 2,684 | `audience=seller`, `platform=Lazada`, `category=joint-inspection-policy` |
| 9 | Đổi trả và hoàn tiền Shopee | https://banhang.shopee.vn/edu/article/563 | 2026-09-20 / not-stated | 9,939 | `audience=both`, `platform=Shopee`, `category=returns-policy` |
| 10 | Bảo hành sản phẩm mua tại Shopee | URL Shopee trong `sources.csv` | 2026-09-20 / not-stated | 4,647 | `audience=buyer`, `platform=Shopee`, `category=warranty-policy` |

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [x] Tập tài liệu benchmark có 10 nguồn công khai, không có dữ liệu đăng nhập, dữ liệu cá nhân hay tài liệu nội bộ. Nội dung menu/footer và chỉ dẫn template không liên quan đã bị loại bỏ.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` trong metadata; `data/policies/sources.csv` khớp một-một với 10 file được bench chọn.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|----------------|------|---------------|-------------------------------|
| `doc_id` | string | `lazada-joint-inspection-seller` | Định danh ổn định, đối chiếu chính xác với file và `sources.csv`. |
| `title` | string | `Chính sách đồng kiểm Lazada cho Nhà Bán Hàng` | Hiển thị nguồn và ngữ cảnh của kết quả truy xuất. |
| `source_url` | URL | URL chính sách Lazada trong `sources.csv` | Kiểm chứng điều khoản từ trang gốc. |
| `retrieved_at` | date | `2026-09-20` | Biết thời điểm dữ liệu được lấy vì chính sách có thể thay đổi. |
| `document_version` | string | `not-stated` | Không bịa số phiên bản khi nguồn không công bố. |
| `audience` | enum | `buyer`, `seller`, `both` | Cho phép lọc riêng chính sách cho người mua hoặc Nhà Bán Hàng. |
| `category` | string | `joint-inspection-policy` | Thu hẹp truy xuất theo loại chính sách. |
| `platform` | string | `Lazada` | Giữ các câu hỏi nền tảng cụ thể không lẫn với nguồn khác. |
| `language` | string | `vi` | Hỗ trợ lọc hoặc chọn embedding phù hợp tiếng Việt. |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

> Mỗi thành viên thử **một chiến lược khác nhau** trên cùng bộ tài liệu; nhóm tổng hợp và so sánh ở đây.

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare()` trên 2-3 tài liệu:

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|-----------|----------|-------------|------------|-------------------|
| `shopee-return-refund-policy` | FixedSizeChunker (`fixed_size`) | 9 | 837.8 | Có overlap nhưng đôi khi cắt giữa ý. |
| `shopee-return-refund-policy` | SentenceChunker (`by_sentences`) | 12 | 592.7 | Giữ trọn câu; số chunk nhiều hơn. |
| `shopee-return-refund-policy` | RecursiveChunker (`recursive`) | 10 | 712.3 | Giữ ranh giới đoạn/câu tốt hơn fixed-size. |
| `lazada-joint-inspection-seller` | FixedSizeChunker (`fixed_size`) | 3 | 622.3 | Đủ dùng, nhưng ranh giới FAQ có thể bị cắt. |
| `lazada-joint-inspection-seller` | SentenceChunker (`by_sentences`) | 5 | 351.2 | Câu FAQ mạch lạc, nhưng có chunk ngắn. |
| `lazada-joint-inspection-seller` | RecursiveChunker (`recursive`) | 3 | 587.7 | Giữ được các mục FAQ gần trọn vẹn. |
| `dmx-marketplace-return-rules` | FixedSizeChunker (`fixed_size`) | 4 | 721.8 | Có overlap nhưng không nhận biết mục chính sách. |
| `dmx-marketplace-return-rules` | SentenceChunker (`by_sentences`) | 7 | 388.9 | Dễ đọc nhưng phân mảnh hơn. |
| `dmx-marketplace-return-rules` | RecursiveChunker (`recursive`) | 4 | 682.8 | Cân bằng độ dài và mạch lạc theo đoạn. |

### Chiến lược của từng thành viên

> Mỗi thành viên điền một khối dưới đây (copy thêm nếu nhóm có nhiều hơn 3 người).

**Thành viên 1 — [Tên]**
- **Loại chiến lược:** FixedSizeChunker (điền tên thành viên khi nhóm phân công)
- **Mô tả & lý do chọn cho chủ đề này:** Dùng chunk kích thước cố định có overlap làm đường cơ sở. Chiến lược này đơn giản, giữ được một phần ngữ cảnh ở ranh giới nhưng không nhận biết cấu trúc mục của chính sách.
- **Code snippet (nếu custom):**
```python
# Dán mã nguồn (implementation) vào đây
```

**Thành viên 2 — [Tên]**
- **Loại chiến lược:** RecursiveChunker
- **Mô tả & lý do chọn:** Ưu tiên ranh giới đoạn, câu và từ để hạn chế cắt giữa ý. Đây là đối chứng với fixed-size khi chính sách có đoạn văn hoặc FAQ dài không đều.
- **Code snippet (nếu custom):**

**Thành viên 3 — [Tên]**
- **Loại chiến lược:** HeadingChunker (custom)
- **Mô tả & lý do chọn:** Mỗi heading Markdown là một điều khoản/FAQ có ngữ nghĩa trọn vẹn, nên chunker tách theo heading trước. Khi mục quá dài, nó dùng RecursiveChunker và gắn lại heading vào từng mảnh để không mất chủ đề.
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
| 1 | Shopee: thời hạn gửi yêu cầu Trả hàng/Hoàn tiền và thời hạn gửi lại hàng sau khi chấp nhận là bao lâu? | 15 ngày từ khi giao thành công; sau khi chấp nhận, gửi lại hàng cho người bán trong 6 ngày. | `shopee-return-refund-policy` |
| 2 | Lazada: NBH có phải trả thêm phí đồng kiểm và liên hệ ai khi hàng hoàn bị thiếu/hư hỏng? | NBH không trả thêm chi phí; liên hệ Bộ Phận Hỗ trợ NBH PSC. | `lazada-joint-inspection-seller` — bắt buộc filter `audience=seller`, `platform=Lazada` |
| 3 | HACOM: đổi mới 100% lỗi nhà sản xuất trong bao nhiêu ngày và bảo hành tận nơi áp dụng cho ai? | 15 ngày đầu; khách doanh nghiệp có Thẻ bảo hành vàng, cách chi nhánh gần nhất dưới 20 km. | `hacom-warranty-process` |
| 4 | Điện Máy Xanh: thời hạn yêu cầu trả hàng và bằng chứng khi không đồng kiểm tại chỗ là gì? | 15 ngày từ khi giao thành công; video mở gói rõ ràng, không cắt ghép, thể hiện trước/sau mở. | `dmx-marketplace-return-rules` |
| 5 | AVAKids: đồ chơi lỗi kỹ thuật đổi trả bao lâu và có bảo hành không? | Đổi một-một trong 30 ngày; đồ chơi chỉ đổi trả, không bảo hành. | `avakids-exchange-policy` |

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
> Có. Câu 2 dùng `metadata_filter={"audience": "seller", "platform": "Lazada"}` trước khi xếp hạng, nên chỉ giữ các chunk FAQ dành cho Nhà Bán Hàng Lazada. Không lọc, các chunk đồng kiểm dành cho người mua hoặc nội dung đổi trả của nền tảng khác có thể chiếm top-k vì có từ vựng giống nhau.

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
