import uuid
from datetime import datetime, timedelta
import random
from azure.cosmos import CosmosClient

import os
from dotenv import load_dotenv
load_dotenv()

URL = os.getenv("COSMOS_URI")
KEY = os.getenv("COSMOS_KEY")
DATABASE_NAME = "SmartBinDB"
CONTAINER_NAME = "Telemetry"
client = CosmosClient(URL, credential=KEY)
container = client.get_database_client(DATABASE_NAME).get_container_client(CONTAINER_NAME)

# Liste des IDs pour simuler plusieurs bacs
device_ids = ["Bin_4", "Bin_1", "Bin_3", "Bin_2", "Bin_5"]
start_date = datetime.utcnow() - timedelta(days=10)

print("🚀 Génération de l'historique de 10 jours...")

for device_id in device_ids:
    current_level = 0
    for day in range(11):
        # 4 à 6 cycles de données par jour
        for hour in range(random.randint(4, 6)):
            timestamp = start_date + timedelta(days=day, hours=hour*4)
            timestamp_str = timestamp.isoformat() + "0000Z" # Format exact Azure

            # --- 1. Événement de Remplissage ---
            current_level += random.randint(10, 20)
            if current_level > 100: current_level = 100
            
            fill_item = {
                "id": str(uuid.uuid4()),
                "deviceId": device_id,
                "type": "fill_level_update",
                "timestamp": timestamp_str,
                "fill_level": current_level,
                "alert": current_level >= 90,
                "detection_type": None # Champ null pour la cohérence
            }
            container.create_item(body=fill_item)

            # --- 2. Événement de Présence (Aléatoire) ---
            if random.random() > 0.4:
                # Arrivée
                presence_in = {
                    "id": str(uuid.uuid4()),
                    "deviceId": device_id,
                    "type": "presence_event",
                    "timestamp": (timestamp + timedelta(minutes=2)).isoformat() + "0000Z",
                    "fill_level": None,
                    "alert": None,
                    "detection_type": "person_arrived"
                }
                container.create_item(body=presence_in)
                
                # Départ
                presence_out = {
                    "id": str(uuid.uuid4()),
                    "deviceId": device_id,
                    "type": "presence_event",
                    "timestamp": (timestamp + timedelta(minutes=5)).isoformat() + "0000Z",
                    "fill_level": None,
                    "alert": None,
                    "detection_type": "person_left"
                }
                container.create_item(body=presence_out)

        # Simuler un vidage si plein
        if current_level >= 90:
            current_level = 0

print("✅ Données injectées")