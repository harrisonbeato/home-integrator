import xml.etree.ElementTree as ET
from datetime import datetime, timezone

from app.domain.events import HikvisionEvent


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def find_text(
    root: ET.Element,
    name: str,
) -> str | None:

    for element in root.iter():

        if local_name(element.tag) == name:

            return (
                element.text.strip()
                if element.text
                else None
            )

    return None


def parse_event(
    xml: str,
    camera_ip: str,
) -> HikvisionEvent:

    root = ET.fromstring(xml)

    event_type = find_text(
        root,
        "eventType",
    )

    event_state = find_text(
        root,
        "eventState",
    )

    event_description = find_text(
        root,
        "eventDescription",
    )

    channel_text = find_text(
        root,
        "channelID",
    )

    try:
        channel_id = (
            int(channel_text)
            if channel_text
            else None
        )

    except ValueError:
        channel_id = None

    channel_name = find_text(
        root,
        "channelName",
    )

    target_type = find_text(
        root,
        "targetType",
    )

    target_id = find_text(
        root,
        "targetID",
    )

    return HikvisionEvent(
        received_at=datetime.now(timezone.utc),
        camera_ip=camera_ip,
        event_type=event_type,
        event_state=event_state,
        event_description=event_description,
        channel_id=channel_id,
        channel_name=channel_name,
        target_type=(
            target_type.lower()
            if target_type
            else None
        ),
        target_id=target_id,
        raw_xml=xml,
    )


def extract_xml_documents(
    buffer: str,
) -> tuple[list[str], str]:

    documents = []

    closing_tag = "</EventNotificationAlert>"

    while closing_tag in buffer:

        end = (
            buffer.index(closing_tag)
            + len(closing_tag)
        )

        starts = [
            index
            for index in (
                buffer.find("<?xml"),
                buffer.find(
                    "<EventNotificationAlert"
                ),
            )
            if index >= 0
        ]

        if not starts:
            buffer = buffer[end:]
            continue

        start = min(starts)

        documents.append(
            buffer[start:end]
        )

        buffer = buffer[end:]

    return documents, buffer
