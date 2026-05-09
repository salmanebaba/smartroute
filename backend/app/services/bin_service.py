"""
Business logic for bin management and operations.
"""
from typing import List
from app.data.cosmos_client import CosmosDataClient
from app.models.schemas import Bin
from app.utils.constants import FULL_THRESHOLD


class BinService:
    """Service layer for bin-related operations."""
    
    def __init__(self, data_client: CosmosDataClient):
        """
        Initialize bin service.
        
        Args:
            data_client: Cosmos DB data access client
        """
        self.data_client = data_client
    
    def get_all_bins(self) -> List[Bin]:
        """
        Get all bins with current telemetry.
        
        Returns:
            List[Bin]: All bins with location and fill level
        """
        return self.data_client.get_all_bins_with_telemetry()
    
    def get_bins_needing_collection(self, threshold: int = FULL_THRESHOLD) -> List[Bin]:
        """
        Get bins that need collection (above threshold).
        Uses 0 as default to include any bin with fill level > 0.
        
        Args:
            threshold: Fill level threshold for collection (default includes all non-empty bins)
            
        Returns:
            List[Bin]: Bins needing collection
        """
        all_bins = self.get_all_bins()
        # Include bins with fill_level > 0 (any non-empty bin)
        return [bin_obj for bin_obj in all_bins if bin_obj.fill_level > 0]
    
    def get_bin_details(self, bin_id: str) -> Bin:
        """
        Get detailed information for a specific bin.
        
        Args:
            bin_id: The bin ID
            
        Returns:
            Bin: Bin details
            
        Raises:
            ValueError: If bin not found
        """
        bin_obj = self.data_client.get_bin_by_id(bin_id)
        if not bin_obj:
            raise ValueError(f"Bin {bin_id} not found")
        return bin_obj
    
    def get_collection_statistics(self) -> dict:
        """
        Get statistics about bin collection needs.
        
        Returns:
            dict: Statistics including total bins, bins needing collection, etc.
        """
        all_bins = self.get_all_bins()
        bins_needing_collection = self.get_bins_needing_collection()
        
        avg_fill_level = (
            sum(b.fill_level for b in all_bins) / len(all_bins) if all_bins else 0
        )
        
        return {
            "total_bins": len(all_bins),
            "bins_needing_collection": len(bins_needing_collection),
            "average_fill_level": round(avg_fill_level, 2),
            "collection_percentage": round(
                (len(bins_needing_collection) / len(all_bins) * 100) if all_bins else 0, 2
            )
        }
