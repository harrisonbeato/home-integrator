import sqlite3
from pathlib import Path

from app.domain.events import HikvisionEvent


class Database:
    def __init__(self, path: str):
        self.path = path

        Path(path).parent.mkdir(
            parents=True,
            exist_ok=True,
        )

    def initialize(self) -> None:
        with sqlite3.connect(self.path) as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    received_at TEXT NOT NULL,
                    camera_ip TEXT NOT NULL,
                    event_type TEXT,
                    event_state TEXT,
                    event_description TEXT,
                    channel_id INTEGER,
                    channel_name TEXT,
                    target_type TEXT,
                    target_id TEXT,
                    payload TEXT NOT NULL
                )
                """
            )

            connection.commit()

    def save_event(
        self,
        event: HikvisionEvent,
    ) -> None:
        with sqlite3.connect(self.path) as connection:
            connection.execute(
                """
                INSERT INTO events (
                    received_at,
                    camera_ip,
                    event_type,
                    event_state,
                    event_description,
                    channel_id,
                    channel_name,
                    target_type,
                    target_id,
                    payload
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event.received_at.isoformat(),
                    event.camera_ip,
                    event.event_type,
                    event.event_state,
                    event.event_description,
                    event.channel_id,
                    event.channel_name,
                    event.target_type,
                    event.target_id,
                    event.raw_xml,
                ),
            )

            connection.commit()
