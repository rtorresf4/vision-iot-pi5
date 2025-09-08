from __future__ import annotations

import json
import logging
import time
from typing import Any, Callable, Optional

import paho.mqtt.client as mqtt


class MqttClient:
    def __init__(
        self,
        host: str,
        port: int,
        client_id: str,
        keepalive: int = 60,
        qos: int = 0,
        base_topic: str = "factory/line1",
        on_connected: Optional[Callable[[], None]] = None,
    ) -> None:
        self.host = host
        self.port = port
        self.keepalive = keepalive
        self.qos = qos
        self.base_topic = base_topic.rstrip("/")
        self.connected = False

        self.cli = mqtt.Client(client_id=client_id, clean_session=True)
        self.cli.will_set(f"{self.base_topic}/status", json.dumps({"state": "lost"}), qos=1, retain=True)

        def _on_connect(cli, userdata, flags, rc):
            self.connected = rc == 0
            if self.connected:
                logging.info("MQTT connected rc=%s", rc)
                self.publish("status", {"state": "online", "ts": time.time()}, retain=True, qos=1)
                if on_connected:
                    on_connected()
            else:
                logging.error("MQTT connection failed rc=%s", rc)

        def _on_disconnect(cli, userdata, rc):
            self.connected = False
            logging.warning("MQTT disconnected rc=%s", rc)

        self.cli.on_connect = _on_connect
        self.cli.on_disconnect = _on_disconnect

    def connect_and_loop(self) -> None:
        backoff = 1.0
        while True:
            try:
                self.cli.connect(self.host, self.port, self.keepalive)
                self.cli.loop_start()
                return
            except Exception as e:
                logging.error("MQTT connect error: %s", e)
                time.sleep(backoff)
                backoff = min(backoff * 2.0, 30.0)

    def publish(self, suffix: str, payload: dict[str, Any], retain: bool = False, qos: Optional[int] = None) -> None:
        topic = f"{self.base_topic}/{suffix}"
        msg = json.dumps(payload, ensure_ascii=False)
        self.cli.publish(topic, msg, qos=self.qos if qos is None else qos, retain=retain)
