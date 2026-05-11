from typing import List, Optional
import time
from azure.cosmos import CosmosClient, exceptions
from app.config import COSMOS_URI, COSMOS_KEY, DATABASE_NAME, TELEMETRY_CONTAINER, INVENTORY_CONTAINER
from app.models.schemas import Bin

class CosmosDataClient:
    def __init__(self):
        try:
            self.client = CosmosClient(COSMOS_URI, credential=COSMOS_KEY)
            self.database = self.client.get_database_client(DATABASE_NAME)
            self.telemetry_container = self.database.get_container_client(TELEMETRY_CONTAINER)
            self.inventory_container = self.database.get_container_client(INVENTORY_CONTAINER)
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Cosmos DB client: {str(e)}")
    
    def get_all_bins_with_telemetry(self) -> List[Bin]:
        try:
            inventory = list(self.inventory_container.read_all_items())
            live_bins = []
            for item in inventory:
                try:
                    bin_id = item['id']
                    fill_level = self._get_latest_fill_level(bin_id)
                    live_bins.append(Bin(
                        id=bin_id, latitude=item['location']['lat'],
                        longitude=item['location']['lng'], fill_level=fill_level
                    ))
                except Exception:
                    continue
            return live_bins
        except Exception as e:
            raise RuntimeError(f"Error fetching bins: {str(e)}")
    
    def _get_latest_fill_level(self, device_id: str) -> int:
        try:
            query = {
                "query": "SELECT TOP 1 c.fill_level FROM c WHERE c.deviceId = @devId AND c.type = 'fill_level_update' ORDER BY c._ts DESC",
                "parameters": [{"name": "@devId", "value": device_id}]
            }
            telemetry = list(self.telemetry_container.query_items(query=query, enable_cross_partition_query=True))
            return telemetry[0]['fill_level'] if telemetry else 0
        except Exception:
            return 0
    
    def get_bin_by_id(self, bin_id: str) -> Optional[Bin]:
        try:
            item = self.inventory_container.read_item(item=bin_id, partition_key=bin_id)
            return Bin(id=bin_id, latitude=item['location']['lat'], longitude=item['location']['lng'], fill_level=self._get_latest_fill_level(bin_id))
        except exceptions.CosmosResourceNotFoundError:
            return None

    def get_bin_fill_history(self, bin_id: str, days: int = 7) -> List[dict]:
        try:
            query = {
                "query": "SELECT c.timestamp, c.fill_level FROM c WHERE c.deviceId = @binId AND c.type = 'fill_level_update' ORDER BY c._ts DESC LIMIT 1000",
                "parameters": [{"name": "@binId", "value": bin_id}]
            }
            return list(self.telemetry_container.query_items(query=query, enable_cross_partition_query=True))
        except Exception:
            return []
    
    def get_all_telemetry_records(self, days: int = 7) -> List[dict]:
        time_threshold = int(time.time()) - (days * 24 * 60 * 60)
        try:
            query = {
                "query": "SELECT c.deviceId, c.timestamp, c.fill_level FROM c WHERE c.type = 'fill_level_update' AND c._ts >= @timeThreshold ORDER BY c._ts DESC",
                "parameters": [{"name": "@timeThreshold", "value": time_threshold}]
            }
            return list(self.telemetry_container.query_items(query=query, enable_cross_partition_query=True))
        except Exception:
            return []
    
    def get_daily_statistics(self, days: int = 7) -> dict:
        telemetry = self.get_all_telemetry_records(days)
        daily_max_per_bin = {}
        
        for record in telemetry:
            try:
                timestamp = record.get('timestamp', '')
                date_str = timestamp.split('T')[0] if 'T' in timestamp else timestamp
                device_id = record.get('deviceId')
                fill_level = record.get('fill_level', 0)
                
                if not date_str or not device_id: continue
                
                if date_str not in daily_max_per_bin: daily_max_per_bin[date_str] = {}
                
                if device_id not in daily_max_per_bin[date_str]:
                    daily_max_per_bin[date_str][device_id] = fill_level
                else:
                    daily_max_per_bin[date_str][device_id] = max(daily_max_per_bin[date_str][device_id], fill_level)
            except Exception:
                continue
                
        daily_data = {}
        for date_str, bins in daily_max_per_bin.items():
            fill_levels = list(bins.values())
            daily_data[date_str] = {'fill_levels': fill_levels, 'max_fill': max(fill_levels) if fill_levels else 0}
            
        return daily_data