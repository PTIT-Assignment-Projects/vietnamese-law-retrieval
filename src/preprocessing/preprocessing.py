import pandas as pd
from src.util.constant import VIETNAMESE_STOPWORDS_FILE_PATH


def load_data(file_path: str) -> pd.DataFrame:
    return pd.read_csv(file_path)

def load_vietnamese_stopwords() -> set[str]:
    with open(VIETNAMESE_STOPWORDS_FILE_PATH, "r", encoding="utf-8") as f:
        return {
            line.strip().replace(" ", "_").lower() # match with underthesea tokenize words
            for line in f
            if line.strip()
        }
