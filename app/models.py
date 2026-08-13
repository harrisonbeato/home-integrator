from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class HikvisionEvent:
    received_at: datetime
    event_type: str | None
    event_state: str | None
    channel_id: int | None
    raw_xml: str
