FROM python:3.10-slim

WORKDIR /app


RUN apt-get update && apt-get install -y gcc librdkafka-dev && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


COPY dashboard/dashboard.py .


ENV KAFKA_BOOTSTRAP="kafka-broker:29092"


EXPOSE 8501


CMD ["streamlit", "run", "dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"]