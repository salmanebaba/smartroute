from pydantic import BaseModel, Field
from typing import Optional, List

class Location(BaseModel):
    lat: float = Field(..., description="Latitude coordinate")
    lng: float = Field(..., description="Longitude coordinate")

class Bin(BaseModel):
    id: str = Field(..., description="Unique bin identifier")
    latitude: float = Field(..., description="Latitude coordinate")
    longitude: float = Field(..., description="Longitude coordinate")
    fill_level: int = Field(..., ge=0, le=100, description="Fill level percentage (0-100)")

class RouteStop(BaseModel):
    bin: Bin
    order: int = Field(..., description="Order in the route")
    distance_from_previous: Optional[float] = None

class OptimizedRoute(BaseModel):
    strategy: str = Field(..., description="Optimization strategy used")
    total_distance: float = Field(..., description="Total route distance in km")
    stops: List[RouteStop]
    estimated_time: Optional[float] = None

class DebugData(BaseModel):
    total_bins: int
    bins: List[Bin]

class DailyStatistics(BaseModel):
    date: str
    average_fill_level: float
    bins_collected: int
    urgent_count: int
    peak_fill_level: int

class CollectionHistory(BaseModel):
    range: str
    total_collections: int
    average_daily_collections: float
    peak_day: Optional[str] = None
    daily_data: List[DailyStatistics]

class BinHistoryData(BaseModel):
    bin_id: str
    timestamp: str
    fill_level: int