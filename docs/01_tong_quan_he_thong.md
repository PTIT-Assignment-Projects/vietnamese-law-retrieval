# 1. Tổng quan hệ thống truy xuất văn bản pháp luật tiếng Việt

## 1.1. Mục tiêu

Xây dựng hệ thống truy xuất thông tin (Information Retrieval - IR) cho văn bản pháp luật tiếng Việt, cho phép người dùng nhập câu hỏi/truy vấn bằng tiếng Việt và hệ thống trả về các văn bản pháp luật liên quan nhất từ kho ngữ liệu.

## 1.2. Kiến trúc tổng thể

Hệ thống tuân theo pipeline kinh điển của IR: **Preprocess -> Index -> Retrieve -> Evaluate**

```
┌─────────────┐    ┌──────────────────┐    ┌─────────────────┐    ┌────────────┐
│  Corpus     │ -> │  Preprocessing   │ -> │   Indexing      │ -> │ Retrieval  │
│  (222K docs)│    │  (Vietnamese NLP)│    │ (Inverted Index │    │ (5 methods)│
│             │    │                  │    │  + Elasticsearch)│    │            │
└─────────────┘    └──────────────────┘    └─────────────────┘    └────────────┘
                                                                        │
                                                                        v
                                                                ┌────────────┐
                                                                │ Evaluation │
                                                                │ (P,R,F1,   │
                                                                │  MRR, MAP) │
                                                                └────────────┘
```

## 1.3. Cấu trúc thư mục

```
vietnamese-law-retrieval/
├── data/                              # Dữ liệu
│   ├── corpus.csv                     # 222,981 văn bản pháp luật
│   ├── train.csv                      # 9,541 câu hỏi huấn luyện
│   ├── test.csv                       # 3,184 câu hỏi kiểm tra
│   ├── train_test_merged.csv          # 12,725 câu hỏi tổng hợp
│   └── indices/                       # Elasticsearch Lucene indices
├── src/                               # Mã nguồn
│   ├── main.py                        # Entry point CLI
│   ├── app.py                         # Giao diện Streamlit
│   ├── search_engine.py               # Bộ điều phối chính
│   ├── preprocessing/
│   │   ├── preprocessing.py           # Đọc dữ liệu, load stopwords
│   │   └── text_processor.py          # Xử lý văn bản tiếng Việt
│   ├── indexing/
│   │   ├── inverted_index.py          # Inverted index tùy chỉnh
│   │   └── elasticsearch_indexing.py  # Elasticsearch integration
│   ├── model/
│   │   ├── model.py                   # Abstract base class
│   │   ├── boolean_retrieval.py       # Mô hình Boolean
│   │   ├── vector_space_model.py      # Mô hình VSM (TF-IDF + cosine)
│   │   └── bm25.py                    # Mô hình Okapi BM25
│   ├── evaluation/
│   │   ├── evaluation_metrics.py      # Các chỉ số đánh giá
│   │   ├── evaluator_service.py       # Đánh giá mô hình local
│   │   └── elasticsearch_evaluator.py # Đánh giá Elasticsearch
│   └── util/
│       ├── constant.py                # Hằng số, đường dẫn
│       └── pickle_handling.py         # Serialize/Deserialize
├── util_file/                         # File hỗ trợ
│   ├── vietnamese-stopwords.txt       # 1,941 từ dừng tiếng Việt
│   ├── raw_corpus.pkl                 # Corpus gốc (dict)
│   ├── processed_corpus.pkl           # Corpus đã xử lý (dict)
│   ├── inverted_index.pkl             # Inverted index đã build
│   ├── vsm_model_built.pkl            # Mô hình VSM
│   ├── bm25_model_built.pkl           # Mô hình BM25
│   ├── evaluation_result.csv          # Kết quả đánh giá local models
│   ├── evaluation_es_result.csv       # Kết quả đánh giá Elasticsearch
│   └── evaluation_all_result.csv      # Kết quả tổng hợp
├── docker-compose.yml                 # Elasticsearch + Kibana
├── requirements.txt                   # Dependencies
└── .env                               # Biến môi trường
```

## 1.4. Công nghệ sử dụng

| Thư viện | Phiên bản | Công dụng |
|----------|-----------|-----------|
| pandas | 2.3.3 | Đọc/xử lý dữ liệu CSV, DataFrame |
| underthesea | 9.2.11 | Xử lý ngôn ngữ tiếng Việt (chuẩn hóa, tách từ) |
| elasticsearch | 9.2.1 | Client kết nối Elasticsearch |
| python-dotenv | 1.1.1 | Đọc biến môi trường từ .env |
| streamlit | 1.54.0 | Xây dựng giao diện web |

## 1.5. Hạ tầng

- **Elasticsearch 9.0.2**: Công cụ tìm kiếm全文, chạy qua Docker
- **Kibana 9.0.2**: Giao diện quản lý và trực quan hóa Elasticsearch
- Cấu hình Docker Compose: single-node, tắt bảo mật, port 9200 (ES) và 5601 (Kibana)

## 1.6. Các mô hình truy xuất

| # | Mô hình | Loại | Đặc điểm |
|---|---------|------|-----------|
| 1 | Boolean Retrieval | Set-based | AND/OR/NOT trên posting lists |
| 2 | Vector Space Model (VSM) | Vector-based | TF-IDF + cosine similarity |
| 3 | Okapi BM25 | Probabilistic | TF saturation + length normalization |
| 4 | Elasticsearch (Normal) | Search engine | Standard analyzer, match query |
| 5 | Elasticsearch (Processed) | Search engine | Pre-tokenized text, match query |

## 1.7. Quy trình hoạt động

1. **Load dữ liệu**: Đọc corpus.csv, train/test CSV files
2. **Tiền xử lý**: Chuẩn hóa -> lowercase -> tách từ -> lọc token -> bỏ stopwords
3. **Xây dựng chỉ mục**: Tạo Inverted Index, sau đó build VSM và BM25 trên đó; đồng thời ingest vào Elasticsearch
4. **Truy xuất**: Người dùng nhập query -> tiền xử lý query -> truy vấn trên mô hình đã chọn -> trả về top-N kết quả
5. **Đánh giá**: Tính Precision@K, Recall@K, F1@K, MRR, MAP trên tập test
