import os
import csv

def generate_grid_csv():
    # Define file path
    data_dir = os.path.dirname(__file__)
    csv_path = os.path.join(data_dir, 'grid_network.csv')

    # CSV headers
    # source, target: Node IDs
    # distance_km: physical length
    # speed_limit_kmh: base speed limit
    # traffic_factor: 1.0 (clear) to 2.5 (heavy congestion)
    # is_toll: 1 if it has a toll, 0 otherwise
    # one_way: 1 if directed source->target only, 0 if bidirectional
    headers = ['source', 'target', 'distance_km', 'speed_limit_kmh', 'traffic_factor', 'is_toll', 'one_way']

    # Edge data rows representing a 3x3 grid (nodes named N11 to N33)
    rows = [
        # --- Horizontal Grid Roads (Grid Rows) ---
        ['N11', 'N12', '1.2', '40.0', '1.0', '0', '0'],
        ['N12', 'N13', '1.2', '40.0', '1.1', '0', '0'],
        
        ['N21', 'N22', '1.0', '45.0', '1.0', '0', '0'],
        ['N22', 'N23', '1.0', '45.0', '1.2', '0', '0'],
        
        ['N31', 'N32', '1.5', '40.0', '1.0', '0', '0'],
        ['N32', 'N33', '1.5', '40.0', '1.0', '0', '0'],

        # --- Vertical Grid Roads (Grid Columns) ---
        ['N11', 'N21', '1.1', '40.0', '1.0', '0', '0'],
        ['N21', 'N31', '1.1', '40.0', '1.0', '0', '0'],
        
        ['N12', 'N22', '1.3', '40.0', '1.5', '0', '0'],
        ['N22', 'N32', '1.3', '40.0', '1.0', '0', '0'],
        
        ['N13', 'N23', '1.0', '40.0', '1.0', '0', '0'],
        ['N23', 'N33', '1.0', '40.0', '1.0', '0', '0'],

        # --- Special Roads ---
        # 1. High-Speed Toll Avenue (Direct link across the top row to bottom row, bypassing center)
        ['N11', 'N33', '2.8', '80.0', '1.0', '1', '0'],  # is_toll = 1

        # 2. One-Way Diagonal Shortcut (Direct diagonal cut from bottom-left to top-right)
        ['N31', 'N13', '1.8', '50.0', '1.0', '0', '1']   # one_way = 1 (N31 -> N13 only)
    ]

    # Write CSV
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)

    print(f"Successfully generated grid network CSV at: data/grid_network.csv")
    print(f"   - Total intersections (nodes): 9 (N11 to N33)")
    print(f"   - Total road segments (edges): {len(rows)}")
    print(f"   - Features: High-speed Toll Avenue (N11 -> N33) & One-Way Shortcut (N31 -> N13)")

if __name__ == '__main__':
    generate_grid_csv()
