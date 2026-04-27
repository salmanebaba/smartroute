from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from mock_data import bins, CAMION_START, generate_fill_history
from services import generate_map_with_route, get_route_geojson, get_bin_stats

router = APIRouter()

# ── Legacy HTML map endpoints (backward compatibility) ──

@router.get("/distance", response_class=HTMLResponse)
def get_map_distance():
    return generate_map_with_route(CAMION_START, strategy="distance")

@router.get("/map", response_class=HTMLResponse)
def get_map_fill_level():
    return generate_map_with_route(CAMION_START, strategy="fill_level")


# ── JSON API endpoints ──

@router.get("/api/bins")
def api_get_bins():
    """Return all bins as JSON."""
    return [b.to_api_dict() for b in bins]


@router.get("/api/bins/history")
def api_get_history(hours: int = 24):
    """Return simulated fill-level history for charts."""
    return generate_fill_history(hours)


@router.get("/api/route")
def api_get_route(strategy: str = "fill_level"):
    """Return optimized route as JSON with GeoJSON coordinates."""
    if strategy not in ("distance", "fill_level"):
        raise HTTPException(status_code=400, detail="Strategy must be 'distance' or 'fill_level'")
    return get_route_geojson(strategy)


@router.get("/api/stats")
def api_get_stats():
    """Return aggregate statistics."""
    return get_bin_stats()


@router.post("/api/bins/{bin_id}/update")
def api_update_bin(bin_id: str, data: dict):
    """Update a bin's fill level."""
    fill = data.get("fill_level")
    if fill is None:
        raise HTTPException(status_code=400, detail="Missing 'fill_level'")

    for b in bins:
        if b.id == bin_id:
            b.fill_level = int(fill)
            from datetime import datetime
            b.last_updated = datetime.now()
            return {"message": f"Bin {bin_id} updated", "bin": b.to_api_dict()}

    raise HTTPException(status_code=404, detail=f"Bin {bin_id} not found")


# ── Legacy update endpoint (backward compatibility) ──

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
            return {"message": f"Poubelle {bin_id} mise à jour avec succès"}