# 🚀 Advanced Routing Extensions Guide

This guide details advanced concepts in graph theory, spatial computing, and route optimization. These extensions represent the technologies deployed in production systems like Google Maps, public transit planners, and fleet logistics software.

---

## 🕒 1. Time-Dependent Traffic (FIFO Networks)
In real cities, traffic congestion is not static; it changes depending on the time of day (e.g. rush hour at 8:00 AM vs. clear midnight roads). 

* **Mathematical Formulation:** 
  Edge weights are modeled as time-varying functions $w(e, t)$ mapping departure time $t$ to travel duration.
* **The FIFO Property (First-In, First-Out):**
  A time-dependent network must satisfy the FIFO property, which states that departing earlier along a road segment always guarantees arriving earlier or at the same time:
  $$t_1 < t_2 \implies t_1 + w(e, t_1) \le t_2 + w(e, t_2)$$
  If this property is violated (e.g. a faster transit vehicle departs later and overtakes you), standard Dijkstra fails, and pathfinding becomes NP-hard.
* **Pathfinding:** 
  If the FIFO property holds, Dijkstra can be adapted by evaluating edge costs dynamically at the current arrival time $t$:
  $$\text{new\_dist} = \text{dist}[u] + w(u \to v, \text{dist}[u])$$

---

## 🔀 2. Turn-Expanded Graphs (Turn Restrictions)
In a standard graph, nodes represent intersections and edges represent roads. However, this structure cannot easily model turn restrictions, such as "No left turn at this intersection between 4 PM and 7 PM", or turn delays (making a U-turn takes longer than going straight).

```text
Standard Node (Cannot restrict paths):
      [North]
         ▲
         │
[West] ──o── [East]   <-- Node 'o' allows West->North, West->East, West->South freely
         │
         ▼
      [South]

Turn-Expanded Node (Splits intersection into directional states):
      [o_North]
         ▲
         │
[o_West] ──x── [o_East]  <-- Turns are modeled as internal edges (e.g. o_West -> o_East).
         │                   We can block or add weight to the edge: o_West -> o_North.
         ▼
      [o_South]
```

* **Solution:** 
  We construct a **Turn-Expanded Graph** ($G_{TE} = (V_{TE}, E_{TE})$).
  * **Turn-Expanded Vertices ($V_{TE}$):** Vertices represent the directed *incoming state* (e.g., `(road_in, intersection)`).
  * **Turn-Expanded Edges ($E_{TE}$):** Directed links connecting incoming states to outgoing states.
* **Benefit:** 
  Turn restrictions are modeled by simply deleting the corresponding internal transition edge. Turn delays are modeled by adding weights to these internal edges.

---

## ⚡ 3. Electric Vehicle (EV) Routing (Energy Constraints)
EV routing differs from combustion engine routing because battery capacity is limited, charging takes time, and downhill slopes can recharge the battery via **regenerative braking**.

* **Energy Constraints:** 
  The vehicle's State of Charge (SoC) must remain bounded by battery limits:
  $$0 \le SoC(t) \le BatteryCapacity$$
* **Negative Edge Weights:** 
  Downhill driving yields negative costs (energy gain). Because negative weights can create negative cycles, standard Dijkstra fails.
* **Solution:** 
  We use the **Constrained Shortest Path** algorithm. We track labels of `(time, SoC)` at each node. If $SoC$ drops below 0, that path label is discarded. Charging stations are modeled as special nodes where the pathfinder can choose to halt and dynamically increase the $SoC$ label (incurring a time cost).

---

## 🚆 4. RAPTOR (Public Transit Routing)
Public transit routing (busses, subways, trains) operates on scheduled timetables. Dijkstra is highly inefficient for timetables because transit links are only available at specific time points (you cannot take a 3:00 PM train if you arrive at 3:15 PM).

* **RAPTOR Algorithm (Round-Based Public Transit Routing):**
  Instead of using priority queues and relaxing edges, RAPTOR operates in rounds:
  * **Round $k$:** Calculates the fastest way to reach stops using at most $k$ transfers.
  * **Dynamic Programming:** In each round, it scans routes that contain stops visited in the previous round, updating arrival times trip-by-trip.
* **Performance:** 
  RAPTOR runs up to **$100\text{x}$ faster** than Dijkstra on large-scale transit networks, and handles multi-criteria objectives (e.g., travel time vs. number of transfers) naturally.

---

## 🗺️ 5. OpenStreetMap (OSM) Import Pipelines
To deploy a route planner in a real city, we must parse geographic data.

* **Data Formats:** 
  OSM data is imported in XML or **PBF** (Protocolbuffer Binary Format) files. We parse:
  * `Nodes`: Geo-coordinates (lat, lng).
  * `Ways`: Ordered lists of nodes forming roads (highways, residential streets, footpaths) with tags (speed limit, one-way, street names).
* **Spatial Indexing:** 
  When a user clicks on a map, they select a coordinate (lat, lng) rather than a graph Node ID. We use a **Spatial Index** to resolve this:
  * **R-Trees / KD-Trees:** Hierarchical bounding-box data structures. They allow the backend to find the nearest graph Node ID to any GPS coordinate in **$O(\log N)$** time.

---

## 🔀 6. Diverse Alternative Routes
Yen's $K$-shortest paths can return routes that are nearly identical (e.g. detouring on a side street for 10 meters and returning to the main road). Users prefer **diverse alternatives** (entirely different highways or major avenues).

* **Alternative Evaluation Metrics:**
  To ensure routes are diverse, we evaluate the **Overlap Ratio** between path $P_A$ and $P_B$:
  $$\text{Overlap}(P_A, P_B) = \frac{\text{Shared Length}(P_A, P_B)}{\min(\text{Length}(P_A), \text{Length}(P_B))}$$
* **Penalty-Based Pathfinding:**
  To calculate diverse paths:
  1. Find the shortest path $P_1$.
  2. Temporarily increase (penalize) the weights of all edges on $P_1$ (e.g., multiply by $1.5$).
  3. Run Dijkstra again. Because the edges of the first path are penalized, the algorithm is forced to explore completely different avenues.
  4. Repeat to find $K$ diverse options.
