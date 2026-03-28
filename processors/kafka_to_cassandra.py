import json
import time
import os
from confluent_kafka import Consumer, KafkaError
from cassandra.cluster import Cluster
from datetime import datetime

kafka_server = os.getenv('KAFKA_BOOTSTRAP', 'localhost:9092')
cassandra_host = os.getenv('CASSANDRA_HOST', '127.0.0.1')

# --- CONFIGURATION ---
KAFKA_CONF = {
    'bootstrap.servers': kafka_server,
    'group.id': 'cassandra-consumer-group',
    'auto.offset.reset': 'earliest'
}
CASSANDRA_NODES = [cassandra_host]
TOPIC = 'test-iot'

def connect_cassandra(retries=10, delay=10):
    cluster = Cluster(CASSANDRA_NODES)
    session = None
    
    for i in range(retries):
        try:
            print(f"[-] Tentative de connexion à Cassandra ({i+1}/{retries})...")
            session = cluster.connect()
            
            print("[-] Vérification/Création du Keyspace 'smart_city'...")
            session.execute("""
                CREATE KEYSPACE IF NOT EXISTS smart_city 
                WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};
            """)
            
            session.set_keyspace('smart_city')
            
            session.execute("""
                CREATE TABLE IF NOT EXISTS telemetry (
                    device_id text,
                    timestamp timestamp,
                    cpu_usage_percent float,
                    ram_available_mb float,
                    temperature_c float,
                    PRIMARY KEY (device_id, timestamp)
                ) WITH CLUSTERING ORDER BY (timestamp DESC);
            """)
            
            print("[V] Cassandra est prête et le schéma est initialisé !")
            return session
        except Exception as e:
            print(f"[!] Erreur: {e}")
            time.sleep(delay)
            
    raise Exception("Impossible d'initialiser Cassandra.")

def main():
    print("[-] Démarrage de la connexion à Cassandra...")
    session = connect_cassandra()
    
    insert_stmt = session.prepare("""
        INSERT INTO telemetry (device_id, timestamp, cpu_usage_percent, ram_available_mb, temperature_c)
        VALUES (?, ?, ?, ?, ?)
    """)

    print("[-] Connexion à Kafka...")
    consumer = Consumer(KAFKA_CONF)
    consumer.subscribe([TOPIC])

    print(f"[*] En attente de messages sur le topic '{TOPIC}'...")

    try:
        while True:
            msg = consumer.poll(1.0) 

            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                else:
                    print(f"[!] Erreur Kafka: {msg.error()}")
                    break

            # --- LOGIQUE DE TRAITEMENT ---
            try:
                data = json.loads(msg.value().decode('utf-8'))
                
                ts_obj = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))

                session.execute(insert_stmt, (
                    data['device_id'],
                    ts_obj,
                    float(data['cpu_usage_percent']),
                    float(data['ram_available_mb']),
                    float(data['temperature_c']) if data['temperature_c'] else None
                ))
                
                print(f"[OK] Message inséré : {data['device_id']} @ {data['timestamp']}")

            except Exception as e:
                print(f"[X] Erreur lors du processing du message: {e}")

    except KeyboardInterrupt:
        print("\n[!] Arrêt du consommateur...")
    finally:
        consumer.close()

if __name__ == "__main__":
    main()