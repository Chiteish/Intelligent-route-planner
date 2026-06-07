# 🧠 Graph Algorithms Interview Preparation Guide

This document is designed to help you prepare for technical interviews by reviewing the core graph theory, priority queue concepts, and algorithmic decisions implemented in the **Intelligent Route Planner** project.

---

## ⏱️ Core Time & Space Complexity Reference

| Algorithm / Operation | Data Structure | Time Complexity (Average/Worst) | Space Complexity | Real-World Suitability |
| :--- | :--- | :--- | :--- | :--- |
| **Graph Representation** | Adjacency List | $O(V + E)$ | $O(V + E)$ | Excellent for sparse road networks. |
| **Graph Representation** | Adjacency Matrix | $O(1)$ edge check | $O(V^2)$ | Poor for sparse networks; wastes memory. |
| **BFS Traversal** | Queue (FIFO) | $O(V + E)$ | $O(V)$ | Finding unweighted shortest paths. |
| **DFS Traversal** | Stack / Recursion | $O(V + E)$ | $O(V)$ | Cycle detection, topological sorting. |
| **Dijkstra's Algorithm** | Unoptimized Array | $O(V^2)$ | $O(V)$ | Disastrous for large road networks. |
| **Dijkstra's Algorithm** | **Min-Heap (Custom)** | **$O((V + E) \log V)$** | $O(V)$ | Industry standard for non-negative weights. |
| **A\* Search** | Min-Heap + Heuristic | $O((V + E) \log V)$ | $O(V)$ | Search-space optimized (standard GPS routing). |
| **Bellman-Ford** | Edge Relaxation Loop| $O(V \cdot E)$ | $O(V)$ | Detects negative weight cycles. |

*Where $V$ represents the number of Vertices (intersections) and $E$ represents the number of Edges (roads).*

---

## 💬 Frequently Asked Interview Questions (FAQ)

### 1. Why did you choose an Adjacency List over an Adjacency Matrix to represent the road network?
* **Answer:** Road networks are **sparse graphs**. In a real city, an intersection is typically connected to only 3 to 4 other intersections ($E \approx 4V$). 
  * An **Adjacency Matrix** takes $O(V^2)$ space regardless of the number of edges. For $10,000$ intersections, it would require $100,000,000$ elements, most of which would be empty (zeros).
  * An **Adjacency List** stores only the actual connections, taking $O(V + E)$ space. For $10,000$ intersections and $40,000$ roads, we store exactly $50,000$ objects, saving massive amounts of RAM and making iteration over neighbors faster ($O(\text{deg}(v))$ vs $O(V)$).

### 2. What is the role of a Priority Queue in Dijkstra's algorithm, and why did you build a custom Min-Heap?
* **Answer:** In each step of Dijkstra's algorithm, we need to extract the unvisited node with the minimum tentative distance.
  * Searching an unsorted list takes $O(V)$ time, leading to a total runtime of $O(V^2)$.
  * A **Min-Heap** lets us extract the minimum element in $O(\log V)$ time.
  * **Why Custom?** Built-in heaps (like Python's `heapq` or C++'s `std::priority_queue`) do not support an efficient **Decrease-Key** operation in $O(\log V)$ time. When we relax an edge and find a shorter path to an already queued node, we must update its priority. In a standard heap, locating the element takes $O(N)$ linear time. 
  * My custom heap resolves this by maintaining a **position lookup hash map** mapping node IDs to their current indices in the heap array. This allows us to look up any node in $O(1)$ and perform **Decrease-Key** in **$O(\log V)$**, ensuring a true $O((V + E) \log V)$ time complexity.

### 3. How does A* Search differ from Dijkstra's Algorithm? What makes a heuristic "admissible"?
* **Answer:** Dijkstra's algorithm is a uniform-cost search. It expands nodes in all directions radially, which guarantees the shortest path but wastes computation on nodes heading away from the target.
  * A* Search incorporates domain knowledge by adding a heuristic estimate $h(n)$ to the actual path cost $g(n)$, selecting nodes that minimize:
    $$f(n) = g(n) + h(n)$$
  * **Admissibility:** A heuristic is **admissible** if it never overestimates the actual cost to reach the destination ($h(n) \le h^*(n)$). If $h(n)$ were to overestimate, the search might prune a path that is actually shorter, losing the guarantee of optimality. 
  * In this project, I used **Euclidean Distance** (straight-line distance). Since a straight line is the shortest distance between two points, it is mathematically guaranteed to be admissible. For the "time" metric, I divided the Euclidean distance by the maximum speed limit in the network to ensure admissibility.

### 4. What happens if a graph contains negative edge weights? Can Dijkstra's algorithm handle them?
* **Answer:** **No, Dijkstra's algorithm cannot handle negative edge weights.**
  * Dijkstra is a greedy algorithm. Once a node is extracted from the priority queue and marked as visited, Dijkstra assumes its shortest path is finalized and never processes it again.
  * If a negative edge weight is present, it might reveal a shorter path *after* a node has been visited. Dijkstra will miss this, leading to incorrect calculations.
  * **Solution:** To handle negative edge weights, we must use the **Bellman-Ford Algorithm**, which relaxes all edges $V-1$ times. It can also detect if the graph has a **negative cycle** (a cycle whose sum of edge weights is negative, which allows a path to infinitely decrease in cost).
