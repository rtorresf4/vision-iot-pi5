#!/usr/bin/env bash
set -e
sudo apt update && sudo apt install -y git python3-venv python3-pip cmake ffmpeg mosquitto mosquitto-clients
python3 -m venv ~/vision
source ~/vision/bin/activate
pip install --upgrade pip wheel
pip install -r requirements.txt
