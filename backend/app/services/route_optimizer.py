"""
Route optimization logic for bin collection.
Implements various strategies for optimal routing.
"""
from typing import List, Tuple
from geopy.distance import geodesic
from app.models.schemas import Bin, RouteStop, OptimizedRoute
from app.config import TRUCK_START


class RouteOptimizer:
    """Handles route optimization algorithms."""
    
    @staticmethod
    def optimize_distance(bins: List[Bin], start_point: Tuple[float, float] = TRUCK_START) -> OptimizedRoute:
        """
        Optimize route using nearest neighbor algorithm (minimize distance).
        
        Args:
            bins: List of bins to visit
            start_point: Starting geographic point (lat, lng)
            
        Returns:
            OptimizedRoute: Optimized route with stops
        """
        if not bins:
            return OptimizedRoute(strategy="distance", total_distance=0, stops=[])
        
        remaining_bins = bins.copy()
        current_location = start_point
        total_distance = 0
        stops = []
        order = 1
        
        while remaining_bins:
            # Find nearest bin
            nearest_bin = min(
                remaining_bins,
                key=lambda b: geodesic(current_location, (b.latitude, b.longitude)).km
            )
            
            distance = geodesic(current_location, (nearest_bin.latitude, nearest_bin.longitude)).km
            total_distance += distance
            
            stops.append(RouteStop(
                bin=nearest_bin,
                order=order,
                distance_from_previous=distance
            ))
            
            current_location = (nearest_bin.latitude, nearest_bin.longitude)
            remaining_bins.remove(nearest_bin)
            order += 1
        
        return OptimizedRoute(
            strategy="distance",
            total_distance=round(total_distance, 2),
            stops=stops
        )
    
    @staticmethod
    def optimize_fill_level(bins: List[Bin], start_point: Tuple[float, float] = TRUCK_START) -> OptimizedRoute:
        """
        Optimize route by prioritizing bins with highest fill levels.
        
        Args:
            bins: List of bins to visit
            start_point: Starting geographic point
            
        Returns:
            OptimizedRoute: Route prioritized by fill level
        """
        if not bins:
            return OptimizedRoute(strategy="fill_level", total_distance=0, stops=[])
        
        # Sort bins by fill level (descending)
        sorted_bins = sorted(bins, key=lambda b: b.fill_level, reverse=True)
        
        current_location = start_point
        total_distance = 0
        stops = []
        
        for order, bin_obj in enumerate(sorted_bins, 1):
            distance = geodesic(current_location, (bin_obj.latitude, bin_obj.longitude)).km
            total_distance += distance
            
            stops.append(RouteStop(
                bin=bin_obj,
                order=order,
                distance_from_previous=distance
            ))
            
            current_location = (bin_obj.latitude, bin_obj.longitude)
        
        return OptimizedRoute(
            strategy="fill_level",
            total_distance=round(total_distance, 2),
            stops=stops
        )
    
    @staticmethod
    def optimize_time(bins: List[Bin], start_point: Tuple[float, float] = TRUCK_START, avg_speed_kmh: float = 30) -> OptimizedRoute:
        """
        Optimize route by minimizing travel time (using distance and average speed).
        
        Args:
            bins: List of bins to visit
            start_point: Starting geographic point
            avg_speed_kmh: Average truck speed in km/h
            
        Returns:
            OptimizedRoute: Time-optimized route
        """
        # For now, time optimization uses the same algorithm as distance
        # In a real system, this could consider traffic patterns, etc.
        route = RouteOptimizer.optimize_distance(bins, start_point)
        estimated_time = (route.total_distance / avg_speed_kmh) * 60  # minutes
        route.strategy = "time"
        route.estimated_time = round(estimated_time, 2)
        return route
