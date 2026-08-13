from app.integrations.hikvision.parser import parse_event


def test_parse_vehicle_event() -> None:
    xml = """
    <EventNotificationAlert
        xmlns="http://www.hikvision.com/ver20/XMLSchema"
    >
        <eventType>VMD</eventType>
        <eventState>active</eventState>
        <eventDescription>Motion alarm</eventDescription>
        <channelID>1</channelID>
        <channelName>Camera Frente</channelName>
        <targetType>vehicle</targetType>
        <targetInfo>
            <targetID>1</targetID>
        </targetInfo>
    </EventNotificationAlert>
    """

    event = parse_event(
        xml,
        "172.16.0.52",
    )

    assert event.camera_ip == "172.16.0.52"
    assert event.event_type == "VMD"
    assert event.event_state == "active"
    assert event.channel_name == "Camera Frente"
    assert event.target_type == "vehicle"
    assert event.target_id == "1"
