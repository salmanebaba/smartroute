from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class Bin(BaseModel):
    id: str
    name: str
    latitude: float
    longitude: float
    fill_level: int
    battery: int = 100
    temperature: float = 25.0
    last_updated: datetime = datetime.now()
    last_collected: Optional[datetime] = None

    @property
    def status(self) -> str:
        if self.fill_level >= 80:
            return "critical"
        elif self.fill_level >= 50:
            return "warning"
        return "normal"

    def to_api_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "fill_level": self.fill_level,
            "status": self.status,
            "battery": self.battery,
            "temperature": self.temperature,
            "last_updated": self.last_updated.isoformat(),
            "last_collected": self.last_collected.isoformat() if self.last_collected else None,
        }
