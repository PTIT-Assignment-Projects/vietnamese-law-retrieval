# 6. Đánh giá và kết quả thực nghiệm

## 6.1. Thiết lập đánh giá

### 6.1.1. Tập đánh giá

- **Số lượng queries**: 2,000 queries (từ `train_test_merged.csv`)
- **Ground truth**: Mỗi query có 1 hoặc nhiều `cid` liên quan được gán nhãn

### 6.1.2. Các chỉ số đánh giá

| Chỉ số | Công thức | Ý nghĩa |
|--------|-----------|---------|
| **Precision@K** | `|relevant ∩ retrieved@K| / K` | Tỷ lệ kết quả đúng trong top-K |
| **Recall@K** | `|relevant ∩ retrieved@K| / |relevant|` | Tỷ lệ tìm được hết kết quả đúng |
| **F1@K** | `2 × P@K × R@K / (P@K + R@K)` | Trung bình điều hòa của P và R |
| **Reciprocal Rank (RR)** | `1 / rank_of_first_relevant` | Vị trí của kết quả đúng đầu tiên |
| **MRR** | `mean(RR over all queries)` | RR trung bình |
| **Average Precision (AP)** | `Σ(P@k × rel(k)) / |relevant|` | AP của một query |
| **MAP** | `mean(AP over all queries)` | AP trung bình |

### 6.1.3. Giá trị K đánh giá

K ∈ {1, 2, 3, 5, 10}

### 6.1.4. Quy trình đánh giá

```
Algorithm: Evaluation Pipeline
Input: search_engine, ground_truth: Dict[qid, List[cid]], queries: Dict[qid, question]

For each method in [Boolean, VSM, BM25, ES_Normal, ES_Processed]:
    For each (qid, question) in queries:
        1. results = search_engine.search(question, method, top_n=10)
        2. retrieved_ids = [doc_id for doc_id, _ in results]
        3. true_ids = ground_truth[qid]
        4. For each K in [1, 2, 3, 5, 10]:
           - precision@K = calculate_precision_at_k(retrieved_ids, true_ids, K)
           - recall@K = calculate_recall_at_k(retrieved_ids, true_ids, K)
           - f1@K = calculate_f1_at_k(retrieved_ids, true_ids, K)
        5. rr = reciprocal_rank(retrieved_ids, true_ids)
        6. ap = calculate_average_precision(retrieved_ids, true_ids)
    Aggregate: mean of all metrics across all queries
```

## 6.2. Kết quả thực nghiệm

### 6.2.1. Bảng tổng hợp kết quả (5 phương pháp)

Đánh giá trên **2,000 queries**:

| Phương pháp | P@1 | P@5 | P@10 | R@10 | F1@10 | MRR | MAP |
|------------|-----|-----|------|------|-------|-----|-----|
| **ES (Processed)** | **0.4132** | **0.1349** | **0.0771** | **0.7708** | **0.1401** | **0.5284** | **0.5284** |
| **BM25** | 0.4120 | 0.1358 | 0.0770 | 0.7695 | 0.1399 | 0.5269 | 0.5269 |
| ES (Normal) | 0.4012 | 0.1339 | 0.0737 | 0.7372 | 0.1340 | 0.5136 | 0.5136 |
| VSM | 0.2195 | 0.0963 | 0.0627 | 0.6270 | 0.1140 | 0.3353 | 0.3353 |
| Boolean | 0.1305 | 0.0541 | 0.0306 | 0.3060 | 0.0556 | 0.1900 | 0.1900 |

### 6.2.2. Bảng chi tiết theo K (Local models)

**BM25:**

| K | Precision@K | Recall@K | F1@K |
|---|-------------|----------|------|
| 1 | 0.4120 | 0.4120 | 0.4120 |
| 2 | 0.2685 | 0.5370 | 0.3580 |
| 3 | 0.2033 | 0.6100 | 0.3050 |
| 5 | 0.1358 | 0.6790 | 0.2263 |
| 10 | 0.0769 | 0.7695 | 0.1399 |

**Boolean:**

| K | Precision@K | Recall@K | F1@K |
|---|-------------|----------|------|
| 1 | 0.1305 | 0.1305 | 0.1305 |
| 2 | 0.0995 | 0.1990 | 0.1327 |
| 3 | 0.0778 | 0.2335 | 0.1167 |
| 5 | 0.0541 | 0.2705 | 0.0902 |
| 10 | 0.0306 | 0.3060 | 0.0556 |

