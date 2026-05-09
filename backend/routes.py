from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from services import generate_map_with_route

router = APIRouter()
CAMION_START = (33.979448, -6.866329) #

router = APIRouter()

@router.get("/map", response_class=HTMLResponse)
def get_map(strategy: str = "distance"):
    return generate_map_with_route(CAMION_START, strategy=strategy)

@router.get("/debug-data")
def debug_data():
    from services import get_live_bins
    return get_live_bins()