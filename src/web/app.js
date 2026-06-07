/**
 * Intelligent Route Planner - Canvas Interaction & Simulation Controller
 */

const canvas = document.getElementById('graphCanvas');
const ctx = canvas.getContext('2d');
const selectStart = document.getElementById('startNode');
const selectTarget = document.getElementById('targetNode');
const selectAlgo = document.getElementById('algorithm');
const selectMetric = document.getElementById('metric');
const inputSpeed = document.getElementById('speed');
const labelSpeed = document.getElementById('speedValue');
const btnRun = document.getElementById('btnRun');
const btnClear = document.getElementById('btnClearPath');
const btnReset = document.getElementById('btnResetGraph');
const btnLoadDefault = document.getElementById('btnLoadDefault');
const statusMessage = document.getElementById('statusMessage');
const summaryCard = document.getElementById('summaryCard');

// State management
let nodes = [];
let edges = [];
let startNodeId = null;
let targetNodeId = null;
let selectedNode = null;
let isDragging = false;
let isDrawingEdge = false;
let edgeDrawSource = null;
let mousePos = { x: 0, y: 0 };

// Animation state
let animationSteps = [];
let animVisitedIdx = 0;
let animVisited = new Set();
let animPath = [];
let isAnimating = false;
let animationTimeout = null;

// Default city dataset (Metroville coordinates)
const defaultCity = {
    nodes: [
        {id: "A", name: "Downtown", x: 10.0, y: 10.0},
        {id: "B", name: "Central Station", x: 12.0, y: 15.0},
        {id: "C", name: "Suburbs", x: 3.0, y: 18.0},
        {id: "D", name: "Tech Park", x: 25.0, y: 12.0},
        {id: "E", name: "Airport", x: 28.0, y: 25.0},
        {id: "F", name: "Industrial Zone", x: 15.0, y: 2.0},
        {id: "G", name: "Medical Center", x: 5.0, y: 9.0},
        {id: "H", name: "Harbor", x: 2.0, y: 3.0},
        {id: "I", name: "University District", x: 8.0, y: 14.0},
        {id: "J", name: "Shopping Mall", x: 18.0, y: 8.0}
    ],
    edges: [
        {source: "A", target: "B", distance: 5.2, speedLimit: 40.0, trafficFactor: 1.5},
        {source: "A", target: "G", distance: 6.0, speedLimit: 50.0, trafficFactor: 1.0},
        {source: "A", target: "J", distance: 8.5, speedLimit: 50.0, trafficFactor: 1.8},
        {source: "B", target: "I", distance: 4.1, speedLimit: 40.0, trafficFactor: 1.2},
        {source: "I", target: "C", distance: 7.2, speedLimit: 60.0, trafficFactor: 1.0},
        {source: "G", target: "I", distance: 5.8, speedLimit: 50.0, trafficFactor: 1.1},
        {source: "G", target: "H", distance: 6.5, speedLimit: 50.0, trafficFactor: 1.0},
        {source: "H", target: "F", distance: 13.0, speedLimit: 80.0, trafficFactor: 1.0},
        {source: "F", target: "A", distance: 9.8, speedLimit: 60.0, trafficFactor: 1.3},
        {source: "F", target: "J", distance: 7.0, speedLimit: 60.0, trafficFactor: 1.1},
        {source: "J", target: "D", distance: 8.2, speedLimit: 60.0, trafficFactor: 1.4},
        {source: "B", target: "J", distance: 9.0, speedLimit: 50.0, trafficFactor: 1.3},
        {source: "C", target: "E", distance: 26.5, speedLimit: 100.0, trafficFactor: 1.0},
        {source: "D", target: "E", distance: 15.0, speedLimit: 80.0, trafficFactor: 1.2},
        {source: "B", target: "E", distance: 19.5, speedLimit: 80.0, trafficFactor: 1.4}
    ]
};

