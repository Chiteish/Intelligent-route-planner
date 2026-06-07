# ⚙️ Installation & Setup Guide

This guide provides step-by-step instructions to set up your environment, install the required packages, and run the **Intelligent Route Planner** on Windows, macOS, and Linux.

---

## 🐍 Python Setup (Recommended for Visual Simulation)

The Python environment runs the core routing engine, CLI interface, and Matplotlib-based visualizations.

### 1. Prerequisites
* **Python 3.8 or higher** must be installed on your system. 
* Verify your python installation in the terminal:
  ```bash
  python --version
  ```

### 2. Creating a Virtual Environment
A virtual environment isolates this project's dependencies from your global system.

* **Windows (PowerShell):**
  ```powershell
  python -m venv .venv
  .venv\Scripts\Activate.ps1
  ```
* **Windows (Command Prompt):**
  ```cmd
  python -m venv .venv
  .venv\Scripts\activate.bat
  ```
* **macOS / Linux:**
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  ```

### 3. Installing Required Libraries
With the virtual environment activated, install the external dependencies listed in `requirements.txt`:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### What These Libraries Do:
1. **`matplotlib`**: Handles drawing coordinates, generating 2D graphs, and saving route path PNGs.
2. **`networkx`**: A mathematical graph-theory library used to model nodes and edges and compute spring-layouts.
3. **`colorama`**: Formats terminal text with colors (e.g., green for success, red for errors) to make the CLI highly readable on Windows cmd/PowerShell.

### 4. Running the Python Application
Execute the entry point script from the project root directory:
```bash
python main.py
```

---

## 💻 C++ Setup (For System Performance Core)

If you compile and run the parallel high-performance C++ implementation inside the `cpp/` folder:

### 1. Prerequisites
A compiler supporting **C++17 or higher** is required.
* **Windows:** Install **MinGW-w64** (g++) or **Microsoft Visual Studio Build Tools** (MSVC).
* **macOS:** Install Xcode Command Line Tools: `xcode-select --install` (which installs clang++).
* **Linux:** Install build tools: `sudo apt install build-essential` (which installs g++).

### 2. Compilation Commands
Navigate to the `cpp/` directory and compile using `g++` or `clang++`:

* **Windows (MinGW/g++):**
  ```bash
  g++ -std=c++17 -O3 src/main.cpp src/graph.cpp src/heap.cpp src/algorithms.cpp -o route_planner.exe
  ```
* **macOS / Linux (g++/clang++):**
  ```bash
  g++ -std=c++17 -O3 src/main.cpp src/graph.cpp src/heap.cpp src/algorithms.cpp -o route_planner
  ```

### 3. Execution Commands
Run the compiled binary:
* **Windows:**
  ```cmd
  .\route_planner.exe
  ```
* **macOS / Linux:**
  ```bash
  ./route_planner
  ```

---

## 📋 Platform Commands Cheat Sheet

| Task | Windows (PowerShell) | macOS / Linux |
| :--- | :--- | :--- |
| **Verify Python** | `python --version` | `python3 --version` |
| **Create Venv** | `python -m venv .venv` | `python3 -m venv .venv` |
| **Activate Venv** | `.venv\Scripts\Activate.ps1` | `source .venv/bin/activate` |
| **Install Packages** | `pip install -r requirements.txt` | `pip3 install -r requirements.txt` |
| **Run Python Engine** | `python main.py` | `python3 main.py` |
| **Verify C++ Compiler**| `g++ --version` | `g++ --version` or `clang++ --version` |
| **Compile C++ Code** | `g++ -std=c++17 -O3 src/main.cpp -o route_planner.exe` | `g++ -std=c++17 -O3 src/main.cpp -o route_planner` |
| **Run C++ Binary** | `.\route_planner.exe` | `./route_planner` |
