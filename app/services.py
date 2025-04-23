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
            return data['routes'][0]['distance'] / 1000  # mètres -> km
    except Exception:
        pass
    return geodesic(start, end).km  # fallback

def calculate_distance(a: Bin, b: Bin) -> float:
    return geodesic((a.latitude, a.longitude), (b.latitude, b.longitude)).km

def optimize_route(bins: list[Bin], start_point: tuple[float, float]) -> tuple[list[str], float]:
    # Sort bins by fill level (descending)
    sorted_bins = sorted(bins, key=lambda b: b.fill_level, reverse=True)

    # Calculate the route distance including return to the starting point
    total_distance = 0.0
    current_pos = start_point
    ordered_ids = []

    for bin in sorted_bins:
        dist = osrm_distance(current_pos, (bin.latitude, bin.longitude))
        total_distance += dist
        current_pos = (bin.latitude, bin.longitude)
        ordered_ids.append(bin.id)

    # Add distance back to the starting point
    total_distance += osrm_distance(current_pos, start_point)

    return ordered_ids, round(total_distance, 2)

def generate_map_with_route(start_point):
    ordered_ids, total_distance = optimize_route(bins, CAMION_START)
    # Create a map centered at the starting point (garage)
    route_map = folium.Map(location=start_point, zoom_start=14)

    # Add a marker for the truck's garage (starting/ending point)
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
    # Add bins to the map
    
    for bin in bins:
        folium.Marker(
            location=(bin.latitude, bin.longitude),
            popup=f"Bin ID: {bin.id}, Fill Level: {bin.fill_level}%",
            icon=folium.Icon(color="blue", icon="trash")
        ).add_to(route_map)

    # Sort bins by fill level (descending) for the route
    sorted_bins = sorted(bins, key=lambda b: b.fill_level, reverse=True)

    # Add the route to the map
    current_location = start_point
    order = 1
    for bin in sorted_bins:
        bin_location = (bin.latitude, bin.longitude)
        # Get route geometry from OSRM
        url = f"http://localhost:5000/route/v1/driving/{current_location[1]},{current_location[0]};{bin_location[1]},{bin_location[0]}?overview=full&geometries=geojson"
        try:
            resp = requests.get(url)
            data = resp.json()
            if data['code'] == 'Ok':
                coords = [(lat, lon) for lon, lat in data['routes'][0]['geometry']['coordinates']]
                segment_distance = data['routes'][0]['distance'] / 1000  # mètres -> km
            else:
                coords = [current_location, bin_location]
                segment_distance = geodesic(current_location, bin_location).km
        except Exception:
            coords = [current_location, bin_location]
            segment_distance = geodesic(current_location, bin_location).km

        # Add label for order and distance with a horizontal arrow
        folium.Marker(
            location=(bin.latitude, bin.longitude),
            icon=folium.DivIcon(html=f'<div style="font-size: 14pt; color: white; background: #007bff; border-radius: 50%; width: 32px; height: 32px; display: flex; align-items: center; justify-content: center; border: 2px solid #fff;">{order}</div>'),
            tooltip=f"Poubelle {bin.id} ({bin.fill_level}%)"
        ).add_to(route_map)
        # Draw a PolyLine with arrows (AntPath) for the route segment
        try:
            from folium.plugins import AntPath
            if data['code'] == 'Ok':
                AntPath(coords, color="green", weight=4, delay=800).add_to(route_map)
            else:
                AntPath([current_location, bin_location], color="green", weight=4, delay=800).add_to(route_map)
        except Exception:
            folium.PolyLine([current_location, bin_location], color="green", weight=2.5).add_to(route_map)

        current_location = bin_location
        order += 1

    # Add the return to the starting point
    url = f"http://localhost:5000/route/v1/driving/{current_location[1]},{current_location[0]};{start_point[1]},{start_point[0]}?overview=full&geometries=geojson"
    try:
        resp = requests.get(url)
        data = resp.json()
        if data['code'] == 'Ok':
            coords = [(lat, lon) for lon, lat in data['routes'][0]['geometry']['coordinates']]
            folium.PolyLine(coords, color="red", weight=2.5, dash_array="5, 5").add_to(route_map)
        else:
            folium.PolyLine([current_location, start_point], color="red", weight=2.5, dash_array="5, 5").add_to(route_map)
    except Exception:
        folium.PolyLine([current_location, start_point], color="red", weight=2.5, dash_array="5, 5").add_to(route_map)

    # Adjust the map to fit all markers (garage and bins)
    bounds = [start_point] + [(bin.latitude, bin.longitude) for bin in bins]
    route_map.fit_bounds(bounds)

    # Return the map as an HTML string
    return route_map._repr_html_()