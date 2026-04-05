# 4. Xây dựng chỉ mục (Indexing)

## 4.1. Tổng quan

Hệ thống sử dụng hai loại chỉ mục:
1. **Inverted Index tùy chỉnh** - phục vụ cho Boolean, VSM, BM25
2. **Elasticsearch Index** - phục vụ cho tìm kiếm全文 qua Elasticsearch

## 4.2. Inverted Index (Chỉ mục đảo)

### 4.2.1. Cấu trúc dữ liệu

**File:** `src/indexing/inverted_index.py`

```python
class InvertedIndex:
    def __init__(self):
        self.index = defaultdict(list)      # term -> [(doc_id, position), ...]
        self.doc_lengths = {}                # doc_id -> độ dài (số tokens)
        self.doc_terms = defaultdict(Counter) # doc_id -> {term: count}
        self.term_doc_freq = {}              # term -> số docs chứa term (DF)
        self.term_docs = {}                  # term -> set of doc_ids
        self.total_docs = 0                  # Tổng số documents (N)
        self.avg_doc_length = 0              # Độ dài trung bình của document
```

### 4.2.2. Thuật toán xây dựng

```
Algorithm: Build Inverted Index
Input: documents: Dict[doc_id, List[term]]
Output: Inverted Index structures

1. total_docs = len(documents)
2. total_length = 0
3. For each (cid, terms) in documents:
   a. doc_length = len(terms)
   b. doc_lengths[cid] = doc_length
   c. total_length += doc_length
   d. doc_terms[cid] = Counter(terms)
   e. For each (pos, term) in enumerate(terms):
      - index[term].append((cid, pos))
      - term_docs[term].add(cid)
4. avg_doc_length = total_length / total_docs
5. term_doc_freq[term] = len(term_docs[term]) for each term
```

### 4.2.3. Chi tiết từng thành phần

| Thành phần | Kiểu dữ liệu | Mô tả | Ví dụ |
|-----------|-------------|-------|-------|
| `index` | `Dict[str, List[Tuple]]` | Term -> [(doc_id, position)] | `"thuế": [(100, 0), (100, 5), (205, 3)]` |
| `doc_lengths` | `Dict[str, int]` | Độ dài mỗi doc (số token) | `{0: 45, 1: 120, ...}` |
| `doc_terms` | `Dict[str, Counter]` | Tần suất term trong doc | `{0: {"thuế": 3, "luật": 1}}` |
| `term_doc_freq` | `Dict[str, int]` | Document frequency (DF) | `{"thuế": 5420}` |
| `term_docs` | `Dict[str, Set]` | Tập doc chứa term | `{"thuế": {0, 100, 205, ...}}` |
| `total_docs` | `int` | Tổng số documents | `222981` |
| `avg_doc_length` | `float` | Độ dài TB | ~XX tokens/doc |

### 4.2.4. Các phương thức truy vấn

```python
def get_docs_contain_term(self, term: str) -> Set[str]:
    """Trả về tập các doc_id chứa term"""
    return self.term_docs.get(term, set())

def get_term_frequency(self, term: str, doc_id: str) -> int:
    """Trả về TF của term trong document"""
    return self.doc_terms[doc_id].get(term, 0)

def get_doc_frequency(self, term: str) -> int:
    """Trả về DF - số documents chứa term"""
    return self.term_doc_freq.get(term, 0)
```

### 4.2.5. Lưu trữ

Inverted index được serialize bằng pickle:
- **File:** `util_file/inverted_index.pkl`
- **Kích thước:** ~46 MB

## 4.3. Elasticsearch Index

### 4.3.1. Cấu hình

**File:** `src/indexing/elasticsearch_indexing.py`

Hệ thống tạo **2 indices** trong Elasticsearch:

| Index | Tên | Nội dung | Analyzer |
|-------|-----|----------|----------|
| Normal Index | `normal_index` | Văn bản gốc (raw text) | Standard (ES built-in) |
| Processed Index | `processed_text_index` | Văn bản đã tokenize (nối bằng khoảng trắng) | Standard |

### 4.3.2. Mapping

```json
{
  "mappings": {
    "properties": {
      "content": {
        "type": "text",
        "analyzer": "standard",
        "fields": {
          "keyword": {
            "type": "keyword",
            "ignore_above": 256
          }
        }
      }
    }
  }
}
```

- `content` (text): Nội dung văn bản, được phân tích bởi standard analyzer
- `content.keyword` (keyword): Trường keyword để exact match, giới hạn 256 ký tự

### 4.3.3. Quá trình Ingest

```python
# Normal index: ingest raw text
for doc_id, text in self.raw_documents.items():
    yield {
        "_index": NORMAL_INDEX_NAME,      # "normal_index"
        "_id": doc_id,
        "_source": {"content": text}
    }

# Processed index: ingest pre-tokenized text
for doc_id, token_list in self.processed_documents.items():
    yield {
        "_index": PROCESSED_INDEX_NAME,    # "processed_text_index"
        "_id": doc_id,
        "_source": {"content": " ".join(token_list)}
    }
```

Dữ liệu được ingest bằng `elasticsearch.helpers.bulk()` cho hiệu suất cao.

### 4.3.4. Hạ tầng Docker

```yaml
# docker-compose.yml
services:
  elastic:
    image: docker.elastic.co/elasticsearch/elasticsearch:9.0.2
    ports: ["127.0.0.1:9200:9200"]
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
      - xpack.security.http.ssl.enabled=false
    volumes:
      - ./data:/usr/share/elasticsearch/data
  kibana:
    image: docker.elastic.co/kibana/kibana:9.0.2
    ports: ["5601:5601"]
```

## 4.4. Quan hệ giữa các chỉ mục

```
                    ┌──────────────────┐
                    │  processed_corpus│
                    │     (pickle)     │
                    └────────┬─────────┘
                             │
                    ┌────────▼─────────┐
                    │  Inverted Index  │
                    │    (pickle)      │
                    └───┬────┬────┬────┘
                        │    │    │
           ┌────────────┘    │    └────────────┐
           │                 │                 │
    ┌──────▼──────┐  ┌──────▼──────┐  ┌───────▼──────┐
    │ Boolean     │  │ VSM         │  │ BM25         │
    │ Retrieval   │  │ (TF-IDF)    │  │ (k1=1.5,    │
    │             │  │             │  │  b=0.75)    │
    └─────────────┘  └─────────────┘  └──────────────┘

    ┌──────────────────────────────────────────────────┐
    │              Elasticsearch                        │
    │  ┌─────────────────┐  ┌───────────────────────┐ │
    │  │ normal_index    │  │ processed_text_index  │ │
    │  │ (raw text)      │  │ (tokenized text)      │ │
    │  └─────────────────┘  └───────────────────────┘ │
    └──────────────────────────────────────────────────┘
```
