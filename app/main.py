import asyncio
import logging

from app.config import get_settings
from app.database import Database
from app.hikvision.client import HikvisionClient
from app.models import HikvisionEvent
from app.telegram.client import TelegramClient


def configure_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )


def should_send(event: HikvisionEvent) -> bool:
    settings = get_settings()

    if settings.hikvision_channels:
        if event.channel_id not in settings.channels:
            return False

    if settings.telegram_send_all_events:
        return True

    if not event.event_type:
        return False

    return event.event_type.lower() in settings.event_types


def format_message(event: HikvisionEvent) -> str:
    timestamp = event.received_at.astimezone().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    return (
        "🚨 Home Integrator\n\n"
        f"Evento: {event.event_type or 'unknown'}\n"
        f"Canal: {event.channel_id or 'unknown'}\n"
        f"Estado: {event.event_state or 'unknown'}\n"
        f"Horário: {timestamp}"
    )


async def run() -> None:
    settings = get_settings()
    configure_logging(settings.log_level)

    logger = logging.getLogger(__name__)

    database = Database(settings.database_path)
    database.initialize()

    hikvision = HikvisionClient(
        host=settings.hikvision_host,
        username=settings.hikvision_username,
        password=settings.hikvision_password,
    )

    telegram = TelegramClient(
        token=settings.telegram_bot_token,
        chat_id=settings.telegram_chat_id,
    )

    logger.info("Home Integrator started")
    logger.info("Database: %s", settings.database_path)

    async for event in hikvision.events():
        database.save_event(
            received_at=event.received_at.isoformat(),
            event_type=event.event_type,
            event_state=event.event_state,
            channel_id=event.channel_id,
            payload=event.raw_xml,
        )

        logger.info(
            "Hikvision event: type=%s state=%s channel=%s",
            event.event_type,
            event.event_state,
            event.channel_id,
        )

        if not should_send(event):
            continue

        try:
            await telegram.send_message(format_message(event))
        except Exception:
            logger.exception("Failed to send Telegram message")


if __name__ == "__main__":
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        pass
