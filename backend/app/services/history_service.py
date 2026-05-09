"""
Service layer for historical data and statistics.
Handles collection history, trends, and analytics.
"""
from datetime import datetime, timedelta
from typing import List, Dict
from app.data.cosmos_client import CosmosDataClient
from app.models.schemas import DailyStatistics, CollectionHistory, BinHistoryData


class HistoryService:
    """Service for managing and analyzing historical collection data."""
    
    def __init__(self, data_client: CosmosDataClient):
        """
        Initialize history service.
        
        Args:
            data_client: Cosmos DB data access client
        """
        self.data_client = data_client
    
    def get_collection_history(self, range_days: str = "7d") -> CollectionHistory:
        """
        Get historical collection statistics for a specified time range.
        
        Args:
            range_days: Time range ('7d', '30d', or '90d')
            
        Returns:
            CollectionHistory with daily statistics
        """
        # Parse range
        days_map = {"7d": 7, "30d": 30, "90d": 90}
        days = days_map.get(range_days, 7)
        
        try:
            # Get daily statistics from database
            daily_stats_dict = self.data_client.get_daily_statistics(days)
            
            # Convert to list of DailyStatistics
            daily_data = []
            total_collections = 0
            peak_day = None
            peak_count = 0
            
            for date_str in sorted(daily_stats_dict.keys(), reverse=True):
                stats = daily_stats_dict[date_str]
                fill_levels = stats['fill_levels']
                
                if fill_levels:
                    avg_fill = sum(fill_levels) / len(fill_levels)
                    # Estimate bins collected as those with fill > 50%
                    bins_collected = len([f for f in fill_levels if f > 50])
                    # Estimate urgent as bins with fill > 85%
                    urgent_count = len([f for f in fill_levels if f > 85])
                    peak_fill = stats['max_fill']
                    
                    daily_stat = DailyStatistics(
                        date=date_str,
                        average_fill_level=round(avg_fill, 2),
                        bins_collected=bins_collected,
                        urgent_count=urgent_count,
                        peak_fill_level=peak_fill
                    )
                    daily_data.append(daily_stat)
                    total_collections += bins_collected
                    
                    if bins_collected > peak_count:
                        peak_count = bins_collected
                        peak_day = date_str
            
            # Calculate average daily collections
            avg_daily = total_collections / len(daily_data) if daily_data else 0
            
            return CollectionHistory(
                range=range_days,
                total_collections=total_collections,
                average_daily_collections=round(avg_daily, 2),
                peak_day=peak_day,
                daily_data=daily_data
            )
        
        except Exception as e:
            print(f"Error getting collection history: {str(e)}")
            # Return empty history
            return CollectionHistory(
                range=range_days,
                total_collections=0,
                average_daily_collections=0,
                peak_day=None,
                daily_data=[]
            )
    
    def get_bin_history(self, bin_id: str, days: int = 7) -> List[BinHistoryData]:
        """
        Get historical fill level data for a specific bin.
        
        Args:
            bin_id: The bin identifier
            days: Number of days to retrieve
            
        Returns:
            List of historical fill level records
        """
        try:
            records = self.data_client.get_bin_fill_history(bin_id, days)
            
            history_data = []
            for record in records:
                try:
                    history_item = BinHistoryData(
                        bin_id=bin_id,
                        timestamp=record.get('timestamp', ''),
                        fill_level=record.get('fill_level', 0)
                    )
                    history_data.append(history_item)
                except Exception:
                    continue
            
            return history_data
        except Exception as e:
            print(f"Error getting bin history: {str(e)}")
            return []
    
    def get_trend_analysis(self, range_days: str = "7d") -> Dict:
        """
        Get trend analysis for collection patterns.
        
        Args:
            range_days: Time range for analysis
            
        Returns:
            Dictionary with trend insights
        """
        try:
            history = self.get_collection_history(range_days)
            
            if not history.daily_data:
                return {
                    "trend": "insufficient_data",
                    "peak_day": None,
                    "average_urgency": 0,
                    "busiest_hour": None
                }
            
            # Calculate metrics
            avg_urgency = (
                sum(d.urgent_count for d in history.daily_data) / len(history.daily_data)
            ) if history.daily_data else 0
            
            # Find busiest day
            busiest_day = max(
                history.daily_data,
                key=lambda x: x.bins_collected
            ).date if history.daily_data else None
            
            # Determine trend
            if len(history.daily_data) >= 2:
                recent_avg = sum(
                    d.bins_collected for d in history.daily_data[:3]
                ) / 3
                older_avg = sum(
                    d.bins_collected for d in history.daily_data[-3:]
                ) / 3
                
                if recent_avg > older_avg * 1.1:
                    trend = "increasing"
                elif recent_avg < older_avg * 0.9:
                    trend = "decreasing"
                else:
                    trend = "stable"
            else:
                trend = "insufficient_data"
            
            return {
                "trend": trend,
                "peak_day": busiest_day,
                "average_urgency": round(avg_urgency, 2),
                "total_days_analyzed": len(history.daily_data),
                "total_collections": history.total_collections
            }
        
        except Exception as e:
            print(f"Error calculating trend analysis: {str(e)}")
            return {
                "trend": "error",
                "error": str(e)
            }
