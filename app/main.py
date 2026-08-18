import asyncio
import logging

from app.config import get_settings
from app.infrastructure.database import Database
from app.integrations.telegram.client import TelegramClient
from app.services.event_processor import EventProcessor


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


async def run() -> None:
    settings = get_settings()

    configure_logging(
        settings.log_level
    )

    logger = logging.getLogger(
        __name__
    )

    database = Database(
        settings.database_path,
        rotation_max_mb=settings.database_rotation_max_mb,
        rotation_keep=settings.database_rotation_keep,
    )

    database.initialize()

    telegram = TelegramClient(
        token=settings.telegram_bot_token,
        chat_id=settings.telegram_chat_id,
    )

    processor = EventProcessor(
        username=settings.hikvision_username,
        password=settings.hikvision_password,
        database=database,
        telegram=telegram,
        target_types=settings.target_types,
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

    tasks = [
        asyncio.create_task(
            processor.monitor_camera(
                camera_ip=camera_ip,
            )
        )
        for camera_ip in settings.cameras
    ]

    await asyncio.gather(
        *tasks
    )


if __name__ == "__main__":
    try:
        asyncio.run(run())

    except KeyboardInterrupt:
        pass
