import asyncio
import logging

import httpx

from app.integrations.hikvision.parser import (
    extract_xml_documents,
    parse_event,
)

logger = logging.getLogger(__name__)


class HikvisionClient:

    def __init__(
        self,
        host: str,
        username: str,
        password: str,
    ):

        self.host = host

        self.url = (
            f"http://{host}"
            "/ISAPI/Event/notification/"
            "alertStream"
        )

        self.snapshot_url = (
            f"http://{host}"
            "/ISAPI/Streaming/channels/101/picture"
        )

        self.auth = httpx.DigestAuth(
            username,
            password,
        )

    async def events(self):

        while True:

            try:

                async for event in self._stream():
                    yield event

            except asyncio.CancelledError:
                raise

            except Exception:

                logger.exception(
                    "[%s] Hikvision event stream failed. "
                    "Reconnecting in 5 seconds.",
                    self.host,
                )

                await asyncio.sleep(5)

    async def _stream(self):

        timeout = httpx.Timeout(
            connect=10.0,
            read=None,
            write=10.0,
            pool=10.0,
        )

        async with httpx.AsyncClient(
            auth=self.auth,
            timeout=timeout,
        ) as client:

            logger.info(
                "[%s] Connecting to Hikvision: %s",
                self.host,
                self.url,
            )

            async with client.stream(
                "GET",
                self.url,
            ) as response:

                response.raise_for_status()

                logger.info(
                    "[%s] Hikvision event stream connected: "
                    "HTTP %s",
                    self.host,
                    response.status_code,
                )

                buffer = ""

                async for chunk in response.aiter_text():

                    buffer += chunk

                    documents, buffer = (
                        extract_xml_documents(
                            buffer
                        )
                    )

                    for document in documents:

                        try:

                            yield parse_event(
                                document,
                                self.host,
                            )

                        except Exception:

                            logger.exception(
                                "[%s] Failed to parse "
                                "Hikvision event XML",
                                self.host,
                            )

    async def get_snapshot(self) -> bytes:

        timeout = httpx.Timeout(
            connect=10.0,
            read=10.0,
            write=10.0,
            pool=10.0,
        )

        async with httpx.AsyncClient(
            auth=self.auth,
            timeout=timeout,
        ) as client:

            response = await client.get(
                self.snapshot_url
            )

            response.raise_for_status()

            return response.content
