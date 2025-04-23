from pydantic import BaseModel
from typing import List
from datetime import datetime

class Bin(BaseModel):
    id: str
    latitude: float
    longitude: float
    fill_level: int  # en %
    last_updated: datetime

class RouteResponse(BaseModel):
    ordered_bins: List[str]
    total_distance_km: float
