import os
from dotenv import load_dotenv

load_dotenv()

# Azure Cosmos DB Configuration
COSMOS_URI = os.getenv("COSMOS_URI")
COSMOS_KEY = os.getenv("COSMOS_KEY")
DATABASE_NAME = os.getenv("DATABASE_NAME", "SmartBinDB")
TELEMETRY_CONTAINER = "Telemetry"
INVENTORY_CONTAINER = "BinsInventory"

# Application Configuration
APP_TITLE = "Smart Bin Route Optimizer"
DEBUG = os.getenv("DEBUG", "False") == "True"

# Geographic Configuration
TRUCK_START_LAT = 33.979448
TRUCK_START_LNG = -6.866329
TRUCK_START = {"lat": TRUCK_START_LAT, "lng": TRUCK_START_LNG}

# CORS Configuration
CORS_ORIGINS = ["*"]  # Restrict in production
