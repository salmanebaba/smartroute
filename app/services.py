import folium
import requests
from geopy.distance import geodesic
from folium.features import DivIcon
from .models import Bin
from .mock_data import bins, CAMION_START


def osrm_distance(start: tuple[float, float], end: tuple[float, float]) -> float:
    """Calcule la distance réelle via OSRM entre deux points (lon, lat)."""
    url = f"http://localhost:5000/route/v1/driving/{start[1]},{start[0]};{end[1]},{end[0]}?overview=false"
    try:
        response = requests.get(url)
        data = response.json()
        if data['code'] == 'Ok':
            return data['routes'][0]['distance'] / 1000
    except Exception:
        pass
    return geodesic(start, end).km


def calculate_distance(a: Bin, b: Bin) -> float:
    return geodesic((a.latitude, a.longitude), (b.latitude, b.longitude)).km


def optimize_route(bins: list[Bin], start_point: tuple[float, float]) -> tuple[list[str], float]:
    # Trier les poubelles du plus plein au moins plein
    sorted_bins = sorted([b for b in bins if b.fill_level > 0], key=lambda b: b.fill_level, reverse=True)

    total_distance = 0.0
    current_pos = start_point
    ordered_ids = []

    for bin in sorted_bins:
        dist = osrm_distance(current_pos, (bin.latitude, bin.longitude))
        total_distance += dist
        ordered_ids.append(bin.id)
        current_pos = (bin.latitude, bin.longitude)

    # Retour au garage
    total_distance += osrm_distance(current_pos, start_point)

    return ordered_ids, round(total_distance, 2)



def generate_map_with_route(start_point):
    ordered_ids, total_distance = optimize_route(bins, CAMION_START)
    route_map = folium.Map(location=start_point)

    folium.Marker(
        location=start_point,
        popup="Truck Garage (Start/End)",
        icon=folium.Icon(color="red", icon="home")
    ).add_to(route_map)

    folium.Marker(
        [start_point[0] + 0.005, start_point[1]],
        icon=DivIcon(
            icon_size=(300, 40),
            html=f'<div style="font-size:18px; background:white; padding:8px; border-radius:5px; box-shadow:0 2px 6px rgba(0,0,0,0.2)">Distance totale : {total_distance} km</div>'
        )
    ).add_to(route_map)

    bin_dict = {b.id: b for b in bins}
    route_points = [start_point] + [(bin_dict[bid].latitude, bin_dict[bid].longitude) for bid in ordered_ids] + [start_point]

    for idx, (lat, lon) in enumerate(route_points[1:-1], start=1):
        bin_obj = bin_dict[ordered_ids[idx-1]]
        folium.Marker(
            location=(lat, lon),
            icon=folium.DivIcon(html=f'<div style="font-size: 14pt; color: white; background: #007bff; border-radius: 50%; width: 32px; height: 32px; display: flex; align-items: center; justify-content: center; border: 2px solid #fff;">{idx}</div>'),
            tooltip=f"Poubelle {bin_obj.id} ({bin_obj.fill_level}%)"
        ).add_to(route_map)

    for i in range(len(route_points) - 1):
        start = route_points[i]
        end = route_points[i + 1]
        url = f"http://localhost:5000/route/v1/driving/{start[1]},{start[0]};{end[1]},{end[0]}?overview=full&geometries=geojson"
        try:
            resp = requests.get(url)
            data = resp.json()
            if data['code'] == 'Ok':
                coords = [(lat, lon) for lon, lat in data['routes'][0]['geometry']['coordinates']]
                from folium.plugins import AntPath
                AntPath(coords, color="green", weight=4, delay=800).add_to(route_map)
            else:
                folium.PolyLine([start, end], color="green", weight=2.5).add_to(route_map)
        except Exception:
            folium.PolyLine([start, end], color="green", weight=2.5).add_to(route_map)

    route_map.fit_bounds(route_points)
    return route_map._repr_html_()
