import requests
from app.config import YANDEX_API_KEY, YANDEX_CATALOG_ID
import os
import logging

logger = logging.getLogger(__name__)

class LLMProvider:
    async def answer(self, question: str, context_chunks: list[str]) -> str:
        raise NotImplementedError


class YandexGPTProvider(LLMProvider):
    def __init__(self):
        self.api_key = YANDEX_API_KEY
        self.catalog_id = YANDEX_CATALOG_ID
        self.model = os.getenv("YANDEX_MODEL", "yandexgpt-lite")
        self.url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"

    async def answer(self, question: str, context_chunks: list[str]) -> str:
        if not self.api_key or not self.catalog_id:
            return "⚠️ Ошибка: не заданы ключ API или каталог Yandex."

        messages = [
            {"role": "system", "text": "Ты — помощник поддержки. Отвечай кратко и по делу."}
        ]

        if context_chunks:
            messages.append({"role": "user", "text": "Контекст:\n" + "\n".join(context_chunks)})

        messages.append({"role": "user", "text": question})

        payload = {
            "modelUri": f"gpt://{self.catalog_id}/{self.model}",
            "completionOptions": {
                "stream": False,
                "temperature": 0.6,
                "maxTokens": "500"
            },
            "messages": messages
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Api-Key {self.api_key}"
        }

        try:
            logger.debug(f"[YANDEX REQUEST] {payload}")
            response = requests.post(self.url, headers=headers, json=payload, timeout=30)

            if response.status_code != 200:
                logger.error(f"[YANDEX ERROR RESPONSE] {response.text}")  # <-- теперь видим тело ошибки
                return f"⚠️ Ошибка при обращении к YandexGPT: {response.text}"

            data = response.json()
            return data.get("result", {}).get("alternatives", [{}])[0].get("message", {}).get("text", "⚠️ Нет текста в ответе")
        except Exception as e:
            logger.exception("Ошибка при запросе к YandexGPT")
            return f"⚠️ Ошибка при обращении к YandexGPT: {e}"


# === Фабрика для получения провайдера ===
def get_llm_provider() -> LLMProvider:
    """
    Возвращает активный LLM-провайдер.
    Сейчас доступен только YandexGPT.
    """
    return YandexGPTProvider()
