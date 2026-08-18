import shutil
import sqlite3
from pathlib import Path

from app.domain.events import HikvisionEvent


class Database:
    def __init__(
        self,
        path: str,
        rotation_max_mb: int = 50,
        rotation_keep: int = 3,
    ):
        self.path = path
        self.rotation_max_bytes = max(0, rotation_max_mb) * 1024 * 1024
        self.rotation_keep = max(1, rotation_keep)

        Path(path).parent.mkdir(
            parents=True,
            exist_ok=True,
        )

    def _can_rotate(self) -> bool:
        database_file = Path(self.path)
        if not database_file.exists():
            return True

        try:
            with sqlite3.connect(self.path) as connection:
                connection.execute("BEGIN IMMEDIATE")
                connection.execute("ROLLBACK")
                return True
        except sqlite3.DatabaseError:
            return False

    def _rotate_if_needed(self) -> None:
        if self.rotation_max_bytes <= 0:
            return

        database_file = Path(self.path)
        if not database_file.exists():
            return

        if database_file.stat().st_size <= self.rotation_max_bytes:
            return

        if not self._can_rotate():
            return

        for index in range(self.rotation_keep, 0, -1):
            archive_path = database_file.with_name(f"{database_file.name}.{index}")
            next_archive_path = database_file.with_name(f"{database_file.name}.{index + 1}")

            if index == self.rotation_keep:
                if archive_path.exists():
                    archive_path.unlink()
                continue

            if archive_path.exists():
                archive_path.replace(next_archive_path)

        rotated_path = database_file.with_name(f"{database_file.name}.1")
        try:
            shutil.copy2(database_file, rotated_path)
        except OSError:
            return

        try:
            database_file.unlink()
        except OSError:
            return

    def initialize(self) -> None:
        self._rotate_if_needed()

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
        self._rotate_if_needed()

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
