from fastapi import APIRouter, HTTPException
from datetime import datetime
from fastapi.responses import HTMLResponse
from .mock_data import bins, CAMION_START
from .services import generate_map_with_route

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
def get_map():
    return generate_map_with_route(CAMION_START)

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