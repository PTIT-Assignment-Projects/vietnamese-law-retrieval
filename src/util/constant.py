
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

# COlUMN
CID_COLUMN = "cid"
TEXT_COLUMN = "text"