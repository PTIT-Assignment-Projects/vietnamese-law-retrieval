import re
from typing import List

from underthesea import text_normalize, word_tokenize

from src.preprocessing.preprocessing import load_vietnamese_stopwords


class TextProcessor:
    def __init__(self):
        self.stopwords = load_vietnamese_stopwords()

    def process_text(self, text: str) -> List[str]:
        if text is None:
            raise ValueError("Input text cannot be None")
        words = text_normalize(text)
        words = words.lower()
        # invalid token
        text = words.replace("\ufffd", " ")
        tokens = word_tokenize(text, format="text", use_token_normalize=True).split()
        valid_pattern = re.compile(
            r"^[a-z0-9_\u00E0-\u01FF\u1EA0-\u1EFF.-]+$"
        )
        cleaned_tokens = []
        for t in tokens:
            # Only keep tokens that match our valid character set
            if not valid_pattern.match(t):
                continue

            # Finally, check for stopwords and length
            if t not in self.stopwords and len(t) > 1:
                cleaned_tokens.append(t)
        return list(set(cleaned_tokens))