import xml.etree.ElementTree as ET
from datetime import datetime, timezone

from app.models import HikvisionEvent


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def find_text(root: ET.Element, name: str) -> str | None:
    for element in root.iter():
        if local_name(element.tag) == name:
            return element.text.strip() if element.text else None
    return None


def parse_event(xml: str) -> HikvisionEvent:
    root = ET.fromstring(xml)

    event_type = find_text(root, "eventType")
    event_state = find_text(root, "eventState")
    channel_text = find_text(root, "channelID")

    try:
        channel_id = int(channel_text) if channel_text else None
    except ValueError:
        channel_id = None

    return HikvisionEvent(
        received_at=datetime.now(timezone.utc),
        event_type=event_type,
        event_state=event_state,
        channel_id=channel_id,
        raw_xml=xml,
    )


def extract_xml_documents(buffer: str) -> tuple[list[str], str]:
    documents: list[str] = []
    closing_tag = "</EventNotificationAlert>"

    while closing_tag in buffer:
        end = buffer.index(closing_tag) + len(closing_tag)

        starts = [
            index
            for index in (
                buffer.find("<?xml"),
                buffer.find("<EventNotificationAlert"),
            )
            if index >= 0
        ]

        if not starts:
            buffer = buffer[end:]
            continue

        start = min(starts)
        documents.append(buffer[start:end])
        buffer = buffer[end:]

    return documents, buffer
