FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y gcc librdkafka-dev && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY processors/kafka_to_cassandra.py .

ENV KAFKA_BOOTSTRAP="kafka-broker:29092"
ENV CASSANDRA_HOST="cassandra-db"

CMD ["python", "-u", "kafka_to_cassandra.py"]