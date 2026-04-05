# 5. Các phương pháp truy xuất (Retrieval Methods)

## 5.1. Tổng quan

Hệ thống triển khai **5 phương pháp truy xuất**, từ đơn giản (Boolean) đến nâng cao (BM25, Elasticsearch):

| # | Phương pháp | Loại | Có xếp hạng | File |
|---|------------|------|-------------|------|
| 1 | Boolean Retrieval | Set-based | Không | `src/model/boolean_retrieval.py` |
| 2 | Vector Space Model | Vector-based | Có (cosine sim) | `src/model/vector_space_model.py` |
| 3 | Okapi BM25 | Probabilistic | Có (BM25 score) | `src/model/bm25.py` |
| 4 | Elasticsearch Normal | Search engine | Có (BM25 built-in) | `src/indexing/elasticsearch_indexing.py` |
| 5 | Elasticsearch Processed | Search engine | Có (BM25 built-in) | `src/indexing/elasticsearch_indexing.py` |

## 5.2. Boolean Retrieval

### 5.2.1. Mô tả

Mô hình truy xuất Boolean sử dụng các toán tử logic (AND, OR, NOT) trên posting lists của inverted index. Không có xếp hạng - kết quả chỉ là "có" hoặc "không".

### 5.2.2. Cách hoạt động

```
Query parsing:
- Các từ trước toán tử → first_term (List[str])
- Các từ sau toán tử → second_term (List[str])
- Nếu không có toán tử → mặc định AND
```

### 5.2.3. Toán tử

**AND (giao):**
```
result = docs(first_term[0]) ∩ docs(first_term[1]) ∩ ... ∩ docs(second_term[0]) ∩ ...
```
Lấy giao của tất cả posting lists - tài liệu chứa TẤT CẢ các term.

**OR (hợp):**
```
result = docs(first_term[0]) ∪ docs(first_term[1]) ∪ ... ∪ docs(second_term[0]) ∪ ...
```
Lấy hợp của các posting lists - tài liệu chứa ÍT NHẤT MỘT term.

**NOT (phần bù):**
```
all_docs = set(doc_lengths.keys())
excluded = docs(first_term) ∪ docs(second_term)
result = all_docs - excluded
```
Loại bỏ các tài liệu chứa bất kỳ term nào.

### 5.2.4. Ví dụ

```
Input query: "quy định and thuế"
→ first_term = ["quy_định"], second_term = ["thuế"], operator = "and"
→ result = docs("quy_định") ∩ docs("thuế")
```

### 5.2.5. Đặc điểm

- **Ưu điểm**: Đơn giản, nhanh, kết quả chính xác (exact match)
- **Nhược điểm**: Không có xếp hạng, kết quả có thể rất nhiều hoặc rất ít, nhạy cảm với cách viết query

---

## 5.3. Vector Space Model (VSM)

### 5.3.1. Mô tả

Biểu diễn documents và query thành vector trong không gian nhiều chiều (mỗi chiều là một term). Đo độ tương đồng bằng cosine similarity.

### 5.3.2. Công thức TF-IDF

**Term Frequency (TF) - sublinear:**
```
tf(t, d) = 1 + log(f(t, d))    nếu f(t, d) > 0
tf(t, d) = 0                    nếu f(t, d) = 0
```

Trong đó `f(t, d)` là số lần term `t` xuất hiện trong document `d`.

**Inverse Document Frequency (IDF) - sklearn smoothing:**
```
idf(t) = log((N + 1) / (1 + df(t))) + 1
```

Trong đó:
- `N` = tổng số documents (222,981)
- `df(t)` = số documents chứa term `t`

**TF-IDF score:**
```
tfidf(t, d) = tf(t, d) × idf(t)
```

### 5.3.3. Cosine Similarity

```
                    Σ(q_tfidf × d_tfidf)
cos(q, d) = ─────────────────────────────────
             ||q|| × ||d||

Trong đó:
||q|| = sqrt(Σ q_tfidf²)
||d|| = sqrt(Σ d_tfidf²)
```

### 5.3.4. Thuật toán tìm kiếm

```
Algorithm: VSM Search
Input: query_terms: List[str], top_n: int
Output: List[Tuple[doc_id, score]]

1. candidates = ∅
2. For each term in query_terms:
   candidates = candidates ∪ get_docs_contain_term(term)
3. Compute query_vector (TF-IDF for each query term)
4. query_norm = sqrt(Σ tfidf²)
5. For each doc_id in candidates:
   a. dot_product = Σ(query_tfidf × doc_tfidf) for shared terms
   b. doc_norm = sqrt(Σ doc_tfidf² for all doc terms)
   c. similarity = dot_product / (query_norm × doc_norm)
   d. scores.append((doc_id, similarity))
6. Sort scores descending, return top_n
```

### 5.3.5. Đặc điểm

- **Ưu điểm**: Có xếp hạng kết quả, đơn giản, hiệu quả với corpus vừa phải
- **Nhược điểm**: Giả định độc lập giữa các term, không xử lý tốt synonym/polysemy, tính toán tốn kém với corpus lớn

