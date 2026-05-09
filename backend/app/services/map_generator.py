from app.models.schemas import OptimizedRoute, Bin
from typing import List, Union, Dict, Tuple
import requests

class MapGenerator:
    @staticmethod
    def generate_map_with_route(route: OptimizedRoute, truck_start: Union[Dict, Tuple]) -> str:
        try:
            import folium
            from folium.plugins import AntPath
            from folium.features import DivIcon
        except ImportError:
            return "Folium map generation failed. Check dependencies."
        
        start_lat, start_lng = truck_start['lat'] if isinstance(truck_start, dict) else truck_start[0], truck_start['lng'] if isinstance(truck_start, dict) else truck_start[1]
        start_point = (start_lat, start_lng)
        
        m = folium.Map(location=start_point, zoom_start=14, tiles="cartodbpositron")
        folium.Marker(start_point, popup="Dépôt Central", icon=folium.Icon(color='black', icon='truck', prefix='fa')).add_to(m)
        
        if not route.stops: return m._repr_html_()
        
        time_html = f"<br><span style='font-size:12px;font-weight:normal;'>⏱️ Est. Time: {route.estimated_time:.0f} min</span>" if getattr(route, 'estimated_time', None) else ""
        distance_html = f'''
            <div style="position: fixed; top: 70px; right: 20px; z-index: 1000; 
                 background: #2c3e50; color: white; padding: 12px; border-radius: 8px;
                 font-family: Arial; font-weight: bold; box-shadow: 2px 2px 10px rgba(0,0,0,0.3); border: 2px solid #3498db;">
                 📍 Trajet : {route.total_distance:.1f} km<br><span style="font-size: 12px; font-weight: normal;">Strategy: {route.strategy}</span>{time_html}
            </div>'''
        m.get_root().html.add_child(folium.Element(distance_html))
        
        bin_locations = []
        for stop in route.stops:
            b, idx = stop.bin, stop.order
            bin_locations.append((b.latitude, b.longitude))
            color, border = ("#d63031", "2px solid #2d3436") if b.fill_level >= 85 else ("#fdcb6e", "1px solid #e17055") if b.fill_level >= 50 else ("#00b894", "1px solid #55efc4")
            
            folium.Marker(
                [b.latitude, b.longitude],
                icon=DivIcon(html=f'<div style="display: flex; flex-direction: column; align-items: center;"><div style="font-size: 13pt; color: white; background: {color}; border-radius: 50%; width: 35px; height: 35px; display: flex; align-items: center; justify-content: center; border: {border}; box-shadow: 0px 3px 6px rgba(0,0,0,0.4); font-weight: bold;">{idx}</div><div style="background: white; color: black; border: 1px solid black; padding: 1px 4px; border-radius: 3px; font-size: 8pt; margin-top: 2px; font-weight: bold;">{b.fill_level}%</div></div>'),
                tooltip=f"Bac {b.id} | Niveau: {b.fill_level}%"
            ).add_to(m)
        
        route_points = [start_point] + bin_locations + [start_point]
        for i in range(len(route_points) - 1):
            p1, p2 = route_points[i], route_points[i + 1]
            try:
                r = requests.get(f"http://router.project-osrm.org/route/v1/driving/{p1[1]},{p1[0]};{p2[1]},{p2[0]}?overview=full&geometries=geojson", timeout=3)
                if r.json().get("code") == "Ok":
                    AntPath([(lat, lon) for lon, lat in r.json()["routes"][0]["geometry"]["coordinates"]], color="#0984e3", weight=6, delay=600, opacity=0.8).add_to(m)
                else: folium.PolyLine([p1, p2], color="#0984e3", weight=4).add_to(m)
            except:
                folium.PolyLine([p1, p2], color="#74b9ff", weight=4).add_to(m)
        
        m.fit_bounds([start_point] + bin_locations + [start_point])
        return m._repr_html_()

    @staticmethod
    def generate_debug_map(bins: List[Bin], truck_start: Union[Dict, Tuple]) -> str:
        """
        Generate a debug map showing all bins without optimization.
        Uses the v1 styling.
        """
        try:
            import folium
            from folium.features import DivIcon
        except ImportError:
            return MapGenerator._generate_fallback_debug_map(bins, truck_start)
        
        # Normalize location
        if isinstance(truck_start, dict):
            start_lat, start_lng = truck_start['lat'], truck_start['lng']
        else:
            start_lat, start_lng = truck_start
            
        start_point = (start_lat, start_lng)
        
        if not bins:
            return MapGenerator._generate_empty_folium_map(start_lat, start_lng)
            
        m = folium.Map(location=start_point, zoom_start=15, tiles="cartodbpositron")
        
        # Add start point
        folium.Marker(
            start_point,
            popup="Dépôt Central",
            icon=folium.Icon(color='black', icon='truck', prefix='fa')
        ).add_to(m)
        
        # Add all bins without numbering
        bin_locations = []
        for b in bins:
            bin_locations.append((b.latitude, b.longitude))
            
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
                        <div style="background: white; color: black; border: 1px solid black; padding: 1px 4px; 
                             border-radius: 3px; font-size: 8pt; margin-top: 2px; font-weight: bold;">
                             {b.fill_level}%
                        </div>
                    </div>'''),
                tooltip=f"Bac {b.id} | Niveau: {b.fill_level}%"
            ).add_to(m)
        
        # Fit map to all bins
        if bin_locations:
            m.fit_bounds([start_point] + bin_locations + [start_point])
            
        return m._repr_html_()