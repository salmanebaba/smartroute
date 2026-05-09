"""
API routes for the Smart Bin Route Optimizer.
"""
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import HTMLResponse

from app.data.cosmos_client import CosmosDataClient
from app.services.bin_service import BinService
from app.services.route_optimizer import RouteOptimizer
from app.services.map_generator import MapGenerator
from app.models.schemas import Bin, OptimizedRoute, DebugData
from app.utils.constants import DEFAULT_OPTIMIZATION_STRATEGY, OPTIMIZATION_STRATEGIES
from app.config import TRUCK_START

router = APIRouter()

# Initialize services (in a real app, use dependency injection)
data_client = CosmosDataClient()
bin_service = BinService(data_client)


@router.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "Smart Bin Route Optimizer"}


@router.get("/bins", response_model=list[Bin], tags=["Bins"])
def get_all_bins():
    """
    Get all bins with their current telemetry data.
    
    Returns:
        List of all bins with location and fill level
    """
    try:
        return bin_service.get_all_bins()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/bins/needing-collection", response_model=list[Bin], tags=["Bins"])
def get_bins_needing_collection(threshold: int = Query(70, ge=0, le=100)):
    """
    Get bins that need collection (above threshold).
    
    Args:
        threshold: Fill level threshold (default: 70%)
        
    Returns:
        List of bins needing collection
    """
    try:
        return bin_service.get_bins_needing_collection(threshold)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/bins/{bin_id}", response_model=Bin, tags=["Bins"])
def get_bin_details(bin_id: str):
    """
    Get detailed information for a specific bin.
    
    Args:
        bin_id: The bin identifier
        
    Returns:
        Bin details with current fill level
    """
    try:
        return bin_service.get_bin_details(bin_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/bins/statistics", tags=["Bins"])
def get_collection_statistics():
    """
    Get statistics about bin collection needs.
    
    Returns:
        Statistics including total bins, bins needing collection, etc.
    """
    try:
        return bin_service.get_collection_statistics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/route/optimize", response_model=OptimizedRoute, tags=["Route"])
def optimize_route(strategy: str = Query(DEFAULT_OPTIMIZATION_STRATEGY, enum=list(OPTIMIZATION_STRATEGIES.keys()))):
    """
    Generate an optimized collection route.
    
    Args:
        strategy: Optimization strategy ('distance', 'fill_level', or 'time')
        
    Returns:
        Optimized route with all stops
    """
    try:
        bins_to_collect = bin_service.get_bins_needing_collection()
        
        if not bins_to_collect:
            return OptimizedRoute(strategy=strategy, total_distance=0, stops=[])
        
        if strategy == "distance":
            return RouteOptimizer.optimize_distance(bins_to_collect, TRUCK_START)
        elif strategy == "fill_level":
            return RouteOptimizer.optimize_fill_level(bins_to_collect, TRUCK_START)
        elif strategy == "time":
            return RouteOptimizer.optimize_time(bins_to_collect, TRUCK_START)
        else:
            raise ValueError(f"Unknown strategy: {strategy}")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/map", response_class=HTMLResponse, tags=["Visualization"])
def get_optimized_map(strategy: str = Query(DEFAULT_OPTIMIZATION_STRATEGY, enum=list(OPTIMIZATION_STRATEGIES.keys()))):
    """
    Get interactive map with optimized route.
    
    Args:
        strategy: Optimization strategy
        
    Returns:
        HTML map showing the optimized route
    """
    try:
        bins_to_collect = bin_service.get_bins_needing_collection()
        
        if not bins_to_collect:
            # Return map with just start point if no bins to collect
            route = OptimizedRoute(strategy=strategy, total_distance=0, stops=[])
        else:
            if strategy == "distance":
                route = RouteOptimizer.optimize_distance(bins_to_collect, TRUCK_START)
            elif strategy == "fill_level":
                route = RouteOptimizer.optimize_fill_level(bins_to_collect, TRUCK_START)
            elif strategy == "time":
                route = RouteOptimizer.optimize_time(bins_to_collect, TRUCK_START)
            else:
                raise ValueError(f"Unknown strategy: {strategy}")
        
        return MapGenerator.generate_map_with_route(route, TRUCK_START)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/map/debug", response_class=HTMLResponse, tags=["Visualization"])
def get_debug_map():
    """
    Get debug map showing all bins without optimization.
    
    Returns:
        HTML map showing all bins
    """
    try:
        all_bins = bin_service.get_all_bins()
        return MapGenerator.generate_debug_map(all_bins, TRUCK_START)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/debug-data", response_model=DebugData, tags=["Debug"])
def get_debug_data():
    """
    Get all debug data (all bins with telemetry).
    
    Returns:
        Debug data with all bins and their current state
    """
    try:
        bins = bin_service.get_all_bins()
        return DebugData(total_bins=len(bins), bins=bins)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
