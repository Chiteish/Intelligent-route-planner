/**
 * Intelligent Route Planner - Visual Pathfinding Algorithms
 * 
 * These functions execute graph searches and return an array of "animation steps"
 * to allow the canvas to render the algorithms' exploration process in real-time.
 */

// Heuristic calculation for A* (Euclidean straight-line distance)
function getEuclideanDistanceJS(nodeA, nodeB) {
    return Math.sqrt(Math.pow(nodeA.x - nodeB.x, 2) + Math.pow(nodeA.y - nodeB.y, 2));
}

function getWeightJS(edge, metric) {
    if (metric === 'distance') {
        return edge.distance;
    } else { // time
        const effectiveSpeed = Math.max(1.0, edge.speedLimit / edge.trafficFactor);
        const timeHours = edge.distance / effectiveSpeed;
        return timeHours * 60.0; // returns minutes
    }
}

/**
 * Dijkstra's Algorithm step generator
 */
function dijkstraVisual(nodes, edges, startId, targetId, metric) {
    const visitedOrder = []; // Nodes visited in order of extraction
    const edgeRelaxations = []; // Edge traversal updates for visualization
    const distances = {};
    const parent = {};
    const unvisited = new Set();

    // Initialize distances
    nodes.forEach(node => {
        distances[node.id] = Infinity;
        parent[node.id] = null;
        unvisited.add(node.id);
    });
    distances[startId] = 0;

    while (unvisited.size > 0) {
        // Find unvisited node with minimum distance
        let currNodeId = null;
        let minDist = Infinity;
        
        unvisited.forEach(nodeId => {
            if (distances[nodeId] < minDist) {
                minDist = distances[nodeId];
                currNodeId = nodeId;
            }
        });

        // If no node is reachable, stop
        if (currNodeId === null || minDist === Infinity) break;

        // Visited step
        visitedOrder.push(currNodeId);
        unvisited.delete(currNodeId);

        // Early termination
        if (currNodeId === targetId) break;

        // Get adjacent edges
        const adjacentEdges = edges.filter(e => e.source === currNodeId);
        
        for (let edge of adjacentEdges) {
            const neighborId = edge.target;
            if (!unvisited.has(neighborId)) continue;

            const weight = getWeightJS(edge, metric);
            const alt = distances[currNodeId] + weight;

            // Log edge relaxation attempt for animation
            edgeRelaxations.push({
                from: currNodeId,
                to: neighborId,
                cost: alt,
                relaxed: alt < distances[neighborId]
            });

            if (alt < distances[neighborId]) {
                distances[neighborId] = alt;
                parent[neighborId] = currNodeId;
            }
        }
    }

    // Reconstruct path
    const path = [];
    let curr = targetId;
    if (distances[targetId] !== Infinity) {
        while (curr !== null) {
            path.push(curr);
            curr = parent[curr];
        }
        path.reverse();
    }

    return {
        visitedOrder,
        edgeRelaxations,
        path,
        cost: distances[targetId]
    };
}

/**
 * A* Search Algorithm step generator
 */
