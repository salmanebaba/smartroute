from pydantic import BaseModel

class Bin(BaseModel):
    id: str
    latitude: float
    longitude: float
    fill_level: int
