import logging
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from app.domain.events import HikvisionEvent
from app.infrastructure.database import Database
from app.integrations.hikvision.client import HikvisionClient
from app.integrations.telegram.client import TelegramClient


class EventProcessor:

    ALERT_COOLDOWN = timedelta(minutes=2)

    def __init__(
        self,
        username: str,
        password: str,
        database: Database,
        telegram: TelegramClient,
        target_types: set[str],
    ):

        self.username = username
        self.password = password
        self.database = database
        self.telegram = telegram
        self.target_types = target_types
        self._last_alert_at: dict[tuple[str, str], datetime] = {}

    def is_relevant_event(
        self,
        event: HikvisionEvent,
    ) -> bool:

        if event.event_state != "active":
            return False

        if not event.target_type:
            return False

        return (
            event.target_type
            in self.target_types
        )

    def target_description(
        self,
        target_type: str | None,
    ) -> str:

        if target_type == "human":
            return "Pessoa detectada"

        if target_type == "vehicle":
            return "Veículo detectado"

        return "Alvo detectado"

    def should_notify(
        self,
        event: HikvisionEvent,
    ) -> bool:

        if not self.is_relevant_event(event):
            return False

        alert_key = (
            event.camera_ip,
            event.event_type or "unknown",
        )
        event_time = event.received_at.astimezone(timezone.utc)
        last_alert = self._last_alert_at.get(alert_key)

        if last_alert and event_time - last_alert < self.ALERT_COOLDOWN:
            return False

        self._last_alert_at[alert_key] = event_time
        return True

    async def process_event(
        self,
        event: HikvisionEvent,
        *,
        client: HikvisionClient | None = None,
    ) -> None:

        self.database.save_event(event)

        if not self.should_notify(event):
            return

        logger = logging.getLogger(
            f"camera.{event.camera_ip}"
        )

        logger.info(
            "[%s] Relevant event: target=%s camera=%s",
            event.camera_ip,
            event.target_type,
            event.channel_name,
        )

        try:
            snapshot_client = client or HikvisionClient(
                host=event.camera_ip,
                username=self.username,
                password=self.password,
            )

            photo = await snapshot_client.get_snapshot()

            await self.telegram.send_photo(
                photo=photo,
                caption=self.format_message(event),
            )

            logger.info(
                "[%s] Telegram notification with snapshot sent",
                event.camera_ip,
            )

        except Exception:
            logger.exception(
                "[%s] Failed to send Telegram notification with snapshot",
                event.camera_ip,
            )

    def format_message(
        self,
        event: HikvisionEvent,
    ) -> str:

        timestamp = (
            event.received_at
            .astimezone(
                ZoneInfo("America/Sao_Paulo")
            )
            .strftime("%d/%m/%Y %H:%M:%S")
        )

        description = self.target_description(
            event.target_type
        )

        camera_name = (
            event.channel_name
            or "Câmera sem nome"
        )

        return (
            "🚨 Home Integrator\n\n"
            f"{description}\n\n"
            f"Câmera: {camera_name}\n"
            f"IP: {event.camera_ip}\n"
            f"Horário: {timestamp}"
        )

    async def monitor_camera(
        self,
        camera_ip: str,
    ) -> None:

        logger = logging.getLogger(
            f"camera.{camera_ip}"
        )

        client = HikvisionClient(
            host=camera_ip,
            username=self.username,
            password=self.password,
        )

        async for event in client.events():

            logger.debug(
                "[%s] Event: "
                "type=%s state=%s target=%s",
                camera_ip,
                event.event_type,
                event.event_state,
                event.target_type,
            )

            await self.process_event(event, client=client)
