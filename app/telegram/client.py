import httpx


class TelegramClient:
    def __init__(self, token: str, chat_id: str):
        self.url = f"https://api.telegram.org/bot{token}/sendMessage"
        self.chat_id = chat_id

    async def send_message(self, text: str) -> None:
        payload = {
            "chat_id": self.chat_id,
            "text": text,
        }

        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.post(
                self.url,
                json=payload,
            )
            response.raise_for_status()
