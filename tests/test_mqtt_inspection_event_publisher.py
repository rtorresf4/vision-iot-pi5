"""Unit tests for MqttInspectionEventPublisher with REV-01 and REV-02 bounded corrections."""

from __future__ import annotations

from unittest.mock import MagicMock

import paho.mqtt.client as mqtt
import pytest

from vision_iot.domain import InspectionEvent, InspectionReason, InspectionStatus
from vision_iot.infrastructure.inspection_event_serializer import (
    InspectionEventSerializationError,
    InspectionEventSerializer,
)
from vision_iot.infrastructure.mqtt_inspection_event_publisher import (
    InspectionEventPublicationError,
    MqttInspectionEventPublisher,
)


@pytest.fixture
def sample_inspection_event() -> InspectionEvent:
    return InspectionEvent(
        inspection_id="insp-001",
        frame_id="frame-001",
        timestamp=1700000000.0,
        status=InspectionStatus.INCONCLUSIVE,
        reason=InspectionReason.UNSUPPORTED_MODEL,
        evidence=(),
    )


@pytest.fixture
def mock_client() -> MagicMock:
    client = MagicMock(spec=mqtt.Client)
    client.callback_api_version = mqtt.CallbackAPIVersion.VERSION2
    client.connect.return_value = mqtt.MQTT_ERR_SUCCESS
    return client


def test_publisher_init_validation(mock_client: MagicMock) -> None:
    serializer = InspectionEventSerializer()
    # Invalid serializer type
    with pytest.raises(TypeError):
        MqttInspectionEventPublisher(
            serializer="not-a-serializer", client=mock_client, host="127.0.0.1"  # type: ignore[arg-type]
        )
    # Invalid client type
    with pytest.raises(TypeError):
        MqttInspectionEventPublisher(serializer=serializer, client="not-a-client", host="127.0.0.1")

    # REV-02: Reject VERSION1 client or missing callback_api_version
    v1_client = MagicMock(spec=mqtt.Client)
    v1_client.callback_api_version = mqtt.CallbackAPIVersion.VERSION1
    with pytest.raises(ValueError, match="CallbackAPIVersion.VERSION2"):
        MqttInspectionEventPublisher(serializer=serializer, client=v1_client, host="127.0.0.1")

    no_version_client = MagicMock(spec=mqtt.Client)
    del no_version_client.callback_api_version
    with pytest.raises(ValueError, match="CallbackAPIVersion.VERSION2"):
        MqttInspectionEventPublisher(
            serializer=serializer, client=no_version_client, host="127.0.0.1"
        )

    # REV-01: Reject DNS hostnames, accept numeric IPv4/IPv6 addresses
    with pytest.raises(ValueError, match="valid numeric IPv4 or IPv6 address"):
        MqttInspectionEventPublisher(serializer=serializer, client=mock_client, host="localhost")
    with pytest.raises(ValueError, match="valid numeric IPv4 or IPv6 address"):
        MqttInspectionEventPublisher(
            serializer=serializer, client=mock_client, host="mqtt.example.com"
        )

    # Valid numeric IPv4 and IPv6 addresses
    pub_ipv4 = MqttInspectionEventPublisher(
        serializer=serializer, client=mock_client, host="127.0.0.1"
    )
    assert pub_ipv4._host == "127.0.0.1"
    assert mock_client.connect_timeout == 5.0

    pub_ipv6 = MqttInspectionEventPublisher(
        serializer=serializer, client=mock_client, host="::1", connect_timeout=3.0
    )
    assert pub_ipv6._host == "::1"
    assert mock_client.connect_timeout == 3.0

    # Invalid port / timeouts
    with pytest.raises(ValueError):
        MqttInspectionEventPublisher(
            serializer=serializer, client=mock_client, host="127.0.0.1", port=0
        )
    with pytest.raises(ValueError):
        MqttInspectionEventPublisher(
            serializer=serializer, client=mock_client, host="127.0.0.1", connack_timeout=0
        )
    with pytest.raises(ValueError):
        MqttInspectionEventPublisher(
            serializer=serializer, client=mock_client, host="127.0.0.1", puback_timeout=-1.0
        )
    with pytest.raises(ValueError):
        MqttInspectionEventPublisher(
            serializer=serializer, client=mock_client, host="127.0.0.1", connect_timeout=0.0
        )


def test_publisher_connect_success(mock_client: MagicMock) -> None:
    serializer = InspectionEventSerializer()
    publisher = MqttInspectionEventPublisher(
        serializer=serializer,
        client=mock_client,
        host="192.168.1.100",
        port=1883,
        connack_timeout=1.0,
    )

    def side_effect_connect(*args, **kwargs):
        # Simulate background on_connect call with rc=0 (accepted)
        if publisher._client.on_connect:
            publisher._client.on_connect(mock_client, None, None, 0)
        return mqtt.MQTT_ERR_SUCCESS

    mock_client.connect.side_effect = side_effect_connect

    publisher.connect()
    mock_client.loop_start.assert_called_once()
    mock_client.connect.assert_called_once_with("192.168.1.100", 1883, 60)

    # Closing
    publisher.close()
    mock_client.disconnect.assert_called_once()
    mock_client.loop_stop.assert_called_once()


