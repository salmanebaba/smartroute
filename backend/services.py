import folium
import requests
from geopy.distance import geodesic
from folium.features import DivIcon
from models import Bin
from mock_data import bins, CAMION_START


def osrm_distance(start: tuple[float, float], end: tuple[float, float]) -> float:
    """Use OSRM to calculate real distance between two points."""
    url = f"http://osrm:5000/route/v1/driving/{start[1]},{start[0]};{end[1]},{end[0]}?overview=false"
    try:
        response = requests.get(url)
        data = response.json()
        if data["code"] == "Ok":
            return data["routes"][0]["distance"] / 1000  # meters -> km
    except Exception:
        pass
    return geodesic(start, end).km


def optimize_route(bins: list[Bin], start_point: tuple[float, float], strategy: str = "distance") -> tuple[list[str], float]:
    full_bins = [b for b in bins if b.fill_level > 0]

    if not full_bins:
        return [], 0.0

    if strategy == "fill_level":
        PRIORITY_THRESHOLD = 40
        NEARBY_THRESHOLD_KM = 0.3

        prioritized = sorted([b for b in full_bins if b.fill_level >= PRIORITY_THRESHOLD], key=lambda b: b.fill_level, reverse=True)
        optional = [b for b in full_bins if b.fill_level < PRIORITY_THRESHOLD]

        route = prioritized[:]
        visited_ids = set(b.id for b in prioritized)

        # Insert nearby optional bins into the route
        extended_route = []
        for i in range(len(route)):
            current_bin = route[i]
            extended_route.append(current_bin)

            if i < len(route) - 1:
                next_bin = route[i + 1]
                for b in optional[:]:
                    if b.id in visited_ids:
                        continue
                    d1 = geodesic((current_bin.latitude, current_bin.longitude), (b.latitude, b.longitude)).km
                    d2 = geodesic((next_bin.latitude, next_bin.longitude), (b.latitude, b.longitude)).km
                    segment_len = geodesic((current_bin.latitude, current_bin.longitude), (next_bin.latitude, next_bin.longitude)).km
                    if d1 + d2 <= segment_len + NEARBY_THRESHOLD_KM:
                        extended_route.append(b)
                        visited_ids.add(b.id)
                        optional.remove(b)

        # Add remaining optional bins (if any), sorted by proximity to last point
        if optional:
            from_pos = (extended_route[-1].latitude, extended_route[-1].longitude) if extended_route else start_point
            optional.sort(key=lambda b: geodesic(from_pos, (b.latitude, b.longitude)).km)
            extended_route.extend(optional)

        # Calculate total distance
        ordered_ids = []
        total_distance = 0.0
        current_pos = start_point
        for b in extended_route:
            dist = osrm_distance(current_pos, (b.latitude, b.longitude))
            total_distance += dist
            ordered_ids.append(b.id)
            current_pos = (b.latitude, b.longitude)

        total_distance += osrm_distance(current_pos, start_point)
        return ordered_ids, round(total_distance, 2)

    else:
        # Default: distance-optimized via OSRM /trip
        coords = f"{start_point[1]},{start_point[0]}"
        coords += ";" + ";".join(f"{b.longitude},{b.latitude}" for b in full_bins)

        url = f"http://osrm:5000/trip/v1/driving/{coords}?source=first&roundtrip=true&overview=false"
        try:
            response = requests.get(url)
            data = response.json()
            if data["code"] == "Ok":
                waypoints = data["waypoints"][1:]
                ordered_ids = [full_bins[wp["waypoint_index"] - 1].id for wp in waypoints]
                total_distance = data["trips"][0]["distance"] / 1000
                return ordered_ids, round(total_distance, 2)
        except Exception:
            pass

        return [b.id for b in full_bins], 0.0


def generate_map_with_route(start_point, strategy="distance"):
    ordered_ids, total_distance = optimize_route(bins, CAMION_START, strategy=strategy)
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
        url = f"http://osrm:5000/route/v1/driving/{start[1]},{start[0]};{end[1]},{end[0]}?overview=full&geometries=geojson"
        try:
            resp = requests.get(url)
            data = resp.json()
            if data["code"] == "Ok":
                coords = [(lat, lon) for lon, lat in data["routes"][0]["geometry"]["coordinates"]]
                from folium.plugins import AntPath
                AntPath(coords, color="green", weight=4, delay=800).add_to(route_map)
            else:
                folium.PolyLine([start, end], color="green", weight=2.5).add_to(route_map)
        except Exception:
            folium.PolyLine([start, end], color="green", weight=2.5).add_to(route_map)

    route_map.fit_bounds(route_points)
    return route_map._repr_html_()