// Canvas Resizing
function resizeCanvas() {
    const rect = canvas.parentElement.getBoundingClientRect();
    canvas.width = rect.width;
    canvas.height = rect.height;
    draw();
}
window.addEventListener('resize', resizeCanvas);
setTimeout(resizeCanvas, 100);

// Helper: Calculate distance between two coordinate sets
function distance(x1, y1, x2, y2) {
    return Math.sqrt(Math.pow(x2 - x1, 2) + Math.pow(y2 - y1, 2));
}

// Convert spatial coords to fit canvas dimensions nicely
function scaleCoordinates(cityNodes) {
    const margin = 60;
    let minX = Infinity, maxX = -Infinity;
    let minY = Infinity, maxY = -Infinity;

    cityNodes.forEach(node => {
        if (node.x < minX) minX = node.x;
        if (node.x > maxX) maxX = node.x;
        if (node.y < minY) minY = node.y;
        if (node.y > maxY) maxY = node.y;
    });

    const rangeX = maxX - minX || 1;
    const rangeY = maxY - minY || 1;

    return cityNodes.map(node => {
        const scaledX = margin + ((node.x - minX) / rangeX) * (canvas.width - 2 * margin);
        // Flip Y coordinates so standard cartesian math displays right-side up
        const scaledY = canvas.height - margin - ((node.y - minY) / rangeY) * (canvas.height - 2 * margin);
        return {
            id: node.id,
            name: node.name,
            x: scaledX,
            y: scaledY
        };
    });
}

// Populate dropdown options
function updateDropdowns() {
    const prevStart = selectStart.value;
    const prevTarget = selectTarget.value;

    selectStart.innerHTML = '<option value="">Select start node...</option>';
    selectTarget.innerHTML = '<option value="">Select destination...</option>';

    nodes.forEach(node => {
        const opt1 = document.createElement('option');
        opt1.value = node.id;
        opt1.textContent = `${node.name} (${node.id})`;
        selectStart.appendChild(opt1);

        const opt2 = document.createElement('option');
        opt2.value = node.id;
        opt2.textContent = `${node.name} (${node.id})`;
        selectTarget.appendChild(opt2);
    });

    // Restore selections if valid
    if (nodes.find(n => n.id === prevStart)) selectStart.value = prevStart;
    if (nodes.find(n => n.id === prevTarget)) selectTarget.value = prevTarget;
    
    startNodeId = selectStart.value || null;
    targetNodeId = selectTarget.value || null;
}

// Load default city graph
function loadDefaultCity() {
    resetAnimation();
    
    // Position scaling requires correct canvas boundaries
    nodes = scaleCoordinates(defaultCity.nodes);
    
    // Import edges
    edges = defaultCity.edges.map(e => ({
        source: e.source,
        target: e.target,
        distance: e.distance,
        speedLimit: e.speedLimit,
        trafficFactor: e.trafficFactor
    }));

    // Generate reverse links to make the visualizer graph bidirectional
    const bidirectionalEdges = [];
    edges.forEach(e => {
        bidirectionalEdges.push(e);
        // Verify reverse edge does not already exist
        const rev = edges.find(r => r.source === e.target && r.target === e.source);
        if (!rev) {
            bidirectionalEdges.push({
                source: e.target,
                target: e.source,
                distance: e.distance,
                speedLimit: e.speedLimit,
                trafficFactor: e.trafficFactor
            });
        }
    });
    edges = bidirectionalEdges;

    updateDropdowns();
    
    // Pick logical default start/end
    if (nodes.length >= 5) {
        selectStart.value = "A";
        startNodeId = "A";
        selectTarget.value = "E";
        targetNodeId = "E";
    }
    
    statusMessage.textContent = "🏙️ Metroville graph loaded successfully.";
    draw();
}

// Reset operations
function resetGraph() {
    resetAnimation();
    nodes = [];
    edges = [];
    startNodeId = null;
    targetNodeId = null;
    updateDropdowns();
    summaryCard.innerHTML = `<div class="summary-placeholder">📊 Route report will appear here after pathfinding execution completes.</div>`;
    statusMessage.textContent = "🗑️ Graph cleared. Double-click canvas to add nodes.";
    draw();
}

