import re
from typing import List

from underthesea import text_normalize, word_tokenize

from src.preprocessing.preprocessing import load_vietnamese_stopwords


class TextProcessor:
    def __init__(self):
        self.stopwords = load_vietnamese_stopwords()
        self._valid_token_pattern = re.compile(
            r"^[a-z0-9_\u00E0-\u01FF\u1EA0-\u1EFF.-]+$"
        )
    def _clean_tokens(self, text: str) -> List[str]:
        if text is None:
            raise ValueError("Input text cannot be None")
        words = text_normalize(text)
        words = words.lower()
        # invalid token
        text = words.replace("\ufffd", " ")
        tokens = word_tokenize(text, format="text", use_token_normalize=True).split()
        cleaned_tokens = []
        for t in tokens:
            # Only keep tokens that match our valid character set
            if not self._valid_token_pattern.match(t):
                continue

            # Finally, check for stopwords and length
            if t not in self.stopwords and len(t) > 1:
                cleaned_tokens.append(t)
        return cleaned_tokens
    def process_text(self, text: str) -> List[str]:
        return self._clean_tokens(text)
    def process_text_join_for_es(self, text: str) -> str:
        return " ".join(self._clean_tokens(text))