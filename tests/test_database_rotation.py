import sqlite3
from datetime import datetime, timezone

from app.domain.events import HikvisionEvent
from app.infrastructure.database import Database


def test_database_rotates_when_exceeds_limit(tmp_path) -> None:
    db_path = tmp_path / "home_integrator.db"
    database = Database(
        str(db_path),
        rotation_max_mb=1,
        rotation_keep=2,
    )
    database.initialize()

    large_payload = "x" * (1024 * 1024 + 500)
    with sqlite3.connect(str(db_path)) as connection:
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
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                datetime.now(timezone.utc).isoformat(),
                "172.16.0.52",
                "VMD",
                "active",
                "Motion alarm",
                1,
                "Camera Frente",
                "human",
                "42",
                large_payload,
            ),
        )
        connection.commit()

    event = HikvisionEvent(
        received_at=datetime.now(timezone.utc),
        camera_ip="172.16.0.53",
        event_type="VMD",
        event_state="active",
        event_description="Motion alarm",
        channel_id=2,
        channel_name="Camera Fundo",
        target_type="human",
        target_id="99",
        raw_xml="<xml>new event</xml>",
    )

    database.save_event(event)

    assert db_path.exists()
    assert (tmp_path / "home_integrator.db.1").exists()