function resetAnimation() {
    isAnimating = false;
    if (animationTimeout) {
        clearTimeout(animationTimeout);
        animationTimeout = null;
    }
    animVisitedIdx = 0;
    animVisited.clear();
    animPath = [];
    animationSteps = [];
    btnRun.textContent = "🚀 Run Pathfind";
    btnRun.disabled = false;
}

// Event Bindings
btnLoadDefault.addEventListener('click', loadDefaultCity);
btnReset.addEventListener('click', resetGraph);
btnClear.addEventListener('click', () => {
    resetAnimation();
    draw();
    summaryCard.innerHTML = `<div class="summary-placeholder">📊 Route report will appear here after pathfinding execution completes.</div>`;
    statusMessage.textContent = "🧹 Visual path cleared. Graph structure preserved.";
});

selectStart.addEventListener('change', (e) => {
    startNodeId = e.target.value || null;
    draw();
});
selectTarget.addEventListener('change', (e) => {
    targetNodeId = e.target.value || null;
    draw();
});
inputSpeed.addEventListener('input', (e) => {
    labelSpeed.textContent = `${e.target.value} ms`;
});

// Canvas Interactions & Mouse coordinates
function getMousePos(e) {
    const rect = canvas.getBoundingClientRect();
    return {
        x: e.clientX - rect.left,
        y: e.clientY - rect.top
    };
}

canvas.addEventListener('mousedown', (e) => {
    const pos = getMousePos(e);
    // Find clicked node
    const clicked = nodes.find(n => distance(n.x, n.y, pos.x, pos.y) < 18);

    if (e.button === 0) { // Left click
        if (e.shiftKey && clicked) { // Start drawing edge
            isDrawingEdge = true;
            edgeDrawSource = clicked;
        } else if (clicked) { // Start dragging node
            selectedNode = clicked;
            isDragging = true;
        }
    }
});

canvas.addEventListener('mousemove', (e) => {
    mousePos = getMousePos(e);
    
    if (isDragging && selectedNode) {
        selectedNode.x = mousePos.x;
        selectedNode.y = mousePos.y;
        
        // Dynamically recalculate edge lengths based on coordinates
        edges.forEach(edge => {
            if (edge.source === selectedNode.id || edge.target === selectedNode.id) {
                const sNode = nodes.find(n => n.id === edge.source);
                const tNode = nodes.find(n => n.id === edge.target);
                if (sNode && tNode) {
                    // 10 pixels on canvas = 1.0 km on map
                    edge.distance = parseFloat((distance(sNode.x, sNode.y, tNode.x, tNode.y) / 25).toFixed(1));
                }
            }
        });
        
        draw();
    } else if (isDrawingEdge) {
        draw();
    }
});

canvas.addEventListener('mouseup', (e) => {
    if (isDragging) {
        isDragging = false;
        selectedNode = null;
        updateDropdowns();
    }
    
    if (isDrawingEdge && edgeDrawSource) {
        const pos = getMousePos(e);
        const clickedTarget = nodes.find(n => distance(n.x, n.y, pos.x, pos.y) < 18);

        if (clickedTarget && clickedTarget.id !== edgeDrawSource.id) {
            // Check duplicate
            const exists = edges.find(edge => edge.source === edgeDrawSource.id && edge.target === clickedTarget.id);
            if (!exists) {
                // Calculate physical distance based on coordinates
                const calculatedDist = parseFloat((distance(edgeDrawSource.x, edgeDrawSource.y, clickedTarget.x, clickedTarget.y) / 25).toFixed(1));
                
                // Add bidirectional edge
                edges.push({
                    source: edgeDrawSource.id,
                    target: clickedTarget.id,
                    distance: Math.max(1.0, calculatedDist),
                    speedLimit: 50.0,
                    trafficFactor: 1.0
                });
                edges.push({
                    source: clickedTarget.id,
                    target: edgeDrawSource.id,
                    distance: Math.max(1.0, calculatedDist),
                    speedLimit: 50.0,
                    trafficFactor: 1.0
                });
                statusMessage.textContent = `🛣️ Added road: ${edgeDrawSource.name} ➔ ${clickedTarget.name}`;
            }
        }
        
        isDrawingEdge = false;
        edgeDrawSource = null;
        draw();
    }
});

