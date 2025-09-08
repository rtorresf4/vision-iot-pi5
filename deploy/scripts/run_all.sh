#!/usr/bin/env bash
set -e
source ~/vision/bin/activate
python apps/pi_detector/main.py &
streamlit run apps/streamlit_dashboard/Home.py