**VSM:**

| K | Precision@K | Recall@K | F1@K |
|---|-------------|----------|------|
| 1 | 0.2195 | 0.2195 | 0.2195 |
| 2 | 0.1633 | 0.3265 | 0.2177 |
| 3 | 0.1323 | 0.3970 | 0.1985 |
| 5 | 0.0963 | 0.4815 | 0.1605 |
| 10 | 0.0627 | 0.6270 | 0.1140 |

### 6.2.3. Bảng chi tiết theo K (Elasticsearch)

**ES Processed Index:**

| K | Precision@K | Recall@K | F1@K |
|---|-------------|----------|------|
| 1 | 0.4132 | 0.4132 | 0.4132 |
| 2 | 0.2716 | 0.5432 | 0.3621 |
| 3 | 0.2043 | 0.6128 | 0.3064 |
| 5 | 0.1349 | 0.6744 | 0.2248 |
| 10 | 0.0771 | 0.7708 | 0.1401 |

**ES Normal Index:**

| K | Precision@K | Recall@K | F1@K |
|---|-------------|----------|------|
| 1 | 0.4012 | 0.4012 | 0.4012 |
| 2 | 0.2644 | 0.5288 | 0.3525 |
| 3 | 0.1988 | 0.5964 | 0.2982 |
| 5 | 0.1339 | 0.6696 | 0.2232 |
| 10 | 0.0737 | 0.7372 | 0.1340 |

## 6.3. Phân tích kết quả

### 6.3.1. Xếp hạng các phương pháp

```
MRR Ranking:
1. ES (Processed)  ████████████████████████████████████  0.5284
2. BM25            ████████████████████████████████████  0.5269
3. ES (Normal)     ██████████████████████████████████    0.5136
4. VSM             ████████████████████████              0.3353
5. Boolean         █████████████                         0.1900
```

### 6.3.2. Phân tích chi tiết

**1. BM25 vs ES Processed (Best performers)**
- Hai phương pháp có hiệu suất **gần như tương đương** (MRR chênh lệch 0.0015)
- ES Processed nhỉnh hơn một chút do BM25 implementation của Elasticsearch đã được tối ưu
- Cả hai đạt ~77% Recall@10, nghĩa là trong top 10 kết quả có chứa ~77% tài liệu liên quan

**2. ES Normal vs ES Processed**
- ES Processed tốt hơn ES Normal: MRR 0.5284 vs 0.5136 (+2.9%)
- Điều này chứng tỏ **tiền xử lý văn bản giúp cải thiện hiệu suất** tìm kiếm
- Khi query được tokenize trước, ES matching chính xác hơn

**3. BM25 vs VSM**
- BM25 vượt trội hơn VSM: MRR 0.5269 vs 0.3353 (+57%)
- BM25 xử lý TF saturation tốt hơn sublinear TF
- BM25 length normalization giúp công bằng giữa văn bản dài và ngắn

**4. Boolean Retrieval**
- Hiệu suất thấp nhất: MRR 0.1900
- Không có xếp hạng → không có thông tin về mức độ liên quan
- Chỉ phù hợp khi cần tìm chính xác (exact match)

### 6.3.3. Xu hướng theo K

```
Precision@K giảm khi K tăng:
- P@1 ≈ 0.41 (BM25/ES) → P@10 ≈ 0.077
- Đây là xu hướng bình thường trong IR

Recall@K tăng khi K tăng:
- R@1 ≈ 0.41 (BM25/ES) → R@10 ≈ 0.77
- Top 10 chứa phần lớn tài liệu liên quan
```

## 6.4. Tổng kết

| Nhận xét | Chi tiết |
|----------|----------|
| Phương pháp tốt nhất | BM25 và ES (Processed) - hiệu suất tương đương |
| Tác động của preprocessing | ES Processed > ES Normal (+2.9% MRR) |
| Khoảng cách BM25 vs VSM | BM25 vượt VSM 57% về MRR |
| Boolean limitation | Không xếp hạng, hiệu suất thấp nhất |
| Recall@10 cao nhất | 77.08% (ES Processed) |

## 6.5. File kết quả

| File | Nội dung |
|------|----------|
| `util_file/evaluation_result.csv` | Kết quả Boolean, VSM, BM25 |
| `util_file/evaluation_es_result.csv` | Kết quả ES Normal, ES Processed |
| `util_file/evaluation_all_result.csv` | Tổng hợp tất cả 5 phương pháp |