// Double click to add node
canvas.addEventListener('dblclick', (e) => {
    const pos = getMousePos(e);
    
    // Check overlay
    const overlay = nodes.find(n => distance(n.x, n.y, pos.x, pos.y) < 30);
    if (overlay) return;

    // Generate unique ID
    const alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
    let newId = "";
    for (let char of alphabet) {
        if (!nodes.find(n => n.id === char)) {
            newId = char;
            break;
        }
    }
    if (!newId) newId = `N${nodes.length + 1}`;

    const newName = prompt("Enter Name for this Landmark:", `Intersection ${newId}`);
    if (newName === null) return; // Cancelled

    nodes.push({
        id: newId,
        name: newName || `Landmark ${newId}`,
        x: pos.x,
        y: pos.y
    });

    statusMessage.textContent = `📍 Created landmark: ${newName || newId}`;
    updateDropdowns();
    draw();
});

// Right click to toggle Start/Destination nodes
canvas.addEventListener('contextmenu', (e) => {
    e.preventDefault();
    const pos = getMousePos(e);
    const clicked = nodes.find(n => distance(n.x, n.y, pos.x, pos.y) < 18);

    if (clicked) {
        if (startNodeId === clicked.id) {
            startNodeId = null;
            selectStart.value = "";
        } else if (targetNodeId === clicked.id) {
            targetNodeId = null;
            selectTarget.value = "";
        } else if (!startNodeId) {
            startNodeId = clicked.id;
            selectStart.value = clicked.id;
        } else {
            targetNodeId = clicked.id;
            selectTarget.value = clicked.id;
        }
        draw();
    }
});

// Pathfinding Execution
btnRun.addEventListener('click', () => {
    if (!startNodeId || !targetNodeId) {
        alert("Please specify both a Start and Destination node.");
        return;
    }
    if (startNodeId === targetNodeId) {
        alert("Start and Destination nodes must be different.");
        return;
    }

    resetAnimation();
    
    const algo = selectAlgo.value;
    const metric = selectMetric.value;
    
    let result = null;
    isAnimating = true;
    btnRun.textContent = "⌛ Simulating...";
    btnRun.disabled = true;

    // Compute route
    if (algo === 'dijkstra') {
        result = dijkstraVisual(nodes, edges, startNodeId, targetNodeId, metric);
    } else if (algo === 'astar') {
        result = astarVisual(nodes, edges, startNodeId, targetNodeId, metric);
    } else if (algo === 'bfs') {
        result = bfsVisual(nodes, edges, startNodeId, targetNodeId);
    } else if (algo === 'dfs') {
        result = dfsVisual(nodes, edges, startNodeId, targetNodeId);
    }

    if (!result || result.path.length === 0) {
        statusMessage.textContent = "❌ Route planning failed. Check connections!";
        btnRun.textContent = "🚀 Run Pathfind";
        btnRun.disabled = false;
        isAnimating = false;
        summaryCard.innerHTML = `<div class="summary-placeholder" style="color: var(--danger)">❌ No viable connection found between start and target.</div>`;
        return;
    }

    // Prepare steps
    animationSteps = result.visitedOrder;
    animPath = result.path;
    
    statusMessage.textContent = `🚀 Running ${selectAlgo.options[selectAlgo.selectedIndex].text}...`;
    animatePathfind(result.cost, metric);
});

