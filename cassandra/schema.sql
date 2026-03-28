-- Création du Keyspace 
CREATE KEYSPACE IF NOT EXISTS smart_city 
WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};

-- Utilisation du Keyspace
USE smart_city;

-- Création de la table pour tes métriques
CREATE TABLE IF NOT EXISTS telemetry (
    device_id text,
    timestamp timestamp,
    cpu_usage_percent float,
    ram_available_mb float,
    temperature_c float,
    PRIMARY KEY (device_id, timestamp)
) WITH CLUSTERING ORDER BY (timestamp DESC);