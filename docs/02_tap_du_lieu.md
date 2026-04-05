# 2. Phân tích tập dữ liệu

## 2.1. Nguồn dữ liệu

Bộ dữ liệu gồm các văn bản pháp luật tiếng Việt (luật, nghị định, thông tư, nghị quyết...) với các câu hỏi và văn bản liên quan được gán nhãn.

## 2.2. Cấu trúc dữ liệu

### 2.2.1. Bảng Corpus (`corpus.csv`)

| Cột | Kiểu | Mô tả |
|-----|------|-------|
| `cid` | int | ID duy nhất của văn bản trong corpus |
| `text` | string | Nội dung đầy đủ của đoạn/điều luật |

**Thống kê:**
- Tổng số văn bản: **222,981** documents
- Kích thước file: ~49 MB
- Mỗi document là một đoạn văn bản pháp luật (có thể là một điều, khoản, điểm)

**Ví dụ dữ liệu:**
```
cid=0: "Thông tư này hướng dẫn tuần tra, canh gác bảo vệ đê Điều trong mùa lũ 
       đối với các tuyến đê sông được phân loại, phân cấp theo quy định tại 
       Điều 4 của Luật Đê Điều."
```

### 2.2.2. Bảng Train (`train.csv`)

| Cột | Kiểu | Mô tả |
|-----|------|-------|
| `qid` | int | ID duy nhất của câu hỏi |
| `question` | string | Câu hỏi bằng tiếng Việt |
| `cid` | string (list) | Danh sách ID các văn bản liên quan (ground truth) |
| `context_list` | string (list) | Nội dung các đoạn văn bản liên quan |

**Thống kê:**
- Tổng số câu hỏi: **9,541** queries
- Kích thước file: ~22 MB

### 2.2.3. Bảng Test (`test.csv`)

- Cùng cấu trúc với train.csv
- Tổng số câu hỏi: **3,184** queries
- Kích thước file: ~7.3 MB

### 2.2.4. Bảng Merged (`train_test_merged.csv`)

- Gộp train + test để đánh giá
- Tổng số câu hỏi: **12,725** queries
- Kích thước file: ~29 MB

## 2.3. Đặc điểm dữ liệu

### 2.3.1. Ngôn ngữ và nội dung
- Toàn bộ dữ liệu bằng **tiếng Việt**
- Nội dung thuộc nhiều lĩnh vực: đê điều, lương thưởng, thanh tra, cứu hỏa, viễn thông, ngân hàng, bảo vệ môi trường, hải quan, thuế, đất đai...
- Văn bản có cấu trúc pháp lý (điều, khoản, điểm) với các con số, ký hiệu văn bản

### 2.3.2. Đặc điểm văn bản
- Văn bản chứa ký tự Unicode tiếng Việt đầy đủ (có dấu thanh)
- Có các ký tự đặc biệt: số, ký hiệu văn bản (Nghị định số 204/2004/NĐ-CP), dấu câu
- Một số văn bản có ký tự lỗi (`\ufffd`) cần được xử lý

### 2.3.3. Đặc điểm câu hỏi
- Câu hỏi tự nhiên bằng tiếng Việt
- Ví dụ: "So sánh mức lương của khuyến nông viên chính và khuyến nông viên?"
- Ví dụ: "Việc đăng ký hạn mức nhận ủy thác của tổ chức nhận ủy thác là ngân hàng thương mại được thực hiện tại đâu?"

## 2.4. Quan hệ giữa Corpus và Queries

```
Query (question)
    │
    ├── qid: 19651
    │   └── cid: [1536]  ──> corpus.csv, cid=1536
    │
    ├── qid: 44619
    │   └── cid: [17986] ──> corpus.csv, cid=17986
    │
    ├── qid: 73069
    │   └── cid: [4637]  ──> corpus.csv, cid=4637
    │
    └── qid: 69349
        └── cid: [3159]  ──> corpus.csv, cid=3159
```

Mỗi query có 1 hoặc nhiều `cid` là ground truth - những văn bản được coi là liên quan đến câu hỏi.

## 2.5. Tỷ lệ chia dữ liệu

| Tập | Số lượng queries | Tỷ lệ |
|-----|-----------------|-------|
| Train | 9,541 | 75% |
| Test | 3,184 | 25% |
| **Tổng** | **12,725** | **100%** |

## 2.6. Thách thức của dữ liệu

1. **Văn bản dài**: Nhiều văn bản pháp luật rất dài, chứa nhiều điều khoản
2. **Ngôn ngữ pháp lý**: Sử dụng từ ngữ chuyên ngành, cấu trúc phức tạp
3. **Ký tự đặc biệt**: Số, ký hiệu văn bản, mã điều luật
4. **Tiếng Việt có dấu**: Cần xử lý Unicode đúng cách
5. **Tỷ lệ positive sample thấp**: Trong 222K documents, mỗi query chỉ có 1 hoặc vài documents liên quan
