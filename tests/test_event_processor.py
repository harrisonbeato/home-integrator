from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest

from app.domain.events import HikvisionEvent
from app.services.event_processor import EventProcessor


class DummyDatabase:
    def save_event(self, event):
        return None


@pytest.mark.asyncio
async def test_same_event_type_same_camera_respects_cooldown() -> None:
    telegram = SimpleNamespace()
    telegram.send_photo = pytest.importorskip("unittest.mock").AsyncMock()

    processor = EventProcessor(
        username="user",
        password="pass",
        database=DummyDatabase(),
        telegram=telegram,
        target_types={"human"},
    )

    base = datetime.now(timezone.utc)
    first = HikvisionEvent(
        received_at=base,
        camera_ip="172.16.0.52",
        event_type="VMD",
        event_state="active",
        event_description="Motion detected",
        channel_id=1,
        channel_name="Camera Frente",
        target_type="human",
        target_id="42",
        raw_xml="<xml>first</xml>",
    )
    second = HikvisionEvent(
        received_at=base + timedelta(seconds=90),
        camera_ip="172.16.0.52",
        event_type="VMD",
        event_state="active",
        event_description="Motion detected",
        channel_id=1,
        channel_name="Camera Frente",
        target_type="human",
        target_id="42",
        raw_xml="<xml>second</xml>",
    )

    fake_client = SimpleNamespace()
    fake_client.get_snapshot = pytest.importorskip("unittest.mock").AsyncMock(return_value=b"image-bytes")

    await processor.process_event(first, client=fake_client)
    await processor.process_event(second, client=fake_client)

    assert telegram.send_photo.await_count == 1


@pytest.mark.asyncio
async def test_same_event_type_after_two_minutes_allows_new_alert() -> None:
    telegram = SimpleNamespace()
    telegram.send_photo = pytest.importorskip("unittest.mock").AsyncMock()

    processor = EventProcessor(
        username="user",
        password="pass",
        database=DummyDatabase(),
        telegram=telegram,
        target_types={"human"},
    )

    base = datetime.now(timezone.utc)
    first = HikvisionEvent(
        received_at=base,
        camera_ip="172.16.0.52",
        event_type="VMD",
        event_state="active",
        event_description="Motion detected",
        channel_id=1,
        channel_name="Camera Frente",
        target_type="human",
        target_id="42",
        raw_xml="<xml>first</xml>",
    )
    second = HikvisionEvent(
        received_at=base + timedelta(minutes=2, seconds=1),
        camera_ip="172.16.0.52",
        event_type="VMD",
        event_state="active",
        event_description="Motion detected",
        channel_id=1,
        channel_name="Camera Frente",
        target_type="human",
        target_id="42",
        raw_xml="<xml>second</xml>",
    )

    fake_client = SimpleNamespace()
    fake_client.get_snapshot = pytest.importorskip("unittest.mock").AsyncMock(return_value=b"image-bytes")

    await processor.process_event(first, client=fake_client)
    await processor.process_event(second, client=fake_client)

    assert telegram.send_photo.await_count == 2
