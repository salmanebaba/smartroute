"""
Map generation and visualization service.
Creates interactive Folium maps for route visualization.
"""
import folium
import requests
from folium.features import DivIcon
from folium.plugins import AntPath
from typing import List, Tuple
from app.models.schemas import Bin, OptimizedRoute
from app.config import TRUCK_START


class MapGenerator:
    """Handles map generation and visualization."""
    
    @staticmethod
    def generate_map_with_route(route: OptimizedRoute, start_point: Tuple[float, float] = TRUCK_START) -> str:
        """
        Generate an interactive map showing the optimized route.
        Uses original styling with numbered markers, color coding, and animated routes.
        
        Args:
            route: Optimized route with stops
            start_point: Starting geographic point
            
        Returns:
            str: HTML representation of the map
        """
        # Create base map with clear background for markers
        m = folium.Map(location=start_point, zoom_start=15, tiles="cartodbpositron")
        
        # Create route points: start -> all stops -> end
        route_points = [start_point]
        for stop in route.stops:
            route_points.append((stop.bin.latitude, stop.bin.longitude))
        route_points.append(start_point)
        
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
                 📍 Trajet : {route.total_distance} km
            </div>'''
        m.get_root().html.add_child(folium.Element(distance_html))
        
        # 3. MARQUEURS DE BACS (Style Haute Visibilité)
        bin_locations = []  # Track bin locations for fitting bounds
        for stop in route.stops:
            b = stop.bin
            idx = stop.order
            bin_locations.append((b.latitude, b.longitude))
            
            # Logique de couleur chauffeur : Rouge = Urgent, Orange = À faire, Vert = Sur le chemin
            if b.fill_level >= 85:
                color = "#d63031"  # Rouge vif
                border = "2px solid #2d3436"
            elif b.fill_level >= 50:
                color = "#fdcb6e"  # Orange
                border = "1px solid #e17055"
            else:
                color = "#00b894"  # Vert émeraude
                border = "1px solid #55efc4"
            
            # Marqueur numérique avec indicateur de remplissage
            folium.Marker(
                [b.latitude, b.longitude],
                icon=DivIcon(html=f'''
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
            p1, p2 = route_points[i], route_points[i + 1]
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
        
        # Fit bounds to include all bins plus start point
        all_bounds = [start_point] + bin_locations + [start_point]
        if all_bounds:
            m.fit_bounds(all_bounds)
        
        return m._repr_html_()
    
    @staticmethod
    def generate_debug_map(bins: List[Bin], start_point: Tuple[float, float] = TRUCK_START) -> str:
        """
        Generate a debug map showing all bins without optimization.
        Uses the same styling as the main map.
        
        Args:
            bins: List of all bins
            start_point: Starting geographic point
            
        Returns:
            str: HTML representation of the map
        """
        m = folium.Map(location=start_point, zoom_start=15)
        
        # Add start point
        folium.Marker(
            start_point,
            popup="Dépôt Central",
            icon=folium.Icon(color='black', icon='truck', prefix='fa')
        ).add_to(m)
        
        # Add all bins without numbering
        for idx, b in enumerate(bins, 1):
            # Same color logic as main map
            if b.fill_level >= 85:
                color = "#d63031"  # Rouge vif
                border = "2px solid #2d3436"
            elif b.fill_level >= 50:
                color = "#fdcb6e"  # Orange
                border = "1px solid #e17055"
            else:
                color = "#00b894"  # Vert émeraude
                border = "1px solid #55efc4"
            
            folium.Marker(
                [b.latitude, b.longitude],
                icon=DivIcon(html=f'''
                    <div style="display: flex; flex-direction: column; align-items: center;">
                        <div style="font-size: 13pt; color: white; background: {color}; 
                             border-radius: 50%; width: 35px; height: 35px; display: flex; 
                             align-items: center; justify-content: center; border: {border};
                             box-shadow: 0px 3px 6px rgba(0,0,0,0.4); font-weight: bold;">
                             ●
                        </div>
                        <div style="background: white; border: 1px solid black; padding: 1px 4px; 
                             border-radius: 3px; font-size: 8pt; margin-top: 2px; font-weight: bold;">
                             {b.fill_level}%
                        </div>
                    </div>'''),
                tooltip=f"Bac {b.id} | Niveau: {b.fill_level}%"
            ).add_to(m)
        
        # Fit map to all bins
        all_points = [start_point] + [(b.latitude, b.longitude) for b in bins] + [start_point]
        m.fit_bounds(all_points)
        return m._repr_html_()
