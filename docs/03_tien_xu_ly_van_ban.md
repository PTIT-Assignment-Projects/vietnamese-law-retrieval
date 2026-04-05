# 3. Quy trình tiền xử lý văn bản (Text Preprocessing)

## 3.1. Tổng quan

Tiền xử lý văn bản tiếng Việt là bước quan trọng đầu tiên, biến đổi văn bản thô thành dạng tokenized, sạch, sẵn sàng cho việc lập chỉ mục và truy xuất.

**File thực hiện:** `src/preprocessing/text_processor.py` (class `TextProcessor`)

## 3.2. Pipeline tiền xử lý

Pipeline gồm 5 bước tuần tự:

```
Raw Text
    │
    ├── Bước 1: text_normalize()         ──> Chuẩn hóa Unicode tiếng Việt
    │
    ├── Bước 2: lower()                  ──> Chuyển về chữ thường
    │
    ├── Bước 3: Replace \ufffd           ──> Xóa ký tự lỗi encoding
    │
    ├── Bước 4: word_tokenize()          ──> Tách từ tiếng Việt (underthesea)
    │
    ├── Bước 5: Regex filter             ──> Chỉ giữ token hợp lệ
    │
    ├── Bước 6: Stopword removal         ──> Loại bỏ từ dừng
    │
    └── Bước 7: Length filter            ──> Loại bỏ token 1 ký tự
    
    ──> List[str] (cleaned tokens)
```

## 3.3. Chi tiết từng bước

### Bước 1: Chuẩn hóa Unicode (`text_normalize`)

Sử dụng hàm `underthesea.text_normalize()` để chuẩn hóa các ký tự Unicode tiếng Việt:
- Chuẩn hóa các dấu thanh (sắc, huyền, hỏi, ngã, nặng)
- Chuẩn hóa các ký tự đặc biệt (ươ, ươ, ứ, ừ, ử, ữ, ự...)
- Xử lý các trường hợp encoding sai

```python
words = text_normalize(text)
```

### Bước 2: Chuyển chữ thường (`lower`)

```python
words = words.lower()
```

Toàn bộ văn bản được chuyển về lowercase để đảm bảo tính nhất quán khi so sánh.

### Bước 3: Xóa ký tự lỗi

```python
text = words.replace("\ufffd", " ")
```

Ký tự `\ufffd` (Unicode replacement character) xuất hiện khi encoding lỗi, được thay thế bằng khoảng trắng.

### Bước 4: Tách từ tiếng Việt (`word_tokenize`)

Sử dụng thư viện `underthesea` với các tham số:
- `format="text"`: Trả về chuỗi các từ cách nhau bởi khoảng trắng
- `use_token_normalize=True`: Chuẩn hóa token khi tách

```python
tokens = word_tokenize(text, format="text", use_token_normalize=True).split()
```

**Ví dụ:**
```
Input:  "Thông tư này hướng dẫn tuần tra"
Output: ["Thông_tư", "này", "hướng_dẫn", "tuần_tra"]
```

Từ ghép tiếng Việt được nối bằng dấu `_` (underthesea convention).

### Bước 5: Lọc token bằng Regex

Chỉ giữ lại các token khớp với pattern:

```python
_valid_token_pattern = re.compile(r"^[a-z0-9_\u00E0-\u01FF\u1EA0-\u1EFF.-]+$")
```

**Pattern giải thích:**
- `a-z`: Chữ cái Latin thường
- `0-9`: Chữ số
- `_`: Dấu gạch dưới (cho từ ghép)
- `\u00E0-\u01FF`: Ký tự Latin có dấu (Latin-1 Supplement + Latin Extended-A)
- `\u1EA0-\u1EFF`: Ký tự tiếng Việt đặc biệt (Latin Extended Additional)
- `.`: Dấu chấm (cho số thập phân, viết tắt)
- `-`: Dấu gạch ngang

Loại bỏ: dấu câu, ký tự đặc biệt, emoji, ký tự lỗi encoding.

### Bước 6: Loại bỏ stopwords

Danh sách **1,941 từ dừng tiếng Việt** được đọc từ file `util_file/vietnamese-stopwords.txt`.

```python
if t not in self.stopwords and len(t) > 1:
    cleaned_tokens.append(t)
```

**Một số stopwords ví dụ:**
```
a lô, ai, anh, ba, bao giờ, bao lâu, bởi, cả, cá nhân, cần, có, 
của, đang, đây, đó, đã,được,đều,để, em, gặp, hay, họ, ...
```

**Lưu ý quan trọng:** Stopwords được xử lý đặc biệt:
```python
# Trong load_vietnamese_stopwords():
line.strip().replace(" ", "_").lower()
# → "bao giờ" becomes "bao_giờ" để match với token từ underthesea
```

### Bước 7: Lọc token ngắn

```python
len(t) > 1
```

Loại bỏ các token chỉ có 1 ký tự (thường là noise hoặc không có ý nghĩa).

## 3.4. Kết quả tiền xử lý

### Lưu trữ

Kết quả được lưu thành 2 dictionary (pickle):

| File | Key | Value | Kích thước |
|------|-----|-------|-----------|
| `raw_corpus.pkl` | cid (int) | raw_text (str) | ~49 MB |
| `processed_corpus.pkl` | cid (int) | tokens (List[str]) | ~40 MB |

### Ví dụ kết quả

```
Raw:     "Thông tư này hướng dẫn tuần tra, canh gác bảo vệ đê Điều 
          trong mùa lũ đối với các tuyến đê sông được phân loại..."

Tokens:  ["thông_tư", "hướng_dẫn", "tuần_tra", "canh_gác", "bảo_vệ", 
          "đê", "điều", "mùa", "lũ", "tuyến", "đê", "sông", "phân_loại", 
          "phân_cấp", "quy_định", "điều", "luật", "đê_điều"]
```

## 3.5. Xử lý truy vấn (Query Processing)

Truy vấn được xử lý **tương tự** như văn bản trong corpus:

```python
# Trong SearchEngine.search():
query_terms = self.processor.process_text(query)
```

Pipeline giống hệt: normalize -> lowercase -> tokenize -> filter -> remove stopwords.

## 3.6. Xử lý đặc biệt cho Elasticsearch

Đối với Elasticsearch processed index, tokens được nối lại thành chuỗi:

```python
def process_text_join_for_es(self, text: str) -> str:
    return " ".join(self._clean_tokens(text))
```

```
Input:  "quy định về thuế"
Output: "quy_định thuế"  (chuỗi, không phải list)
```
