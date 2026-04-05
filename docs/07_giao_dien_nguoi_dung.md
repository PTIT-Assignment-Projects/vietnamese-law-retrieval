# 7. Giao diện người dùng (Streamlit Web App)

## 7.1. Tổng quan

Giao diện web được xây dựng bằng **Streamlit**, cho phép người dùng tương tác với hệ thống truy xuất thông qua trình duyệt.

**File:** `src/app.py`  
**Chạy:** `streamlit run src/app.py`

## 7.2. Tính năng

### 7.2.1. Chọn phương pháp truy xuất

Sidebar cho phép chọn 1 trong 5 phương pháp:
- Boolean
- Vector Space Model (VSM)
- BM25 (mặc định)
- Elasticsearch (Normal)
- Elasticsearch (Processed)

### 7.2.2. Cấu hình

- **Top N Results**: Số lượng kết quả trả về (1-100, mặc định 10)

### 7.2.3. Nhập truy vấn

- Text input cho phép nhập câu hỏi bằng tiếng Việt
- Nút "Search" để kích hoạt tìm kiếm

### 7.2.4. Hiển thị kết quả

Mỗi kết quả hiển thị:
- **Rank**: Thứ tự (#1, #2, ...)
- **Document ID**: ID của văn bản trong corpus
- **Score**: Điểm số (hoặc "N/A (Match)" cho Boolean)
- **Nội dung**: Văn bản gốc đầy đủ

## 7.3. Kiến trúc giao diện

```
┌─────────────────────────────────────────────────────────┐
│  ⚖️ Vietnamese Law Retrieval                             │
│  Search for legal documents using various retrieval methods│
├──────────────┬────────────────────────────────────────────┤
│  Sidebar     │  Main Area                                │
│              │                                           │
│  Method:     │  [Enter your search query...]             │
│  [BM25 ▼]   │  [Search]                                 │
│              │                                           │
│  Top N: 10   │  ┌─ Result Card ───────────────────────┐ │
│              │  │ Rank #1 | ID: 12345    Score: 12.34 │ │
│              │  │ Nội dung văn bản pháp luật...       │ │
│              │  └─────────────────────────────────────┘ │
│              │  ┌─ Result Card ───────────────────────┐ │
│              │  │ Rank #2 | ID: 67890    Score: 10.21 │ │
│              │  │ Nội dung văn bản pháp luật...       │ │
│              │  └─────────────────────────────────────┘ │
└──────────────┴────────────────────────────────────────────┘
```

## 7.4. Caching

Sử dụng `@st.cache_resource` để cache search engine và ES engine:
- Tránh load lại models mỗi lần người dùng tương tác
- Tăng tốc độ phản hồi

```python
@st.cache_resource
def get_engines():
    search_engine = SearchEngine()
    search_engine.load_prebuilt_index()
    es_engine = ElasticSearchIndexing()
    return search_engine, es_engine
```

## 7.5. Style CSS

Giao diện sử dụng custom CSS:
- **Result card**: Nền trắng, border-left màu xanh, shadow nhẹ
- **Score badge**: Nền xanh nhạt, border-radius tròn
- **Button**: Full-width, nền xanh, chữ trắng
- **Doc ID**: Chữ xám, font nhỏ

## 7.6. Xử lý lỗi

- Nếu models chưa được build: Hiển thị warning
- Nếu ES không kết nối được: Hiển thị error
- Nếu query rỗng: Hiển thị warning
- Nếu không có kết quả: Hiển thị "No results found"
