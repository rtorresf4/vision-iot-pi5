import streamlit as st, json, queue
from paho.mqtt.client import Client

st.set_page_config(page_title='Vision + IoT', layout='wide')
msg_q = queue.Queue(maxsize=200)

col_fps, col_ok, col_ng = st.columns(3)

def on_msg(cli, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        msg_q.put_nowait(data)
    except Exception:
        pass

@st.cache_resource
def mqtt_client():
    c = Client('dashboard')
    c.on_message = on_msg
    c.connect('localhost', 1883, 60)
    c.subscribe('factory/line1/detections')
    c.loop_start()
    return c

mqtt_client()
st.write('Listening on MQTT topic `factory/line1/detections`...')

while True:
    try:
        data = msg_q.get(timeout=1)
        col_fps.metric('FPS', f"{data.get('fps',0):.1f}")
        col_ok.metric('OK', data.get('pieces_ok',0))
        col_ng.metric('DEFECT', data.get('pieces_ng',0))
        st.experimental_rerun()
    except Exception:
        st.stop()
