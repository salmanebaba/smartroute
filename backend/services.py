import os
import folium
import requests
from geopy.distance import geodesic
from folium.features import DivIcon
from folium.plugins import AntPath
from azure.cosmos import CosmosClient
from dotenv import load_dotenv
from models import Bin

load_dotenv()

# ── CONFIGURATION AZURE ──────────────────────────────────────────────────
URL = os.getenv("COSMOS_URI")
KEY = os.getenv("COSMOS_KEY")
DATABASE_NAME = os.getenv("DATABASE_NAME", "SmartBinDB")
CAMION_START = (33.979448, -6.866329) # Garage INPT Rabat

client = CosmosClient(URL, credential=KEY)
database = client.get_database_client(DATABASE_NAME)
container_telemetry = database.get_container_client("Telemetry")
container_inventory = database.get_container_client("BinsInventory")

# ── RÉCUPÉRATION DES DONNÉES LIVE ────────────────────────────────────────

def get_live_bins():
    """Fusionne la localisation (Inventory) et le niveau (Telemetry)."""
    try:
        inventory = list(container_inventory.read_all_items())
        live_bins = []

        for item in inventory:
            b_id = item['id']
            # Récupérer le dernier niveau de remplissage pour ce bac précis
            query = {
                "query": "SELECT TOP 1 c.fill_level FROM c WHERE c.deviceId = @devId AND c.type = 'fill_level_update' ORDER BY c._ts DESC",
                "parameters": [{"name": "@devId", "value": b_id}]
            }
            telemetry = list(container_telemetry.query_items(query=query, enable_cross_partition_query=True))
            
            fill = telemetry[0]['fill_level'] if telemetry else 0
            
            live_bins.append(Bin(
                id=b_id,
                latitude=item['location']['lat'],
                longitude=item['location']['lng'],
                fill_level=fill
            ))
        return live_bins
    except Exception as e:
        print(f"Erreur Cosmos DB: {e}")
        return []

# ── LOGIQUE DE ROUTAGE ───────────────────────────────────────────────────

def osrm_distance(start, end):
    """Calcule la distance réelle via OSRM (fallback géodésique)."""
    url = f"http://router.project-osrm.org/route/v1/driving/{start[1]},{start[0]};{end[1]},{end[0]}?overview=false"
    try:
        r = requests.get(url, timeout=2)
        data = r.json()
        if data["code"] == "Ok":
            return data["routes"][0]["distance"] / 1000
    except: pass
    return geodesic(start, end).km

def optimize_route(bins_list, start_point, strategy="distance"):
    """Implémente la logique hybride : Priorité remplissage + ramassage sur le chemin."""
    full_bins = [b for b in bins_list if b.fill_level > 0]
    if not full_bins: return [], 0.0

    if strategy == "fill_level":
        PRIORITY_THRESHOLD = 80  # Seuil critique
        NEARBY_THRESHOLD_KM = 0.3 # Détour max autorisé pour un bac non-plein

        prioritized = sorted([b for b in full_bins if b.fill_level >= PRIORITY_THRESHOLD], 
                             key=lambda b: b.fill_level, reverse=True)
        optional = [b for b in full_bins if b.fill_level < PRIORITY_THRESHOLD]

        route = prioritized[:]
        visited_ids = set(b.id for b in prioritized)
        extended_route = []

        # Logique d'insertion intelligente (Hybrid Route)
        for i in range(len(route)):
            current_bin = route[i]
            extended_route.append(current_bin)

            if i < len(route) - 1:
                next_bin = route[i + 1]
                for b in optional[:]:
                    if b.id in visited_ids: continue
                    
                    # Calculer si le bac optionnel est sur le chemin
                    d1 = geodesic((current_bin.latitude, current_bin.longitude), (b.latitude, b.longitude)).km
                    d2 = geodesic((next_bin.latitude, next_bin.longitude), (b.latitude, b.longitude)).km
                    segment_len = geodesic((current_bin.latitude, current_bin.longitude), (next_bin.latitude, next_bin.longitude)).km
                    
                    if d1 + d2 <= segment_len + NEARBY_THRESHOLD_KM:
                        extended_route.append(b)
                        visited_ids.add(b.id)
                        optional.remove(b)

        # Ajouter les bacs restants triés par proximité
        if optional:
            from_pos = (extended_route[-1].latitude, extended_route[-1].longitude) if extended_route else start_point
            optional.sort(key=lambda b: geodesic(from_pos, (b.latitude, b.longitude)).km)
            extended_route.extend(optional)

        ordered_ids = [b.id for b in extended_route]
        
    else:
        # Stratégie Distance Pure : Simple tri par proximité au point précédent
        ordered_ids = []
        current_pos = start_point
        temp_bins = full_bins[:]
        while temp_bins:
            next_b = min(temp_bins, key=lambda b: geodesic(current_pos, (b.latitude, b.longitude)).km)
            ordered_ids.append(next_b.id)
            current_pos = (next_b.latitude, next_b.longitude)
            temp_bins.remove(next_b)

    # Calcul distance totale via OSRM
    total_dist = 0.0
    current_pos = start_point
    bin_dict = {b.id: b for b in bins_list}
    for bid in ordered_ids:
        b = bin_dict[bid]
        total_dist += osrm_distance(current_pos, (b.latitude, b.longitude))
        current_pos = (b.latitude, b.longitude)
    total_dist += osrm_distance(current_pos, start_point)

    return ordered_ids, round(total_dist, 2)

