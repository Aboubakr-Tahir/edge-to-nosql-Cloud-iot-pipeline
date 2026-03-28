import streamlit as st
import pandas as pd
from confluent_kafka import Consumer, KafkaError
import json
import time
import os


kafka_server = os.getenv('KAFKA_BOOTSTRAP', 'localhost:9092')


KAFKA_CONF = {
    'bootstrap.servers': kafka_server,
    'group.id': 'streamlit-live-dashboard', 
    'auto.offset.reset': 'latest'          
}
TOPIC = 'test-iot'


st.set_page_config(page_title="Kafka Live Dashboard", layout="wide")
st.title("🚀 Flux Temps Réel (Direct Kafka)")


if 'data_buffer' not in st.session_state:
    st.session_state.data_buffer = pd.DataFrame(columns=[
        'timestamp', 'device_id', 'cpu_usage_percent', 'ram_available_mb', 'temperature_c'
    ])


@st.cache_resource
def get_kafka_consumer():
    consumer = Consumer(KAFKA_CONF)
    consumer.subscribe([TOPIC])
    return consumer

consumer = get_kafka_consumer()


col1, col2, col3 = st.columns(3)
cpu_metric = col1.empty()
ram_metric = col2.empty()
temp_metric = col3.empty()

chart_cpu = st.empty()
chart_temp = st.empty()
data_table = st.empty()


while True:
    msg = consumer.poll(0.5) 

    if msg is not None and not msg.error():
        try:
            
            new_data = json.loads(msg.value().decode('utf-8'))
            new_row = pd.DataFrame([new_data])

            
            st.session_state.data_buffer = pd.concat([st.session_state.data_buffer, new_row]).tail(50)
            df = st.session_state.data_buffer

            
            cpu_metric.metric("CPU Live", f"{new_data['cpu_usage_percent']}%")
            ram_metric.metric("RAM Live", f"{new_data['ram_available_mb']} MB")
            temp_metric.metric("Température", f"{new_data['temperature_c']}°C")

            
            with chart_cpu.container():
                st.subheader("CPU en direct")
                st.line_chart(df.set_index('timestamp')['cpu_usage_percent'])

            with chart_temp.container():
                st.subheader("Température en direct")
                st.line_chart(df.set_index('timestamp')['temperature_c'])

            with data_table.container():
                st.dataframe(df.sort_values('timestamp', ascending=False), use_container_width=True)

        except Exception as e:
            st.error(f"Erreur de parsing : {e}")
    
    
    time.sleep(0.1)
