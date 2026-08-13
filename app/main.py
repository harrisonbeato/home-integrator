import asyncio
import logging
from zoneinfo import ZoneInfo

from app.config import get_settings
from app.database import Database
from app.hikvision.client import HikvisionClient
from app.models import HikvisionEvent
from app.telegram.client import TelegramClient


def configure_logging(level: str) -> None:

    logging.basicConfig(
        level=getattr(
            logging,
            level.upper(),
            logging.INFO,
        ),
        format=(
            "%(asctime)s "
            "%(levelname)s "
            "%(name)s - "
            "%(message)s"
        ),
    )


def is_relevant_event(
    event: HikvisionEvent,
) -> bool:

    settings = get_settings()

    if event.event_state != "active":
        return False

    if not event.target_type:
        return False

    return (
        event.target_type
        in settings.target_types
    )


def target_description(
    target_type: str | None,
) -> str:

    if target_type == "human":
        return "Pessoa detectada"

    if target_type == "vehicle":
        return "Veículo detectado"

    return "Alvo detectado"


def format_message(
    event: HikvisionEvent,
) -> str:

    timestamp = (
        event.received_at
        .astimezone(
            ZoneInfo("America/Sao_Paulo")
        )
        .strftime("%d/%m/%Y %H:%M:%S")
    )

    description = target_description(
        event.target_type
    )

    camera_name = (
        event.channel_name
        or "Câmera sem nome"
    )

    return (
        "🚨 Home Integrator\n"
        "\n"
        f"{description}\n"
        "\n"
        f"Câmera: {camera_name}\n"
        f"IP: {event.camera_ip}\n"
        f"Canal: {event.channel_id or '-'}\n"
        f"Horário: {timestamp}"
    )


async def monitor_camera(
    camera_ip: str,
    username: str,
    password: str,
    database: Database,
    telegram: TelegramClient,
) -> None:

    logger = logging.getLogger(
        f"camera.{camera_ip}"
    )

    client = HikvisionClient(
        host=camera_ip,
        username=username,
        password=password,
    )

    async for event in client.events():

        database.save_event(event)

        logger.debug(
            "[%s] Event: "
            "type=%s state=%s target=%s",
            camera_ip,
            event.event_type,
            event.event_state,
            event.target_type,
        )

        if not is_relevant_event(event):
            continue

        logger.info(
            "[%s] Relevant event: "
            "target=%s camera=%s",
            camera_ip,
            event.target_type,
            event.channel_name,
        )

        try:

            photo = await client.get_snapshot()

            await telegram.send_photo(
                photo=photo,
                caption=format_message(event),
            )

            logger.info(
                "[%s] Telegram notification with "
                "snapshot sent",
                camera_ip,
            )

        except Exception:

            logger.exception(
                "[%s] Failed to send Telegram "
                "notification with snapshot",
                camera_ip,
            )


async def run() -> None:

    settings = get_settings()

    configure_logging(
        settings.log_level
    )

    logger = logging.getLogger(
        __name__
    )

    database = Database(
        settings.database_path
    )

    database.initialize()

    telegram = TelegramClient(
        token=settings.telegram_bot_token,
        chat_id=settings.telegram_chat_id,
    )

    logger.info(
        "Home Integrator started"
    )

    logger.info(
        "Cameras: %s",
        ", ".join(settings.cameras),
    )

    logger.info(
        "Allowed targets: %s",
        ", ".join(settings.target_types),
    )

    tasks = []

    for camera_ip in settings.cameras:

        task = asyncio.create_task(
            monitor_camera(
                camera_ip=camera_ip,
                username=settings.hikvision_username,
                password=settings.hikvision_password,
                database=database,
                telegram=telegram,
            )
        )

        tasks.append(task)

    await asyncio.gather(
        *tasks
    )


if __name__ == "__main__":

    try:
        asyncio.run(run())

    except KeyboardInterrupt:
        pass