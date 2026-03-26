# Real-Time Edge-to-NoSQL IoT Pipeline

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2CA5E0?style=for-the-badge&logo=docker&logoColor=white)
![Apache NiFi](https://img.shields.io/badge/Apache%20NiFi-72B258?style=for-the-badge&logo=apache&logoColor=white)
![Apache Kafka](https://img.shields.io/badge/Apache%20Kafka-231F20?style=for-the-badge&logo=apachekafka&logoColor=white)
![Apache Cassandra](https://img.shields.io/badge/cassandra-%231287B1.svg?style=for-the-badge&logo=apache-cassandra&logoColor=white)
![Tailscale](https://img.shields.io/badge/Tailscale-FFFFFF?style=for-the-badge&logo=tailscale&logoColor=383939)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)

## 📌 Overview
The **Real-Time Edge-to-NoSQL IoT Pipeline** is an end-to-end data engineering architecture designed specifically for Edge Computing. It demonstrates a highly resilient, low-latency stream processing pipeline that securely ingests high-velocity hardware telemetry data from a remote edge device into a robust distributed storage and visualization layer.

This project serves as a comprehensive Data Engineering portfolio piece, highlighting expertise in zero-trust networking, stream buffering, event-driven architecture, and NoSQL data modeling.

## 🏗️ Architecture

The pipeline processes real-time metrics (CPU usage, RAM availability, and Temperature) at 0.5-second intervals. The data flow is structured as follows:

1. **Edge Device (Hardware):** A Debian 13 edge node runs a Python telemetry agent (`edge/edge_agent.py`), capturing hardware metrics and transmitting them as JSON payloads via HTTP POST.
2. **Secure Network Layer:** **Tailscale VPN** guarantees a secure, zero-trust overlay network between the edge device and the centralized ingestion server.
3. **Ingestion Layer:** **Apache NiFi** serves as the central data gateway. It receives the HTTP requests, routes the data, validates the schema, and streams the payload to the message broker.
4. **Streaming/Broker Layer:** **Apache Kafka** (running in KRaft mode) buffers the high-throughput events under the `test-iot` topic, decoupling ingestion from downstream processors.
5. **Processing & Storage Layer:** A custom Python consumer (`processors/kafka_to_cassandra.py`) retrieves events from Kafka, applies necessary transformations, and continuously persists the time-series data into **Apache Cassandra**. The processor features built-in retry mechanisms to gracefully handle NoSQL cluster cold starts.
6. **Visualization Layer:** A live **Streamlit** dashboard (`dashboard/dashboard.py`) consumes metrics directly from Kafka to render real-time, animated analytical charts.

---

## 🛠️ Prerequisites

Before running the pipeline, ensure the following are installed and configured on your host machine:

- **Docker** and **Docker Compose**
- **Python 3.x** (for running the edge agent locally or on the edge device)
- A **Tailscale** account and client configured on both the edge device and the host machine.

---

## 🚀 Quick Start / How to Run

Follow these steps to deploy the data pipeline locally:

### Step 1: Clone the Repository
```bash
git clone https://github.com/your-username/iot-pipeline.git
cd iot-pipeline
```

### Step 2: Spin Up the Infrastructure
Start the entire infrastructure (Kafka, NiFi, Cassandra, Consumer, and Dashboard) using Docker Compose in detached mode:
```bash
docker compose up -d --build
```
*Note: Cassandra may take a few minutes to complete its initial bootstrap. The custom Python consumer will automatically retry until the database is ready.*

### Step 3: Configure Apache NiFi
1. Navigate to the NiFi Web UI at [http://localhost:8080/nifi](http://localhost:8080/nifi).
2. Default Credentials (unless modified in your `docker-compose.yml`):
   - **Username:** `admin`
   - **Password:** `supersecretpassword123`
3. Upload the pre-built NiFi flow template:
   - Go to the **Process Group** grid.
   - Click the **Upload Template** icon and select the `nifi/iot-nifi-template.xml` file from this repository.
4. Drag and drop the instantiated template onto the canvas and start all processors to begin listening for incoming HTTP payloads.

### Step 4: Start the Edge Telemetry Agent
On your edge device (or locally for testing), start the Python agent to begin data transmission. Make sure to install the requirements first:
```bash
# Install dependencies
pip install -r requirements.txt

# Run the agent
python3 edge/edge_agent.py
```

### Step 5: View the Live Dashboard
With data flowing securely from the edge to the message broker, open the Streamlit visualization app in your browser:
[http://localhost:8501](http://localhost:8501)

---

## 🗺️ Future Roadmap

While the pipeline currently operates successfully in a local/Dockerized environment, the architecture is designed to scale. Future iterations will include:

- **Cloud Migration (AWS):** Deploying the core infrastructure (`docker-compose` stack) to an **AWS EC2** instance, establishing a true remote connection from the Debian 13 edge device via the Tailscale VPN.
- **Continuous Deployment (CI/CD):** Implementing fully automated **GitHub Actions** workflows to test, build, and deploy the infrastructure to the AWS EC2 instance upon every `git push`.
