import psutil
import time
import requests
from datetime import datetime

# --- CONFIGURATION ---
URL = "http://100.82.235.96:9999/content"
DEVICE_ID = "debian-edge-01"
SEND_INTERVAL = 0.5  

def get_metrics():
    """Récupère les métriques système en temps réel."""
    cpu_usage = psutil.cpu_percent(interval=None)

    ram = psutil.virtual_memory()
    ram_available_mb = round(ram.available / (1024 * 1024), 2)

    temp = None
    sensors = psutil.sensors_temperatures()
    if 'coretemp' in sensors:
        temp = sensors['coretemp'][0].current
    elif 'cpu_thermal' in sensors:
        temp = sensors['cpu_thermal'][0].current

    return {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "device_id": DEVICE_ID,
        "cpu_usage_percent": cpu_usage,
        "ram_available_mb": ram_available_mb,
        "temperature_c": temp
    }

def main():
    print(f"🚀 Démarrage de l'Agent Edge Python sur {DEVICE_ID}...")
    print(f"📡 Cible : {URL}")

    try:
        while True:
            
            payload = get_metrics()

            try:
                response = requests.post(URL, json=payload, timeout=2)
                print(f"[+] Envoyé à {payload['timestamp']} | Status: {response.status_code} | CPU: {payload['cpu_usage_percent']}%")
            except requests.exceptions.RequestException as e:
                print(f"[-] Erreur réseau (le PC principal est-il allumé ?) : {e}")

            time.sleep(SEND_INTERVAL)

    except KeyboardInterrupt:
        print("\n🛑 Arrêt de l'agent par l'utilisateur.")

if __name__ == "__main__":
    main()