import re

import pandas as pd
from underthesea import text_normalize, word_tokenize

from src.util.constant import VIETNAMESE_STOPWORDS_FILE_PATH


def load_data(file_path: str) -> pd.DataFrame :
    return pd.read_csv(file_path)

def load_vietnamese_stopwords() -> set[str]:
    with open(VIETNAMESE_STOPWORDS_FILE_PATH, "r", encoding="utf-8") as f:
        return {
            line.strip().replace(" ", "_").lower() # match with underthesea tokenize words
            for line in f
            if line.strip()
        }
stopwords = load_vietnamese_stopwords()
def process_text(text: str) -> str:
    words = text_normalize(text)
    words = words.lower()
    # invalid token
    text = words.replace("\ufffd", " ")
    tokens = word_tokenize(text, format="text", use_token_normalize=True).split()
    valid_pattern = re.compile(
        r'^[a-z0-9_àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ\.\-]+$')
    cleaned_tokens = []
    for t in tokens:
        # Only keep tokens that match our valid character set
        if not valid_pattern.match(t):
            continue

        # Finally, check for stopwords and length
        if t not in stopwords and len(t) > 1:
            cleaned_tokens.append(t)
    return " ".join(cleaned_tokens)
