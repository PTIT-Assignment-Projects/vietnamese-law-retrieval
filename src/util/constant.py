
from pathlib import Path
BASE = Path(__file__).resolve().parent.parent.parent
# DATA FILE
CORPUS_PATH = str(BASE / "data" / "corpus.csv")
TRAIN_PATH = str(BASE / "data" / "train.csv")
TEST_PATH = str(BASE / "data" / "test.csv")



# UTIL FILE

VIETNAMESE_STOPWORDS_FILE_PATH = str(BASE / "util_file" / "vietnamese-stopwords.txt")