---

## 5.4. Okapi BM25

### 5.4.1. Mô tả

BM25 là mô hình xác suất, cải tiến của VSM bằng cách引入 term frequency saturation và document length normalization.

### 5.4.2. Tham số

| Tham số | Giá trị | Ý nghĩa |
|---------|---------|---------|
| k1 | 1.5 | TF saturation: kiểm soát mức độ ảnh hưởng của TF |
| b | 0.75 | Length normalization: chuẩn hóa theo độ dài document |

### 5.4.3. Công thức

**IDF (BM25):**
```
idf(t) = log((N - df(t) + 0.5) / (df(t) + 0.5) + 1)
```

**BM25 score:**
```
                tf × (k1 + 1)
BM25(t, d) = idf(t) × ─────────────────────────────
              tf + k1 × (1 - b + b × (|d| / avgdl))

Trong đó:
- tf = tần suất term t trong document d
- |d| = độ dài document d (số tokens)
- avgdl = độ dài trung bình của tất cả documents
```

### 5.4.4. Giải thích công thức

1. **TF saturation**: Khi tf tăng, score tăng nhưng với tốc độ giảm dần (diminishing returns). Được kiểm soát bởi k1.
   - k1 = 0: TF không ảnh hưởng
   - k1 → ∞: TF ảnh hưởng tuyến tính

2. **Length normalization**: Chuẩn hóa theo độ dài document, được kiểm soát bởi b.
   - b = 0: Không chuẩn hóa theo độ dài
   - b = 1: Chuẩn hóa hoàn toàn theo độ dài

3. **IDF**: Term hiếm có IDF cao → đóng góp lớn hơn vào score.

### 5.4.5. Thuật toán tìm kiếm

```
Algorithm: BM25 Search
Input: query_terms: List[str], top_n: int
Output: List[Tuple[doc_id, score]]

1. candidates = ∅
2. For each term in query_terms:
   candidates = candidates ∪ get_docs_contain_term(term)
3. For each doc_id in candidates:
   score = 0
   For each term in query_terms:
      score += compute_bm25_score(term, doc_id)
   scores.append((doc_id, score))
4. Sort scores descending, return top_n
```

### 5.4.6. Đặc điểm

- **Ưu điểm**: Hiệu quả cao với text retrieval, xử lý tốt TF saturation và length normalization, là baseline mạnh cho IR
- **Nhược điểm**: Tham số k1, b cần tuning, không nắm bắt ngữ nghĩa

---

## 5.5. Elasticsearch Search

### 5.5.1. Normal Index Search

Sử dụng Elasticsearch standard analyzer trên văn bản gốc:

```python
# Query gửi tới ES:
query_es = {
    "query": {
        "match": {
            "content": "quy định về thuế"  # raw query
        }
    }
}
```

Elasticsearch tự động: tokenize -> lowercase -> remove stopwords -> BM25 scoring.

### 5.5.2. Processed Index Search

Query được tiền xử lý trước khi gửi tới ES:

```python
# Tiền xử lý query:
processed_query = self.processor.process_text_join_for_es(query)
# "quy định về thuế" → "quy_định thuế"

query_es = {
    "query": {
        "match": {
            "content": "quy_định thuế"  # processed query
        }
    }
}
```

### 5.5.3. So sánh 2 index

| Đặc điểm | Normal Index | Processed Index |
|-----------|-------------|-----------------|
| Input data | Raw text | Pre-tokenized text |
| Analyzer | ES standard | ES standard |
| Query | Raw query | Pre-processed query |
| Ưu điểm | ES tự xử lý tốt | Kiểm soát được preprocessing |
| Nhược điểm | Phụ thuộc ES analyzer | Phải preprocess query |

---

## 5.6. Luồng xử lý truy vấn chung

```
User Query: "quy định về thuế thu nhập cá nhân"
        │
        ▼
TextProcessor.process_text()
        │
        ▼
Query Terms: ["quy_định", "thuế", "thu_nhập", "cá_nhân"]
        │
        ▼
Match method:
├── boolean  → BooleanRetrieval.search()
├── vsm      → VectorSpaceModel.search()
├── bm25     → OkapiBM25.search()
├── es_normal→ ElasticSearchIndexing.search(is_normal_index=True)
└── es_proc  → ElasticSearchIndexing.search(is_normal_index=False)
        │
        ▼
Results: List[Tuple[doc_id, score]]
        │
        ▼
Display: Rank, doc_id, score, raw_text preview
```

## 5.7. Tham chiếu code

| Phương pháp | Class | Method chính | File |
|------------|-------|-------------|------|
| Boolean | `BooleanRetrieval` | `search(query_terms)` | `src/model/boolean_retrieval.py:12` |
| VSM | `VectorSpaceModel` | `search(query_terms, top_n)` | `src/model/vector_space_model.py:32` |
| BM25 | `OkapiBM25` | `search(query_terms, top_n)` | `src/model/bm25.py:40` |
| ES | `ElasticSearchIndexing` | `search(query, top_n, is_normal_index)` | `src/indexing/elasticsearch_indexing.py:72` |
