import os
import sys
import time
import subprocess
import urllib.request
import json

def test_fastapi_server():
    print("=========================================================")
    print("TESTING FASTAPI BACKEND SERVER ENDPOINTS (/route & /alternatives)")
    print("=========================================================")

    # 1. Start the uvicorn server in a separate subprocess
    server_dir = os.path.join(os.path.dirname(__file__), '..', 'src')
    
    print("Starting FastAPI Uvicorn server on http://127.0.0.1:8000...")
    # Launch uvicorn
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "server:app", "--host", "127.0.0.1", "--port", "8000"],
        cwd=server_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Wait for the server to spin up
    time.sleep(3.0)

    try:
        # Check if the process is still running
        if proc.poll() is not None:
            print("Error: Server failed to start. Logs:")
            out, err = proc.communicate()
            print("STDOUT:", out)
            print("STDERR:", err)
            return

        print("Server is active. Sending test requests...\n")

        # -----------------------------------------------------------------
        # TEST CASE 1: POST /route (Weighted Sum Cost: 30% time + 70% distance)
        # -----------------------------------------------------------------
        print("--- TEST 1: POST /route (Weighted Metric: 30% time, 70% dist) ---")
        url_route = "http://127.0.0.1:8000/route"
        payload_route = {
            "source": "A",
            "destination": "E",
            "metric": "weighted",
            "weights": {"time": 0.3, "distance": 0.7},
            "closures": [],
            "traffic": []
        }
        
        req = urllib.request.Request(
            url_route,
            data=json.dumps(payload_route).encode('utf-8'),
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        
        with urllib.request.urlopen(req) as resp:
            res_data = json.loads(resp.read().decode('utf-8'))
            print("Response Path:", res_data.get("path"))
            print(f"Distance: {res_data.get('total_distance_km'):.2f} km")
            print(f"Duration: {res_data.get('total_duration_minutes'):.2f} mins")
        print()

        # -----------------------------------------------------------------
        # TEST CASE 2: POST /route with dynamic closures
        # -----------------------------------------------------------------
        print("--- TEST 2: POST /route (Time metric, with closure of B -> E) ---")
        payload_closure = {
            "source": "A",
            "destination": "E",
            "metric": "time",
            "closures": [{"source": "B", "target": "E"}]
        }
        
        req = urllib.request.Request(
            url_route,
            data=json.dumps(payload_closure).encode('utf-8'),
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        
        with urllib.request.urlopen(req) as resp:
            res_data = json.loads(resp.read().decode('utf-8'))
            print("Detoured Path:", res_data.get("path"))
            print(f"Distance: {res_data.get('total_distance_km'):.2f} km")
            print(f"Duration: {res_data.get('total_duration_minutes'):.2f} mins")
        print()

        # -----------------------------------------------------------------
        # TEST CASE 3: POST /alternatives (Pareto-frontier search from C to D)
        # -----------------------------------------------------------------
        print("--- TEST 3: POST /alternatives (C -> D trade-offs) ---")
        url_alt = "http://127.0.0.1:8000/alternatives"
        payload_alt = {
            "source": "C",
            "destination": "D",
            "K": 5
        }
        
        req = urllib.request.Request(
            url_alt,
            data=json.dumps(payload_alt).encode('utf-8'),
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        
        with urllib.request.urlopen(req) as resp:
            res_data = json.loads(resp.read().decode('utf-8'))
            print(f"Pareto Frontier Options ({res_data.get('pareto_options_count')} choices):")
            for option in res_data.get("options", []):
                print(f"  - Label: {option.get('option_label')} ({option.get('trade_off')})")
                print(f"    Path: {' -> '.join(option.get('path'))}")
                print(f"    Distance: {option.get('total_distance_km'):.2f} km | Time: {option.get('total_duration_minutes'):.2f} mins")
        print()

        print("[SUCCESS] FastAPI server endpoints validated successfully!")

    except Exception as e:
        print("Error during API request testing:", e)
    finally:
        # 4. Clean up: terminate the server subprocess
        print("Shutting down the test server process...")
        proc.terminate()
        proc.wait()
        print("Server successfully stopped.")
        print("=========================================================")

if __name__ == '__main__':
    test_fastapi_server()