// Pathfind animation tick
function animatePathfind(totalCost, metric) {
    if (!isAnimating) return;

    const delay = parseInt(inputSpeed.value);

    if (animVisitedIdx < animationSteps.length) {
        animVisited.add(animationSteps[animVisitedIdx]);
        animVisitedIdx++;
        draw();
        animationTimeout = setTimeout(() => animatePathfind(totalCost, metric), delay);
    } else {
        // Animation finished
        isAnimating = false;
        btnRun.textContent = "🚀 Run Pathfind";
        btnRun.disabled = false;
        statusMessage.textContent = "🟢 Route optimization complete!";
        
        displaySummaryReport(animPath, totalCost, metric);
        draw();
    }
}

// Display Summary report cards
function displaySummaryReport(path, cost, metric) {
    let totalDist = 0;
    let totalTimeMins = 0;

    const steps = [];

    for (let i = 0; i < path.length - 1; i++) {
        const u = path[i];
        const v = path[i+1];
        
        const sNode = nodes.find(n => n.id === u);
        const tNode = nodes.find(n => n.id === v);
        
        const edge = edges.find(e => e.source === u && e.target === v);
        
        if (edge) {
            totalDist += edge.distance;
            totalTimeMins += getWeightJS(edge, 'time');
            
            let trafficColor = "🟢 clear";
            if (edge.trafficFactor > 1.8) trafficColor = "🔴 congested";
            else if (edge.trafficFactor > 1.3) trafficColor = "🟠 moderate";

            steps.push(`
                <div class="direction-step">
                    <strong>Step ${i+1}:</strong> Depart from <b>${sNode.name}</b> ➔ Head to <b>${tNode.name}</b> 
                    (${edge.distance.toFixed(1)} km, speed: ${edge.speedLimit} km/h, traffic: ${trafficColor})
                </div>
            `);
        }
    }

    const durationText = totalTimeMins >= 60 
        ? `${Math.floor(totalTimeMins / 60)} hr ${(totalTimeMins % 60).toFixed(1)} mins`
        : `${totalTimeMins.toFixed(1)} mins`;

    summaryCard.innerHTML = `
        <div class="route-stat-grid">
            <div class="stat-item">
                <div class="stat-val">${totalDist.toFixed(2)} km</div>
                <div class="stat-label">📏 TOTAL DISTANCE</div>
            </div>
            <div class="stat-item">
                <div class="stat-val">${durationText}</div>
                <div class="stat-label">🕒 ESTIMATED DURATION</div>
            </div>
            <div class="stat-item">
                <div class="stat-val">${path.join(' ➔ ')}</div>
                <div class="stat-label">🔀 ROUTE PATTERN</div>
            </div>
        </div>
        <div class="direction-list">
            ${steps.join('')}
        </div>
    `;
}