function astarVisual(nodes, edges, startId, targetId, metric) {
    const visitedOrder = [];
    const edgeRelaxations = [];
    const gScore = {};
    const fScore = {};
    const parent = {};
    const openSet = new Set();
    const closedSet = new Set();

    const targetNode = nodes.find(n => n.id === targetId);

    // Get max speed limit in graph for admissible time heuristic
    const maxSpeed = edges.reduce((max, e) => e.speedLimit > max ? e.speedLimit : max, 100);

    nodes.forEach(node => {
        gScore[node.id] = Infinity;
        fScore[node.id] = Infinity;
        parent[node.id] = null;
    });

    gScore[startId] = 0;
    
    // Heuristic estimate to target
    const startNode = nodes.find(n => n.id === startId);
    const hStart = targetNode ? getEuclideanDistanceJS(startNode, targetNode) : 0;
    const hStartAdjusted = metric === 'distance' ? hStart : (hStart / maxSpeed) * 60;
    fScore[startId] = hStartAdjusted;

    openSet.add(startId);

    while (openSet.size > 0) {
        // Get node in openSet with lowest fScore
        let currNodeId = null;
        let minF = Infinity;
        openSet.forEach(nodeId => {
            if (fScore[nodeId] < minF) {
                minF = fScore[nodeId];
                currNodeId = nodeId;
            }
        });

        if (currNodeId === null) break;

        visitedOrder.push(currNodeId);

        if (currNodeId === targetId) break;

        openSet.delete(currNodeId);
        closedSet.add(currNodeId);

        const adjacentEdges = edges.filter(e => e.source === currNodeId);

        for (let edge of adjacentEdges) {
            const neighborId = edge.target;
            if (closedSet.has(neighborId)) continue;

            const weight = getWeightJS(edge, metric);
            const tentativeG = gScore[currNodeId] + weight;

            const isRelaxed = tentativeG < gScore[neighborId];

            edgeRelaxations.push({
                from: currNodeId,
                to: neighborId,
                cost: tentativeG,
                relaxed: isRelaxed
            });

            if (isRelaxed || !openSet.has(neighborId)) {
                parent[neighborId] = currNodeId;
                gScore[neighborId] = tentativeG;
                
                const neighborNode = nodes.find(n => n.id === neighborId);
                const hVal = targetNode ? getEuclideanDistanceJS(neighborNode, targetNode) : 0;
                const hValAdjusted = metric === 'distance' ? hVal : (hVal / maxSpeed) * 60;
                
                fScore[neighborId] = tentativeG + hValAdjusted;
                openSet.add(neighborId);
            }
        }
    }

    const path = [];
    let curr = targetId;
    if (gScore[targetId] !== Infinity) {
        while (curr !== null) {
            path.push(curr);
            curr = parent[curr];
        }
        path.reverse();
    }

    return {
        visitedOrder,
        edgeRelaxations,
        path,
        cost: gScore[targetId]
    };
}

/**
 * Breadth-First Search (BFS) step generator
 */
function bfsVisual(nodes, edges, startId, targetId) {
    const visitedOrder = [];
    const edgeRelaxations = [];
    const visitedSet = new Set();
    const parent = {};
    const queue = [];

    queue.push(startId);
    visitedSet.add(startId);
    parent[startId] = null;

    while (queue.length > 0) {
        const currNodeId = queue.shift();
        visitedOrder.push(currNodeId);

        if (currNodeId === targetId) break;

        const adjacentEdges = edges.filter(e => e.source === currNodeId);

        for (let edge of adjacentEdges) {
            const neighborId = edge.target;
            
            if (!visitedSet.has(neighborId)) {
                visitedSet.add(neighborId);
                parent[neighborId] = currNodeId;
                queue.push(neighborId);
                
                edgeRelaxations.push({
                    from: currNodeId,
                    to: neighborId,
                    relaxed: true
                });
            }
        }
    }

    const path = [];
    let curr = targetId;
    if (visitedSet.has(targetId)) {
        while (curr !== null) {
            path.push(curr);
            curr = parent[curr];
        }
        path.reverse();
    }

    return {
        visitedOrder,
        edgeRelaxations,
        path,
        cost: path.length - 1 // simple hop cost
    };
}

/**
 * Depth-First Search (DFS) step generator
 */
function dfsVisual(nodes, edges, startId, targetId) {
    const visitedOrder = [];
    const edgeRelaxations = [];
    const visitedSet = new Set();
    const parent = {};
    let found = false;

    parent[startId] = null;

    function dfsRecursive(currNodeId) {
        if (found) return;

        visitedSet.add(currNodeId);
        visitedOrder.push(currNodeId);

        if (currNodeId === targetId) {
            found = true;
            return;
        }

        const adjacentEdges = edges.filter(e => e.source === currNodeId);

        for (let edge of adjacentEdges) {
            const neighborId = edge.target;
            if (!visitedSet.has(neighborId) && !found) {
                parent[neighborId] = currNodeId;
                edgeRelaxations.push({
                    from: currNodeId,
                    to: neighborId,
                    relaxed: true
                });
                dfsRecursive(neighborId);
            }
        }
    }

    dfsRecursive(startId);

    const path = [];
    let curr = targetId;
    if (visitedSet.has(targetId)) {
        while (curr !== null) {
            path.push(curr);
            curr = parent[curr];
        }
        path.reverse();
    }

    return {
        visitedOrder,
        edgeRelaxations,
        path,
        cost: path.length - 1
    };
}
