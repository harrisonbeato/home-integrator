import sqlite3
from pathlib import Path


class Database:
    def __init__(self, path: str):
        self.path = path
        Path(path).parent.mkdir(parents=True, exist_ok=True)

    def initialize(self) -> None:
        with sqlite3.connect(self.path) as connection:
            connection.execute(
                '''
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    received_at TEXT NOT NULL,
                    event_type TEXT,
                    event_state TEXT,
                    channel_id INTEGER,
                    payload TEXT NOT NULL
                )
                '''
            )
            connection.commit()

    def save_event(
        self,
        received_at: str,
        event_type: str | None,
        event_state: str | None,
        channel_id: int | None,
        payload: str,
    ) -> None:
        with sqlite3.connect(self.path) as connection:
            connection.execute(
                '''
                INSERT INTO events (
                    received_at,
                    event_type,
                    event_state,
                    channel_id,
                    payload
                )
                VALUES (?, ?, ?, ?, ?)
                ''',
                (
                    received_at,
                    event_type,
                    event_state,
                    channel_id,
                    payload,
                ),
            )
            connection.commit()
