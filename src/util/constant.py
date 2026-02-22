
from pathlib import Path
BASE = Path(__file__).resolve().parent.parent.parent
# DATA FILE
CORPUS_PATH = str(BASE / "data" / "corpus.csv")
TRAIN_PATH = str(BASE / "data" / "train.csv")
TEST_PATH = str(BASE / "data" / "test.csv")
TRAIN_TEST_MERGED_PATH = str(BASE / "data" / "train_test_merged.csv")



# UTIL FILE
VIETNAMESE_STOPWORDS_FILE_PATH = str(BASE / "util_file" / "vietnamese-stopwords.txt")
RAW_CORPUS_DICT_PATH = str(BASE / "util_file" / "raw_corpus.pkl")
PROCESSED_CORPUS_DICT_PATH = str(BASE / "util_file" / "processed_corpus.pkl")
RAW_EVALUATION_DOCUMENT_PATH = str(BASE / "util_file" / "raw_evaluation_document.pkl")
GROUND_TRUTH_EVALUATION_DOCUMENT_PATH = str(BASE / "util_file" / "ground_truth_evaluation_document.pkl")
INVERTED_INDEX_BUILT_PATH = str(BASE / "util_file" / "inverted_index.pkl")
VSM_MODEL_INDEX_BUILT_PATH = str(BASE / "util_file" / "vsm_model_built.pkl")
BM25_MODEL_INDEX_BUILT_PATH = str(BASE / "util_file" / "bm25_model_built.pkl")
EVALUATION_RESULT_FILE_PATH = str(BASE / "util_file" / "evaluation_result.csv")
# COlUMN
CID_COLUMN = "cid"
TEXT_COLUMN = "text"
QID_COLUMN = "qid"
QUESTION_COLUMN = "question"

# MODEL_NAME
BOOLEAN_RETRIEVAL_NAME = "boolean"
VSM_MODEL_NAME = "vsm"
BM25_MODEL_NAME = "bm25"

# BOOLEAN_OPERATOR
AND_OPERATOR = "and"
OR_OPERATOR = "or"
NOT_OPERATOR = "not"


# ELastic search
PROCESSED_INDEX_NAME = "processed_text_index"
NORMAL_INDEX_NAME = "normal_index"
EVALUATION_ES_RESULT_FILE_PATH = str(BASE / "util_file" / "evaluation_result_es.csv")