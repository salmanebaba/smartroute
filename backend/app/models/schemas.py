from pydantic import BaseModel, Field
from typing import Optional, List


class Location(BaseModel):
    """Geographic location model."""
    lat: float = Field(..., description="Latitude coordinate")
    lng: float = Field(..., description="Longitude coordinate")


class Bin(BaseModel):
    """Bin/Container model with location and telemetry."""
    id: str = Field(..., description="Unique bin identifier")
    latitude: float = Field(..., description="Latitude coordinate")
    longitude: float = Field(..., description="Longitude coordinate")
    fill_level: int = Field(..., ge=0, le=100, description="Fill level percentage (0-100)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "bin_001",
                "latitude": 33.979,
                "longitude": -6.866,
                "fill_level": 75
            }
        }


class RouteStop(BaseModel):
    """Single stop in an optimized route."""
    bin: Bin
    order: int = Field(..., description="Order in the route")
    distance_from_previous: Optional[float] = None


class OptimizedRoute(BaseModel):
    """Complete optimized route with all stops."""
    strategy: str = Field(..., description="Optimization strategy used")
    total_distance: float = Field(..., description="Total route distance in km")
    stops: List[RouteStop]
    estimated_time: Optional[float] = None


class DebugData(BaseModel):
    """Debug information containing all bins and their telemetry."""
    total_bins: int
    bins: List[Bin]
