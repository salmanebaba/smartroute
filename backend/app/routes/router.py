from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import HTMLResponse
from datetime import datetime

from app.data.cosmos_client import CosmosDataClient
from app.services.bin_service import BinService
from app.services.history_service import HistoryService
from app.services.route_optimizer import RouteOptimizer
from app.services.map_generator import MapGenerator
from app.services.ai_service import AIService
from app.models.schemas import Bin, OptimizedRoute, DebugData, CollectionHistory
from app.utils.constants import DEFAULT_OPTIMIZATION_STRATEGY, OPTIMIZATION_STRATEGIES
from app.config import TRUCK_START

router = APIRouter()

data_client = CosmosDataClient()
bin_service = BinService(data_client)
history_service = HistoryService(data_client)
ai_service = AIService(data_client)

@router.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "service": "Smart Bin Route Optimizer"}

# ─── BINS & STATISTICS (STATIC ROUTES FIRST) ───

@router.get("/bins", response_model=list[Bin], tags=["Bins"])
def get_all_bins():
    return bin_service.get_all_bins()

@router.get("/bins/needing-collection", response_model=list[Bin], tags=["Bins"])
def get_bins_needing_collection(threshold: int = Query(70, ge=0, le=100)):
    return bin_service.get_bins_needing_collection(threshold)

@router.get("/bins/statistics", tags=["Statistics"])
def get_collection_statistics():
    return bin_service.get_collection_statistics()

@router.get("/bins/statistics/history", response_model=CollectionHistory, tags=["Statistics"])
def get_collection_history(range: str = Query("7d", pattern="^(7d|30d|90d)$")):
    return history_service.get_collection_history(range)

@router.get("/statistics/trends", tags=["Statistics"])
def get_trend_analysis(range: str = Query("7d", pattern="^(7d|30d|90d)$")):
    return history_service.get_trend_analysis(range)

# ─── AI SIMULATION & PREDICTION ───

@router.post("/ai/train", tags=["AI Prediction"])
def train_ai_model(days: int = Query(10)):
    return ai_service.train_predictive_model(days)

@router.get("/ai/simulate-route", tags=["AI Prediction"])
def get_simulated_route(target_date: str = Query(..., description="ISO datetime")):
    target_dt = datetime.fromisoformat(target_date.replace('Z', '+00:00'))
    all_bins = bin_service.get_all_bins()
    
    sim_data = ai_service.simulate_future_state(all_bins, target_dt)
    simulated_bins = [Bin(**b) for b in sim_data]
    bins_to_collect = [b for b in simulated_bins if b.fill_level >= 70]
    
    if not bins_to_collect:
        return {"route": None, "simulated_bins": simulated_bins, "message": "No collections needed at this time."}
        
    route = RouteOptimizer.optimize_fill_level(bins_to_collect, TRUCK_START)
    return {"route": route, "simulated_bins": simulated_bins}

@router.get("/map/simulate", response_class=HTMLResponse, tags=["Visualization"])
def get_simulated_map(target_date: str = Query(...)):
    target_dt = datetime.fromisoformat(target_date.replace('Z', '+00:00'))
    sim_data = ai_service.simulate_future_state(bin_service.get_all_bins(), target_dt)
    bins_to_collect = [Bin(**b) for b in sim_data if b["fill_level"] >= 70]
    
    if not bins_to_collect: return MapGenerator.generate_empty_folium_map(TRUCK_START['lat'], TRUCK_START['lng'])
    
    route = RouteOptimizer.optimize_fill_level(bins_to_collect, TRUCK_START)
    return MapGenerator.generate_map_with_route(route, TRUCK_START)

# ─── ROUTING & MAPPING ───

@router.get("/route/optimize", response_model=OptimizedRoute, tags=["Route"])
def optimize_route(strategy: str = Query(DEFAULT_OPTIMIZATION_STRATEGY)):
    bins = bin_service.get_bins_needing_collection()
    if not bins: return OptimizedRoute(strategy=strategy, total_distance=0, stops=[])
    
    if strategy == "distance": return RouteOptimizer.optimize_distance(bins, TRUCK_START)
    elif strategy == "fill_level": return RouteOptimizer.optimize_fill_level(bins, TRUCK_START)
    elif strategy == "time": return RouteOptimizer.optimize_time(bins, TRUCK_START)

@router.get("/map", response_class=HTMLResponse, tags=["Visualization"])
def get_optimized_map(strategy: str = Query(DEFAULT_OPTIMIZATION_STRATEGY)):
    route = optimize_route(strategy)
    return MapGenerator.generate_map_with_route(route, TRUCK_START)

@router.get("/map/debug", response_class=HTMLResponse, tags=["Visualization"])
def get_debug_map():
        bins = bin_service.get_all_bins()
        return MapGenerator.generate_debug_map(bins, TRUCK_START)


@router.get("/debug-data", tags=["Debug"])
def get_debug_data():
    bins = bin_service.get_all_bins()
    return {"total_bins": len(bins), "bins": bins}

# ─── DYNAMIC ROUTES LAST ───

@router.get("/bins/{bin_id}", response_model=Bin, tags=["Bins"])
def get_bin_details(bin_id: str):
    try: return bin_service.get_bin_details(bin_id)
    except ValueError as e: raise HTTPException(status_code=404, detail=str(e))

@router.get("/bins/{bin_id}/history", tags=["Bins"])
def get_bin_history(bin_id: str, days: int = Query(7, ge=1, le=90)):
    return history_service.get_bin_history(bin_id, days)