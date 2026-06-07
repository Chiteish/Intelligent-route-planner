import os
import copy
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Tuple

# Import project modules
from graph import Graph, Edge
from algorithms import dijkstra, astar
from multicriteria import yens_k_shortest_paths, filter_pareto_optimal, get_path_metrics
from summary import generate_route_summary

app = FastAPI(
    title="Intelligent Route Planner API",
    description="A graph-theory backend service supporting dynamic pathfinding, traffic overlays, road closures, and Pareto-optimal alternatives.",
    version="1.0.0"
)

# Enable CORS (Cross-Origin Resource Sharing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_headers=["*"],
    allow_methods=["*"],
)

# Load base graph dataset once during startup
BASE_GRAPH = Graph()
DATASET_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'metroville.json')

if os.path.exists(DATASET_PATH):
    BASE_GRAPH.load_from_json(DATASET_PATH)
    print(f"Server Startup: Loaded base graph containing {len(BASE_GRAPH.nodes)} nodes.")
else:
    print(f"Server Startup: Error - base graph JSON dataset not found at {DATASET_PATH}")


# =====================================================================
# PYDANTIC INPUT/OUTPUT SCHEMAS
# =====================================================================

class ClosureOverride(BaseModel):
    source: str = Field(..., description="Starting node ID of closed road")
    target: str = Field(..., description="Ending node ID of closed road")

class TrafficOverride(BaseModel):
    source: str = Field(..., description="Starting node ID of congested road")
    target: str = Field(..., description="Ending node ID of congested road")
    factor: float = Field(..., description="Traffic multiplier factor (e.g. 2.5)", gt=0.0)

class RouteRequest(BaseModel):
    source: str = Field(..., example="A", description="Starting location node ID")
    destination: str = Field(..., example="E", description="Target location node ID")
    metric: str = Field("time", example="time", description="Routing optimization objective: 'time', 'distance', or 'weighted'")
    weights: Optional[Dict[str, float]] = Field(None, example={"time": 0.5, "distance": 0.5}, description="Coefficients for weighted sum objective (must sum to 1.0)")
    closures: Optional[List[ClosureOverride]] = Field(default=[], description="List of roads to temporarily close for this request")
    traffic: Optional[List[TrafficOverride]] = Field(default=[], description="List of roads to temporarily update traffic factors for this request")

class AlternativeRequest(BaseModel):
    source: str = Field(..., example="C", description="Starting location node ID")
    destination: str = Field(..., example="D", description="Target location node ID")
    K: int = Field(5, description="Number of candidate paths to generate", ge=1, le=10)


# =====================================================================
# API ROUTE ENDPOINTS
# =====================================================================

@app.post("/route", summary="Compute shortest path under dynamic overrides")
def compute_route(req: RouteRequest):
    # 1. Validate node boundaries
    if req.source not in BASE_GRAPH.nodes or req.destination not in BASE_GRAPH.nodes:
        raise HTTPException(status_code=400, detail="Invalid source or destination node ID.")

    # 2. Thread-safe copy: Construct a clean copy of the base graph for this request
    # This prevents parallel client calls from contaminating each other's traffic/closures
    graph = copy.deepcopy(BASE_GRAPH)

    # 3. Apply temporary closures
    for closure in req.closures:
        try:
            graph.toggle_road_closure(closure.source, closure.target, is_closed=True, bidirectional=True)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    # 4. Apply temporary traffic multipliers
    for t_update in req.traffic:
        try:
            graph.update_traffic(t_update.source, t_update.target, t_update.factor, bidirectional=True)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    # 5. Define weighted sum objective callback if requested
    cost_fn = None
    if req.metric == 'weighted':
        if not req.weights:
            raise HTTPException(status_code=400, detail="Weights dictionary must be provided when metric is set to 'weighted'.")
        w_time = req.weights.get('time', 0.5)
        w_dist = req.weights.get('distance', 0.5)
        # Verify sum
        if abs((w_time + w_dist) - 1.0) > 0.01:
            raise HTTPException(status_code=400, detail="Weighted sum coefficients (time + distance) must sum to 1.0.")
        
        # Pluggable weighted sum function
        cost_fn = lambda edge: w_time * edge.get_weight('time') + w_dist * edge.get_weight('distance')

    # 6. Execute pathfinder
    path, cost, _ = dijkstra(graph, req.source, req.destination, req.metric, cost_fn=cost_fn)

    if not path or cost == float('inf'):
        raise HTTPException(status_code=404, detail="No viable connection found between source and destination under current constraints.")

    # 7. Compile metrics and return response
    total_dist, total_time = get_path_metrics(graph, path)
    summary_txt = generate_route_summary(graph, path, req.metric)

    return {
        "source": req.source,
        "destination": req.destination,
        "metric": req.metric,
        "path": path,
        "total_distance_km": total_dist,
        "total_duration_minutes": total_time,
        "summary": summary_txt
    }


@app.post("/alternatives", summary="Get Pareto-optimal alternative route choices")
def get_alternatives(req: AlternativeRequest):
    if req.source not in BASE_GRAPH.nodes or req.destination not in BASE_GRAPH.nodes:
        raise HTTPException(status_code=400, detail="Invalid source or destination node ID.")

    # Run Yen's K-Shortest Paths to generate candidates based on Travel Time
    candidates = yens_k_shortest_paths(BASE_GRAPH, req.source, req.destination, K=req.K, metric='time')
    
    if not candidates:
        raise HTTPException(status_code=404, detail="No candidate paths found.")

    # Filter out dominated candidates for the Pareto-optimal frontier
    pareto_frontier = filter_pareto_optimal(candidates, BASE_GRAPH)

    # Format output list
    options = []
    for i, (path, dist, time_mins) in enumerate(pareto_frontier):
        options.append({
            "option_label": f"Option {chr(65+i)}",
            "path": path,
            "total_distance_km": dist,
            "total_duration_minutes": time_mins,
            "trade_off": "Shorter distance / Slower duration" if i == 0 and len(pareto_frontier) > 1 else "Longer distance / Faster duration" if i == 1 else "Alternative route"
        })

    return {
        "source": req.source,
        "destination": req.destination,
        "candidates_evaluated_count": len(candidates),
        "pareto_options_count": len(options),
        "options": options
    }
