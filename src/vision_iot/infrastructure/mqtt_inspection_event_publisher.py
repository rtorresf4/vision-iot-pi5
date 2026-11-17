"""Deterministic synchronous MQTT inspection event publisher implementation."""

from __future__ import annotations

import ipaddress
import threading
from contextlib import suppress
from typing import Any
from uuid import uuid4

import paho.mqtt.client as mqtt

from vision_iot.domain import InspectionEvent
from vision_iot.infrastructure.inspection_event_serializer import (
    InspectionEventSerializationError,
    InspectionEventSerializer,
)


class InspectionEventPublicationError(Exception):
    """Raised when an MQTT connection or publication operation fails."""

    pass


class MqttInspectionEventPublisher:
    """Publishes InspectionEvents via MQTT with QoS 1, confirmed CONNACK and PUBACK."""

    def __init__(
        self,
        serializer: InspectionEventSerializer,
        client: mqtt.Client,
        host: str,
        port: int = 1883,
        keepalive: int = 60,
        connack_timeout: float = 5.0,
        puback_timeout: float = 5.0,
        connect_timeout: float = 5.0,
    ) -> None:
        if not isinstance(serializer, InspectionEventSerializer):
            raise TypeError("Expected InspectionEventSerializer instance")
        if not isinstance(client, mqtt.Client):
            raise TypeError("Expected paho.mqtt.client.Client instance")

        # REV-02: Strict Paho Callback API Version 2 validation on injected client before registering callbacks
        if (
            not hasattr(client, "callback_api_version")
            or client.callback_api_version != mqtt.CallbackAPIVersion.VERSION2
        ):
            raise ValueError(
                "Expected Paho MQTT client configured with CallbackAPIVersion.VERSION2"
            )

        # REV-01: Numeric IPv4 or IPv6 address validation (rejecting DNS hostnames)
        if not isinstance(host, str):
            raise TypeError("Host must be a string")
        try:
            ipaddress.ip_address(host)
        except ValueError as e:
            raise ValueError(
                f"Host must be a valid numeric IPv4 or IPv6 address, got: {host}"
            ) from e

        if not isinstance(port, int) or port <= 0:
            raise ValueError("Port must be a positive integer")
        if not isinstance(keepalive, int) or keepalive < 0:
            raise ValueError("Keepalive must be a non-negative integer")
        if not isinstance(connack_timeout, int | float) or connack_timeout <= 0:
            raise ValueError("connack_timeout must be a positive number")
        if not isinstance(puback_timeout, int | float) or puback_timeout <= 0:
            raise ValueError("puback_timeout must be a positive number")
        if not isinstance(connect_timeout, int | float) or connect_timeout <= 0:
            raise ValueError("connect_timeout must be a positive number")

        self._serializer = serializer
        self._client = client
        self._host = host
        self._port = port
        self._keepalive = keepalive
        self._connack_timeout = float(connack_timeout)
        self._puback_timeout = float(puback_timeout)
        self._connect_timeout = float(connect_timeout)

        # Set public connection timeout for bounded TCP establishment (REV-01)
        self._client.connect_timeout = self._connect_timeout

        self._lock = threading.Lock()
        self._connected = False
        self._connack_event = threading.Event()
        self._connack_rc: int | None = None

        # Configure callbacks on the client after validation
        self._client.on_connect = self._on_connect
        self._client.on_disconnect = self._on_disconnect
        self._client.on_publish = self._on_publish

    def connect(self) -> None:
        """Connect to the MQTT broker and block until CONNACK is received and accepted."""
        with self._lock:
            if self._connected:
                return

            self._connack_event.clear()
            self._connack_rc = None

            try:
                self._client.loop_start()
            except Exception as e:
                raise InspectionEventPublicationError(
                    f"Failed to start MQTT network loop: {e}"
                ) from e

            try:
                result = self._client.connect(self._host, self._port, self._keepalive)
                if result != mqtt.MQTT_ERR_SUCCESS:
                    self._client.loop_stop()
                    raise InspectionEventPublicationError(
                        f"MQTT connect request failed with error code {result}"
                    )
            except Exception as e:
                with suppress(Exception):
                    self._client.loop_stop()
                if isinstance(e, InspectionEventPublicationError):
                    raise
                raise InspectionEventPublicationError(
                    f"Failed to connect to MQTT broker: {e}"
                ) from e

            if not self._connack_event.wait(timeout=self._connack_timeout):
                with suppress(Exception):
                    self._client.loop_stop()
                raise InspectionEventPublicationError(
                    f"MQTT connection timed out after {self._connack_timeout} seconds waiting for CONNACK"
                )

            if self._connack_rc is None or self._connack_rc != 0:
                with suppress(Exception):
                    self._client.loop_stop()
                rc_val = self._connack_rc
                raise InspectionEventPublicationError(
                    f"MQTT connection refused by broker with CONNACK return code: {rc_val}"
                )

            self._connected = True

    def publish(self, event: InspectionEvent) -> None:
        """Serialize and publish an InspectionEvent with QoS 1, requiring confirmed PUBACK."""
        with self._lock:
            if not self._connected:
                raise InspectionEventPublicationError(
                    "Cannot publish when not connected to MQTT broker"
                )

            event_id = uuid4()

            try:
                payload = self._serializer.serialize(event, event_id=event_id)
            except InspectionEventSerializationError:
                raise
            except Exception as e:
                raise InspectionEventSerializationError(
                    f"Unexpected serialization failure: {e}"
                ) from e

            try:
                info = self._client.publish(
                    topic="factory/line1/inspection/events",
                    payload=payload,
                    qos=1,
                    retain=False,
                )
            except Exception as e:
                raise InspectionEventPublicationError(
                    f"Failed to submit MQTT publication: {e}"
                ) from e

            if info.rc != mqtt.MQTT_ERR_SUCCESS:
                raise InspectionEventPublicationError(
                    f"MQTT publish submission failed with error code {info.rc}"
                )

            try:
                info.wait_for_publish(timeout=self._puback_timeout)
            except (ValueError, RuntimeError) as e:
                raise InspectionEventPublicationError(
                    f"MQTT publication transmission failed: {e}"
                ) from e

            if not info.is_published():
                raise InspectionEventPublicationError(
                    f"MQTT publication timed out after {self._puback_timeout} seconds waiting for PUBACK"
                )

    def close(self) -> None:
        """Disconnect from the broker and stop the network loop."""
        with self._lock:
            with suppress(Exception):
                self._client.disconnect()

            with suppress(Exception):
                self._client.loop_stop()

            self._connected = False

    def _on_connect(
        self,
        client: mqtt.Client,
        userdata: Any,
        flags: Any,
        reason_code: Any,
        properties: Any = None,
    ) -> None:
        rc = int(reason_code) if hasattr(reason_code, "__int__") else reason_code
        self._connack_rc = rc
        self._connack_event.set()

    def _on_disconnect(
        self,
        client: mqtt.Client,
        userdata: Any,
        flags: Any,
        reason_code: Any = None,
        properties: Any = None,
    ) -> None:
        with self._lock:
            self._connected = False

    def _on_publish(
        self,
        client: mqtt.Client,
        userdata: Any,
        mid: int,
        reason_code: Any = None,
        properties: Any = None,
    ) -> None:
        pass