def test_publisher_connect_rejected(mock_client: MagicMock) -> None:
    serializer = InspectionEventSerializer()
    publisher = MqttInspectionEventPublisher(
        serializer=serializer,
        client=mock_client,
        host="127.0.0.1",
        connack_timeout=0.5,
    )

    def side_effect_connect(*args, **kwargs):
        # Simulate CONNACK refused (rc=5 not authorized)
        if publisher._client.on_connect:
            publisher._client.on_connect(mock_client, None, None, 5)
        return mqtt.MQTT_ERR_SUCCESS

    mock_client.connect.side_effect = side_effect_connect

    with pytest.raises(InspectionEventPublicationError, match="CONNACK return code: 5"):
        publisher.connect()

    mock_client.loop_stop.assert_called()


def test_publisher_connect_timeout(mock_client: MagicMock) -> None:
    serializer = InspectionEventSerializer()
    publisher = MqttInspectionEventPublisher(
        serializer=serializer,
        client=mock_client,
        host="127.0.0.1",
        connack_timeout=0.1,
    )

    # Do not invoke on_connect, causing timeout
    with pytest.raises(InspectionEventPublicationError, match="timed out"):
        publisher.connect()

    mock_client.loop_stop.assert_called()


def test_publisher_publish_before_connect(
    mock_client: MagicMock, sample_inspection_event: InspectionEvent
) -> None:
    serializer = InspectionEventSerializer()
    publisher = MqttInspectionEventPublisher(
        serializer=serializer,
        client=mock_client,
        host="127.0.0.1",
    )

    with pytest.raises(InspectionEventPublicationError, match="not connected"):
        publisher.publish(sample_inspection_event)


def test_publisher_publish_success(
    mock_client: MagicMock, sample_inspection_event: InspectionEvent
) -> None:
    serializer = InspectionEventSerializer()
    publisher = MqttInspectionEventPublisher(
        serializer=serializer,
        client=mock_client,
        host="127.0.0.1",
        connack_timeout=1.0,
        puback_timeout=1.0,
    )

    def side_effect_connect(*args, **kwargs):
        if publisher._client.on_connect:
            publisher._client.on_connect(mock_client, None, None, 0)
        return mqtt.MQTT_ERR_SUCCESS

    mock_client.connect.side_effect = side_effect_connect

    # Mock publish return info
    msg_info = mqtt.MQTTMessageInfo(1)
    msg_info.rc = mqtt.MQTT_ERR_SUCCESS

    # Simulate async publish completion
    def mock_publish(topic, payload, qos, retain):
        assert topic == "factory/line1/inspection/events"
        assert qos == 1
        assert retain is False
        # Set as published (PUBACK received)
        msg_info._set_as_published()
        return msg_info

    mock_client.publish.side_effect = mock_publish

    publisher.connect()
    publisher.publish(sample_inspection_event)

    mock_client.publish.assert_called_once()
    publisher.close()


def test_publisher_publish_rejection(
    mock_client: MagicMock, sample_inspection_event: InspectionEvent
) -> None:
    serializer = InspectionEventSerializer()
    publisher = MqttInspectionEventPublisher(
        serializer=serializer,
        client=mock_client,
        host="127.0.0.1",
        connack_timeout=1.0,
    )

    def side_effect_connect(*args, **kwargs):
        if publisher._client.on_connect:
            publisher._client.on_connect(mock_client, None, None, 0)
        return mqtt.MQTT_ERR_SUCCESS

    mock_client.connect.side_effect = side_effect_connect

    msg_info = mqtt.MQTTMessageInfo(1)
    msg_info.rc = mqtt.MQTT_ERR_QUEUE_SIZE
    mock_client.publish.return_value = msg_info

    publisher.connect()

    with pytest.raises(
        InspectionEventPublicationError, match="submission failed|transmission failed"
    ):
        publisher.publish(sample_inspection_event)


def test_publisher_publish_timeout(
    mock_client: MagicMock, sample_inspection_event: InspectionEvent
) -> None:
    serializer = InspectionEventSerializer()
    publisher = MqttInspectionEventPublisher(
        serializer=serializer,
        client=mock_client,
        host="127.0.0.1",
        connack_timeout=1.0,
        puback_timeout=0.1,
    )

    def side_effect_connect(*args, **kwargs):
        if publisher._client.on_connect:
            publisher._client.on_connect(mock_client, None, None, 0)
        return mqtt.MQTT_ERR_SUCCESS

    mock_client.connect.side_effect = side_effect_connect

    msg_info = mqtt.MQTTMessageInfo(1)
    msg_info.rc = mqtt.MQTT_ERR_SUCCESS
    # Do not set as published, forcing timeout waiting for PUBACK
    mock_client.publish.return_value = msg_info

    publisher.connect()

    with pytest.raises(InspectionEventPublicationError, match="timed out"):
        publisher.publish(sample_inspection_event)


def test_publisher_serialization_error(mock_client: MagicMock) -> None:
    serializer = InspectionEventSerializer()
    publisher = MqttInspectionEventPublisher(
        serializer=serializer,
        client=mock_client,
        host="127.0.0.1",
        connack_timeout=1.0,
    )

    def side_effect_connect(*args, **kwargs):
        if publisher._client.on_connect:
            publisher._client.on_connect(mock_client, None, None, 0)
        return mqtt.MQTT_ERR_SUCCESS

    mock_client.connect.side_effect = side_effect_connect
    publisher.connect()

    # Invalid event missing required fields or invalid type
    invalid_event = "not-an-inspection-event"

    with pytest.raises(InspectionEventSerializationError):
        publisher.publish(invalid_event)  # type: ignore[arg-type]
