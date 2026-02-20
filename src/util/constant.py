
from pathlib import Path
BASE = Path(__file__).resolve().parent.parent.parent
# DATA FILE
CORPUS_PATH = str(BASE / "data" / "corpus.csv")
TRAIN_PATH = str(BASE / "data" / "train.csv")
TEST_PATH = str(BASE / "data" / "test.csv")



# UTIL FILE
VIETNAMESE_STOPWORDS_FILE_PATH = str(BASE / "util_file" / "vietnamese-stopwords.txt")
RAW_CORPUS_DICT_PATH = str(BASE / "util_file" / "raw_corpus.pkl")
PROCESSED_CORPUS_DICT_PATH = str(BASE / "util_file" / "processed_corpus.pkl")
INVERTED_INDEX_BUILT_PATH = str(BASE / "util_file" / "inverted_index.pkl")
VSM_MODEL_INDEX_BUILT_PATH = str(BASE / "util_file" / "vsm_model_built.pkl")
BM25_MODEL_INDEX_BUILT_PATH = str(BASE / "util_file" / "bm25_model_built.pkl")
# COlUMN
CID_COLUMN = "cid"
TEXT_COLUMN = "text"

# MODEL_NAME
BOOLEAN_RETRIEVAL_NAME = "boolean"
VSM_MODEL_NAME = "vsm"
BM25_MODEL_NAME = "bm25"

# BOOLEAN_OPERATOR
AND_OPERATOR = "and"
OR_OPERATOR = "or"
NOT_OPERATOR = "not"