# ── GÉNÉRATION DE LA CARTE ──────────────────────────────────────────────

def generate_map_with_route(start_point, strategy="distance"):
    """Génère une carte optimisée pour la navigation chauffeur avec un style haute visibilité."""
    bins_data = get_live_bins()
    ordered_ids, total_dist = optimize_route(bins_data, start_point, strategy)
    
    # Utilisation d'un fond de carte plus clair pour faire ressortir les marqueurs
    m = folium.Map(location=start_point, zoom_start=15)
    bin_dict = {b.id: b for b in bins_data}
    route_points = [start_point] + [(bin_dict[bid].latitude, bin_dict[bid].longitude) for bid in ordered_ids] + [start_point]

    # 1. STYLE DU GARAGE (Point de départ/arrivée)
    folium.Marker(
        start_point, 
        popup="Dépôt Central", 
        icon=folium.Icon(color='black', icon='truck', prefix='fa')
    ).add_to(m)

    # 2. LABEL DE DISTANCE (Style "Dashboard" flottant)
    distance_html = f'''
        <div style="position: fixed; top: 70px; right: 20px; z-index: 1000; 
             background: #2c3e50; color: white; padding: 12px; border-radius: 8px;
             font-family: Arial; font-weight: bold; box-shadow: 2px 2px 10px rgba(0,0,0,0.3);
             border: 2px solid #3498db;">
             📍 Trajet : {total_dist} km
        </div>'''
    m.get_root().html.add_child(folium.Element(distance_html))

    # 3. MARQUEURS DE BACS (Style Haute Visibilité)
    for idx, b_id in enumerate(ordered_ids, 1):
        b = bin_dict[b_id]
        
        # Logique de couleur chauffeur : Rouge = Urgent, Orange = À faire, Vert = Sur le chemin
        if b.fill_level >= 85:
            color = "#d63031" # Rouge vif
            border = "2px solid #2d3436"
        elif b.fill_level >= 50:
            color = "#fdcb6e" # Orange
            border = "1px solid #e17055"
        else:
            color = "#00b894" # Vert émeraude
            border = "1px solid #55efc4"

        # Marqueur numérique avec indicateur de remplissage
        folium.Marker(
            [b.latitude, b.longitude],
            icon=folium.DivIcon(html=f'''
                <div style="display: flex; flex-direction: column; align-items: center;">
                    <div style="font-size: 13pt; color: white; background: {color}; 
                         border-radius: 50%; width: 35px; height: 35px; display: flex; 
                         align-items: center; justify-content: center; border: {border};
                         box-shadow: 0px 3px 6px rgba(0,0,0,0.4); font-weight: bold;">
                         {idx}
                    </div>
                    <div style="background: white; border: 1px solid black; padding: 1px 4px; 
                         border-radius: 3px; font-size: 8pt; margin-top: 2px; font-weight: bold;">
                         {b.fill_level}%
                    </div>
                </div>'''),
            tooltip=f"Bac {b.id} | Niveau: {b.fill_level}%"
        ).add_to(m)

    # 4. TRACÉ DE ROUTE (AntPath bleu pour la direction)
    for i in range(len(route_points) - 1):
        p1, p2 = route_points[i], route_points[i+1]
        url = f"http://router.project-osrm.org/route/v1/driving/{p1[1]},{p1[0]};{p2[1]},{p2[0]}?overview=full&geometries=geojson"
        try:
            r = requests.get(url, timeout=3)
            data = r.json()
            if data["code"] == "Ok":
                geom = data["routes"][0]["geometry"]["coordinates"]
                # Ligne bleue épaisse avec animation de mouvement
                AntPath(
                    [(lat, lon) for lon, lat in geom], 
                    color="#0984e3", 
                    weight=6, 
                    delay=600,
                    opacity=0.8
                ).add_to(m)
            else:
                folium.PolyLine([p1, p2], color="#0984e3", weight=4, dash_array='10, 10').add_to(m)
        except:
            folium.PolyLine([p1, p2], color="#74b9ff", weight=4).add_to(m)

    m.fit_bounds(route_points)
    return m._repr_html_()