// Render Graph Drawing Loops
function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // 1. Draw Edges
    edges.forEach(edge => {
        const sNode = nodes.find(n => n.id === edge.source);
        const tNode = nodes.find(n => n.id === edge.target);

        if (!sNode || !tNode) return;

        // Curve lines slightly to distinguish directions
        const angle = Math.atan2(tNode.y - sNode.y, tNode.x - sNode.x);
        const controlOffset = 15;
        const midX = (sNode.x + tNode.x) / 2 + Math.cos(angle + Math.PI/2) * controlOffset;
        const midY = (sNode.y + tNode.y) / 2 + Math.sin(angle + Math.PI/2) * controlOffset;

        // Check if edge is in our computed animation path
        let onPath = false;
        if (!isAnimating && animPath.length > 1) {
            for (let i = 0; i < animPath.length - 1; i++) {
                if (animPath[i] === edge.source && animPath[i+1] === edge.target) {
                    onPath = true;
                    break;
                }
            }
        }

        ctx.beginPath();
        ctx.moveTo(sNode.x, sNode.y);
        ctx.quadraticCurveTo(midX, midY, tNode.x, tNode.y);

        if (onPath) {
            ctx.strokeStyle = '#38BDF8';  // Glowing cyan path
            ctx.lineWidth = 4.0;
        } else {
            // Draw traffic coloration
            if (edge.trafficFactor > 1.8) {
                ctx.strokeStyle = 'rgba(239, 68, 68, 0.4)';  // red traffic line
            } else if (edge.trafficFactor > 1.3) {
                ctx.strokeStyle = 'rgba(245, 158, 11, 0.4)';  // amber traffic line
            } else {
                ctx.strokeStyle = 'rgba(51, 65, 85, 0.5)';    // slate road line
            }
            ctx.lineWidth = 2.0;
        }
        ctx.stroke();

        // Draw arrowheads on roads
        const arrowLength = 10;
        const arrowAngle = Math.PI / 6;
        
        // Arrow position closer to target
        const arrowX = (midX + tNode.x) / 2;
        const arrowY = (midY + tNode.y) / 2;
        
        const arrowAngleTarget = Math.atan2(tNode.y - midY, tNode.x - midX);

        ctx.beginPath();
        ctx.moveTo(arrowX, arrowY);
        ctx.lineTo(arrowX - arrowLength * Math.cos(arrowAngleTarget - arrowAngle), arrowY - arrowLength * Math.sin(arrowAngleTarget - arrowAngle));
        ctx.lineTo(arrowX - arrowLength * Math.cos(arrowAngleTarget + arrowAngle), arrowY - arrowLength * Math.sin(arrowAngleTarget + arrowAngle));
        ctx.closePath();
        ctx.fillStyle = onPath ? '#38BDF8' : 'rgba(148, 163, 184, 0.4)';
        ctx.fill();

        // Draw edge labels (Distance / traffic multiplier)
        if (!isAnimating) {
            ctx.font = '8px monospace';
            ctx.fillStyle = '#64748B';
            ctx.fillText(`${edge.distance}km`, midX, midY - 4);
        }
    });

    // Drawing drag edge
    if (isDrawingEdge && edgeDrawSource) {
        ctx.beginPath();
        ctx.moveTo(edgeDrawSource.x, edgeDrawSource.y);
        ctx.lineTo(mousePos.x, mousePos.y);
        ctx.strokeStyle = '#A78BFA';
        ctx.lineWidth = 2.0;
        ctx.setLineDash([5, 5]);
        ctx.stroke();
        ctx.setLineDash([]);
    }

    // 2. Draw Nodes
    nodes.forEach(node => {
        ctx.beginPath();
        ctx.arc(node.x, node.y, 16, 0, 2 * Math.PI);

        // Styling based on state
        if (node.id === startNodeId) {
            ctx.fillStyle = '#10B981'; // Green Start
        } else if (node.id === targetNodeId) {
            ctx.fillStyle = '#EF4444'; // Red Target
        } else if (animPath.includes(node.id) && !isAnimating) {
            ctx.fillStyle = '#0284C7'; // Blue completed Path
        } else if (animVisited.has(node.id)) {
            ctx.fillStyle = 'rgba(167, 139, 250, 0.8)'; // Violet Visited state
        } else {
            ctx.fillStyle = '#1E293B'; // Slate base node
        }
        ctx.fill();
        
        // Node border
        ctx.lineWidth = 2.0;
        if (animPath.includes(node.id) && !isAnimating) {
            ctx.strokeStyle = '#38BDF8';
        } else {
            ctx.strokeStyle = '#334155';
        }
        ctx.stroke();

        // Node letter label
        ctx.font = 'bold 12px sans-serif';
        ctx.fillStyle = '#FFFFFF';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(node.id, node.x, node.y);

        // Landmark name
        ctx.font = '500 11px var(--font-body)';
        ctx.fillStyle = '#94A3B8';
        ctx.fillText(node.name, node.x, node.y + 28);
    });
}

// Start visualizer with default map loaded automatically
loadDefaultCity();
draw();
