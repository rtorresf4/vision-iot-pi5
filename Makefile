SHELL := /bin/bash

.PHONY: setup dev lint test run-detector run-dashboard precommit \
	check-camera capture-ok capture-defect sim-detections

setup:
	python -m pip install --upgrade pip
	pip install -r requirements.txt

dev:
	pip install -r requirements-dev.txt
	pre-commit install

lint:
	black --check .
	ruff check .
	mypy apps || true

test:
	pytest -q

run-detector:
	python apps/pi_detector/main.py

run-dashboard:
	streamlit run apps/streamlit_dashboard/Home.py

precommit:
	pre-commit run -a

# --- Utilities for local development ---

check-camera:
	python apps/tools/check_camera.py --probe-res --fourcc MJPG

capture-ok:
	python apps/tools/capture_dataset.py --label ok --show --max 20

capture-defect:
	python apps/tools/capture_dataset.py --label defect --every 5 --show --max 20

# Publish synthetic detections to MQTT (localhost:1883). Stop with Ctrl+C.
sim-detections:
	python - <<'PY'
	import time, json, random as r
	import paho.mqtt.client as m
	c = m.Client('sim')
	c.connect('localhost', 1883, 60)
	c.loop_start()
	i = 0
	try:
	    while True:
	        payload = {
	            'fps': round(r.uniform(10, 20), 1),
	            'pieces_ok': i,
	            'pieces_ng': i // 7,
	        }
	        c.publish('factory/line1/detections', json.dumps(payload))
	        i += 1
	        time.sleep(1)
	except KeyboardInterrupt:
	    pass
	PY
