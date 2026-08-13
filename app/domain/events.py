from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class HikvisionEvent:
    received_at: datetime
    camera_ip: str
    event_type: str | None
    event_state: str | None
    event_description: str | None
    channel_id: int | None
    channel_name: str | None
    target_type: str | None
    target_id: str | None
    raw_xml: str
