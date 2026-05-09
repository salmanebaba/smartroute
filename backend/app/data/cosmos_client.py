"""
Data Access Layer for Azure Cosmos DB
Handles all database operations for bins inventory and telemetry.
"""
from typing import List, Optional
from azure.cosmos import CosmosClient, exceptions
from app.config import (
    COSMOS_URI,
    COSMOS_KEY,
    DATABASE_NAME,
    TELEMETRY_CONTAINER,
    INVENTORY_CONTAINER,
)
from app.models.schemas import Bin


class CosmosDataClient:
    """Manages all Cosmos DB operations."""
    
    def __init__(self):
        """Initialize Cosmos DB client."""
        try:
            self.client = CosmosClient(COSMOS_URI, credential=COSMOS_KEY)
            self.database = self.client.get_database_client(DATABASE_NAME)
            self.telemetry_container = self.database.get_container_client(TELEMETRY_CONTAINER)
            self.inventory_container = self.database.get_container_client(INVENTORY_CONTAINER)
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Cosmos DB client: {str(e)}")
    
    def get_all_bins_with_telemetry(self) -> List[Bin]:
        """
        Fetch all bins from inventory with their latest telemetry data.
        
        Returns:
            List[Bin]: List of bins with location and fill level
        """
        try:
            inventory = list(self.inventory_container.read_all_items())
            live_bins = []
            
            for item in inventory:
                try:
                    bin_id = item['id']
                    fill_level = self._get_latest_fill_level(bin_id)
                    
                    bin_obj = Bin(
                        id=bin_id,
                        latitude=item['location']['lat'],
                        longitude=item['location']['lng'],
                        fill_level=fill_level
                    )
                    live_bins.append(bin_obj)
                except KeyError as e:
                    print(f"Warning: Missing field for bin {item.get('id', 'unknown')}: {str(e)}")
                    continue
                except Exception as e:
                    print(f"Warning: Error processing bin {item.get('id', 'unknown')}: {str(e)}")
                    continue
            
            return live_bins
        except Exception as e:
            raise RuntimeError(f"Error fetching bins from inventory: {str(e)}")
    
    def _get_latest_fill_level(self, device_id: str) -> int:
        """
        Get the latest fill level for a specific device from telemetry.
        
        Args:
            device_id: The device/bin ID
            
        Returns:
            int: Latest fill level (0-100), defaults to 0 if not found
        """
        try:
            query = {
                "query": "SELECT TOP 1 c.fill_level FROM c WHERE c.deviceId = @devId AND c.type = 'fill_level_update' ORDER BY c._ts DESC",
                "parameters": [{"name": "@devId", "value": device_id}]
            }
            telemetry = list(
                self.telemetry_container.query_items(
                    query=query,
                    enable_cross_partition_query=True
                )
            )
            return telemetry[0]['fill_level'] if telemetry else 0
        except KeyError as e:
            print(f"Warning: Missing 'fill_level' field for {device_id}: {str(e)}")
            return 0
        except Exception as e:
            print(f"Warning: Could not fetch telemetry for {device_id}: {str(e)}")
            return 0
    
    def get_bin_by_id(self, bin_id: str) -> Optional[Bin]:
        """
        Fetch a specific bin by ID.
        
        Args:
            bin_id: The bin ID to fetch
            
        Returns:
            Bin: The bin object or None if not found
        """
        try:
            item = self.inventory_container.read_item(item=bin_id, partition_key=bin_id)
            fill_level = self._get_latest_fill_level(bin_id)
            
            return Bin(
                id=bin_id,
                latitude=item['location']['lat'],
                longitude=item['location']['lng'],
                fill_level=fill_level
            )
        except exceptions.CosmosResourceNotFoundError:
            return None
        except Exception as e:
            raise RuntimeError(f"Error fetching bin {bin_id}: {str(e)}")
    
    def get_bins_above_threshold(self, threshold: int = 70) -> List[Bin]:
        """
        Get all bins with fill level above a certain threshold.
        
        Args:
            threshold: Minimum fill level percentage
            
        Returns:
            List[Bin]: Bins above threshold
        """
        all_bins = self.get_all_bins_with_telemetry()
        return [bin_obj for bin_obj in all_bins if bin_obj.fill_level >= threshold]
