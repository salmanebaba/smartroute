from fastapi import APIRouter, HTTPException
from datetime import datetime
from fastapi.responses import HTMLResponse

from .models import RouteResponse
from .mock_data import bins, CAMION_START
from .services import generate_map_with_route, optimize_route

router = APIRouter()
@router.get("/optimize-route", response_model=RouteResponse)
def get_optimized_route(strategy: str = "distance"):
    ordered_ids, total_distance = optimize_route(bins, CAMION_START, strategy=strategy)
    return RouteResponse(ordered_bins=ordered_ids, total_distance_km=total_distance)

@router.get("/distance", response_class=HTMLResponse)
def get_map_distance():
    return generate_map_with_route(CAMION_START, strategy="distance")

@router.get("/", response_class=HTMLResponse)
def get_map_fill_level():
    return generate_map_with_route(CAMION_START, strategy="fill_level")

@router.post("/update-bin")
def update_bin_partial(data: dict):
    bin_id = data.get("id")
    fill = data.get("fill_level")

    if bin_id is None or fill is None:
        raise HTTPException(status_code=400, detail="Missing 'id' or 'fill_level'")

    # Trouver la poubelle
    for b in bins:
        if b.id == bin_id:
            b.fill_level = fill
            b.last_updated = datetime.now()
            return {"message": f"Poubelle {bin_id} mise à jour avec succès"}