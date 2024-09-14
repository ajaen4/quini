import unidecode
import re


def clean_text(text: str) -> str:
    text = unidecode.unidecode(text)

    cleaned_text = re.sub(r"[^a-zA-Z\s.]", "", text)
    cleaned_text = re.sub(r"\s+", " ", cleaned_text).strip()

    return cleaned_text
