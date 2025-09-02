import hashlib
import re


def normalize(text: str) -> str:
    """
    Нормализует текст для поиска/сравнения:
    - приводит к нижнему регистру
    - убирает лишние пробелы
    - обрезает по краям
    """
    if not text:
        return ""

    # lower + trim
    text = text.lower().strip()

    # collapse spaces (и табы, и переводы строк -> один пробел)
    text = re.sub(r"\s+", " ", text)

    return text


def qhash(text: str) -> str:
    """
    SHA-256 хэш от нормализованного текста.
    Используется как ключ для gpt_cache.
    """
    norm = normalize(text)
    return hashlib.sha256(norm.encode("utf-8")).hexdigest()


def shorten(text: str, max_len: int = 200) -> str:
    """
    Усечение строки для логов или промптов LLM.
    """
    if len(text) <= max_len:
        return text
    return text[:max_len - 3] + "..."
