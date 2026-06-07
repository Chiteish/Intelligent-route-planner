# 📐 System Architecture Sketch: Advanced Route Planner

This document outlines the end-to-end system design for an production-ready route planner, integrating a **FastAPI backend (algorithms engine)** with a **React + Leaflet.js frontend (interactive map interface)**.

---

## 🏗️ 1. Core Architecture Diagram

```
  ┌────────────────────────────────────────────────────────┐
  │              REACT + LEAFLET.JS FRONTEND               │
  │  - Interactive Map (Leaflet tiles & polyline overlays) │
  │  - Search Panel (Geocoding source/target addresses)    │
  │  - Routing Profiles Selector (Fastest, Shortest, Eco)  │
  └───────────────────────────┬────────────────────────────┘
                              │ HTTP POST /api/route (JSON)
                              ▼
  ┌────────────────────────────────────────────────────────┐
  │                 FASTAPI BACKEND SERVICE                │
  │  - CORS Middleware & JSON Serialization Wrapper        │
  │  - Spatial Geocoder Resolver (LatLng ➔ Node ID mapping)│
  │  - Routing Logic Handler                               │
  └─────────────┬────────────────────────────┬─────────────┘
                │ Queries Graph DATA         │ Runs Pathfind
                ▼                            ▼
  ┌──────────────────────────┐  ┌──────────────────────────┐
  │    ROAD NETWORK GRAPH    │  │    ALGORITHMS MODULE     │
  │  - Nodes: OSM Vertices   │  │  - Dijkstra (Unguided)   │
  │  - Edges + Attributes    │  │  - A* (Heuristic Guided) │
  │    (Distance, Elevation, │  │  - Multi-Criteria        │
  │     Traffic, Speed)      │  │    (Composite Weights)   │
  └──────────────────────────┘  └──────────────────────────┘
```

---

## 🗄️ 2. Data Schema & Graph Representation

For real-world spatial planning (e.g., using OpenStreetMap data), the nodes and edges are enriched with attributes.

### A. Node Schema (Vertices)
```json
{
  "id": "osm_node_104825",
  "lat": 40.7128,
  "lng": -74.0060,
  "elevation_meters": 12.5
}
```

### B. Edge Schema (Roads with Attributes)
```json
{
  "source_id": "osm_node_104825",
  "target_id": "osm_node_104829",
  "distance_km": 0.45,
  "speed_limit_kmh": 50.0,
  "road_type": "secondary",
  "surface": "asphalt",
  "traffic_multiplier": 1.2,
  "elevation_gain_meters": 3.2,
  "safety_score": 9.5
}
```

---

## ⚡ 3. FastAPI Backend API Design

FastAPI serves as the lightweight HTTP wrapper around the C++/Python graph engine.

### A. Endpoint: `POST /api/route`
* **Description:** Calculates the optimal path between coordinates under criteria constraints.

#### Request Payload:
```json
{
  "source_coords": { "lat": 40.7128, "lng": -74.0060 },
  "destination_coords": { "lat": 40.7259, "lng": -73.9967 },
  "profile": "eco", 
  "preferences": {
    "avoid_tolls": false,
    "max_elevation_slope": 5.0
  }
}
```
*(Routing profiles: `fastest` (optimize time), `shortest` (optimize distance), `eco` (optimize fuel/elevation), `safest` (optimize safety_score)).*

#### Response Payload:
```json
{
  "status": "success",
  "metrics": {
    "total_distance_km": 2.15,
    "total_duration_minutes": 5.4,
    "total_elevation_gain_m": 4.1
  },
  "route_coordinates": [
    [40.7128, -74.0060],
    [40.7152, -74.0035],
    [40.7259, -73.9967]
  ],
  "directions": [
    { "instruction": "Head northeast on Broadway", "distance_km": 0.4 },
    { "instruction": "Turn right onto W 4th St", "distance_km": 1.75 }
  ]
}
```

---

## 🧩 4. Multi-Criteria Pathfinding Strategies

To optimize for multiple things at once (e.g., fuel economy and speed), we combine attributes into a **Composite Weight Function**.

### A. Cost Calculation Formula
For each edge $e(u, v)$, we calculate a composite cost $C$:
$$C(e) = \alpha \cdot \text{Time}(e) + \beta \cdot \text{Distance}(e) + \gamma \cdot \text{ElevationGain}(e) + \delta \cdot \text{RiskFactor}(e)$$

* **Weight Factors ($\alpha, \beta, \gamma, \delta$):** Configured based on the selected user profile:
  * **`fastest` Profile:** $\alpha = 1.0$, $\beta = 0.0$, $\gamma = 0.0$, $\delta = 0.0$ (focuses purely on time).
  * **`shortest` Profile:** $\alpha = 0.0$, $\beta = 1.0$, $\gamma = 0.0$, $\delta = 0.0$ (focuses purely on distance).
  * **`eco` Profile:** $\alpha = 0.3$, $\beta = 0.2$, $\gamma = 0.5$, $\delta = 0.0$ (penalizes uphill climbs to conserve fuel/energy).
  * **`safest` Profile:** $\alpha = 0.2$, $\beta = 0.0$, $\gamma = 0.0$, $\delta = 0.8$ (routes via roads with higher safety_scores).

---

## 🎨 5. React + Leaflet UI Frontend Structure

The frontend is built using standard React hooks and the `react-leaflet` package wrapper.

```jsx
// React Route Planner Component Layout Sketch
import React, { useState } from 'react';
import { MapContainer, TileLayer, Polyline, Marker, Popup } from 'react-leaflet';
import axios from 'axios';

export default function RoutePlanner() {
  const [start, setStart] = useState([40.7128, -74.0060]);
  const [end, setEnd] = useState([40.7259, -73.9967]);
  const [profile, setProfile] = useState('fastest');
  const [routeCoords, setRouteCoords] = useState([]);
  const [metrics, setMetrics] = useState(null);

  const calculateRoute = async () => {
    const response = await axios.post('/api/route', {
      source_coords: { lat: start[0], lng: start[1] },
      destination_coords: { lat: end[0], lng: end[1] },
      profile: profile
    });
    setRouteCoords(response.data.route_coordinates);
    setMetrics(response.data.metrics);
  };

  return (
    <div style={{ display: 'flex', height: '100vh' }}>
      {/* Sidebar Control Panel */}
      <div style={{ width: '350px', padding: '20px', zIndex: 1000, boxShadow: '2px 0 5px rgba(0,0,0,0.1)' }}>
        <h2>📍 Route Setup</h2>
        <select onChange={(e) => setProfile(e.target.value)}>
          <option value="fastest">Fastest (Time)</option>
          <option value="shortest">Shortest (Distance)</option>
          <option value="eco">Eco-Route (Elevation)</option>
        </select>
        <button onClick={calculateRoute}>Get Route</button>

        {metrics && (
          <div style={{ marginTop: '20px' }}>
            <p>📏 Distance: {metrics.total_distance_km} km</p>
            <p>🕒 Duration: {metrics.total_duration_minutes} mins</p>
            <p>⛰️ Elevation Gain: {metrics.total_elevation_gain_m} m</p>
          </div>
        )}
      </div>

      {/* Map Viewport Container */}
      <MapContainer center={[40.7128, -74.006]} zoom={13} style={{ flex: 1 }}>
        <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
        <Marker position={start}><Popup>Origin</Popup></Marker>
        <Marker position={end}><Popup>Destination</Popup></Marker>
        
        {routeCoords.length > 0 && (
          <Polyline pathOptions={{ color: 'blue', weight: 5 }} positions={routeCoords} />
        )}
      </MapContainer>
    </div>
  );
}
```
