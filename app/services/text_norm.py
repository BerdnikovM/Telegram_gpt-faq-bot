import re
import hashlib

try:
    import pymorphy2
    morph = pymorphy2.MorphAnalyzer()
except ImportError:
    morph = None  # fallback, если pymorphy2 не установлен


def normalize(text: str) -> str:
    """
    Нормализация текста:
    - приведение к нижнему регистру
    - удаление лишних пробелов
    - опциональная лемматизация (через pymorphy2, если доступна)
    """
    text = text.lower().strip()
    text = re.sub(r"\s+", " ", text)

    if morph:
        tokens = re.findall(r"[а-яёa-z0-9]+", text)
        lemmas = []
        for t in tokens:
            try:
                lemma = morph.parse(t)[0].normal_form
                lemmas.append(lemma)
            except Exception:
                lemmas.append(t)
        return " ".join(lemmas)

    return text


def qhash(text: str) -> str:
    """
    SHA-256 хэш нормализованного текста
    """
    return hashlib.sha256(normalize(text).encode("utf-8")).hexdigest()


def shorten(text: str, limit: int = 100) -> str:
    """
    Урезать длинный текст до limit символов (для логов/отладки)
    """
    return text if len(text) <= limit else text[:limit] + "..."
