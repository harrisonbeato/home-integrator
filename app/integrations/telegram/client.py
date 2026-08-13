import httpx


class TelegramClient:

    def __init__(
        self,
        token: str,
        chat_id: str,
    ):

        self.url = (
            f"https://api.telegram.org/"
            f"bot{token}/sendMessage"
        )

        self.photo_url = (
            f"https://api.telegram.org/"
            f"bot{token}/sendPhoto"
        )

        self.chat_id = chat_id

    async def send_message(
        self,
        text: str,
    ) -> None:

        payload = {
            "chat_id": self.chat_id,
            "text": text,
        }

        async with httpx.AsyncClient(
            timeout=15,
        ) as client:

            response = await client.post(
                self.url,
                json=payload,
            )

            response.raise_for_status()

    async def send_photo(
        self,
        photo: bytes,
        caption: str,
    ) -> None:

        files = {
            "photo": (
                "snapshot.jpg",
                photo,
                "image/jpeg",
            )
        }

        data = {
            "chat_id": self.chat_id,
            "caption": caption,
        }

        async with httpx.AsyncClient(
            timeout=30,
        ) as client:

            response = await client.post(
                self.photo_url,
                data=data,
                files=files,
            )

            response.raise_for_status()
