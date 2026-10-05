# AI-Based 8-Puzzle Solver

A desktop GUI application that uses **A\* Search Algorithm** to solve the classic 8-puzzle problem. Built with Python and Tkinter — no external APIs or paid services required.

---

## 📌 Project Description

The 8-puzzle is a classic AI problem where tiles numbered 1–8 are placed on a 3×3 grid with one blank space. The goal is to rearrange tiles from an initial configuration to the goal state by sliding tiles into the blank space.

**Goal State:**
```
1  2  3
4  5  6
7  8  _
```

This application uses AI search algorithms (A\* and BFS) to find the optimal solution path.

---

## ✨ Features

- **3 Search Algorithms**: BFS, A\* with Misplaced Tiles, A\* with Manhattan Distance
- **Interactive GUI**: Click tiles to move them manually
- **Custom Puzzle Input**: Enter any valid puzzle configuration
- **Random Puzzle Generation**: Easy, Medium, and Hard difficulties
- **Solution Animation**: Watch the AI solve the puzzle step-by-step
- **Statistics Panel**: See moves, states explored, and execution time
- **Algorithm Comparison**: Compare all 3 algorithms on the same puzzle
- **AI Explanation Panel**: Understand how f(n) = g(n) + h(n) works
- **Solvability Checking**: Detects unsolvable puzzles before searching

---

## 🧠 AI Concepts Used

### A\* Search Algorithm

A\* is an informed search algorithm that uses a heuristic to guide the search.

**Formula:** `f(n) = g(n) + h(n)`

| Component | Meaning |
|-----------|---------|
| `g(n)` | Cost from the start state to the current state (number of moves made) |
| `h(n)` | Estimated cost from the current state to the goal (heuristic) |
| `f(n)` | Total estimated cost of the path through the current state |

A\* always explores the state with the **lowest f(n)** first. With an admissible heuristic (one that never overestimates), A\* guarantees finding the **optimal solution**.

### BFS (Breadth-First Search)

BFS explores all states at depth *d* before moving to depth *d+1*. It guarantees the shortest path (fewest moves) but does **not** use a heuristic, so it explores many more states than A\*.

### Manhattan Distance Heuristic

For each tile, calculate the horizontal distance + vertical distance from its current position to its goal position. Sum these distances for all non-blank tiles.

**Example:** If tile `5` is at position (0, 1) but should be at (1, 1), its Manhattan distance is |0-1| + |1-1| = 1.

### Misplaced Tiles Heuristic

Count the number of tiles that are **not** in their correct goal position (excluding the blank). This is a simpler but less informative heuristic than Manhattan Distance.

---

## 📁 Project Structure

```
AI_8_Puzzle_Solver/
│
├── main.py           # Application entry point
├── puzzle.py         # Puzzle state, moves, solvability, random generation
├── algorithms.py     # BFS and A* search implementations
├── heuristics.py     # Manhattan Distance and Misplaced Tiles
├── gui.py            # Tkinter GUI (board, controls, panels)
├── utils.py          # Helper functions (formatting, conversion)
├── README.md         # This file
└── requirements.txt  # Dependencies (stdlib only)
```

### File Responsibilities

| File | Purpose |
|------|---------|
| `main.py` | Creates the window and starts the app |
| `puzzle.py` | Puzzle logic: valid moves, solvability check, random puzzles, input validation |
| `algorithms.py` | BFS and A\* search with path reconstruction |
| `heuristics.py` | Manhattan Distance and Misplaced Tiles heuristic functions |
| `gui.py` | Full Tkinter interface: board, buttons, panels, animation |
| `utils.py` | Formatting helpers (state display, time formatting) |

---

## 🔧 Installation

### Prerequisites

- **Python 3.7+** (Python 3.8 or newer recommended)
- **Tkinter** (included with standard Python on Windows and macOS)

### Steps

1. Clone or download the project folder.
2. Open a terminal/command prompt in the project directory.
3. No packages to install! Everything uses Python's standard library.

If Tkinter is missing:
- **Windows**: Re-install Python and check "tcl/tk and IDLE" during setup.
- **Ubuntu/Debian**: `sudo apt-get install python3-tk`
- **Fedora**: `sudo dnf install python3-tkinter`

---

## ▶ How to Run

```bash
cd AI_8_Puzzle_Solver
python main.py
```

That's it!

---

## 📖 How to Use

1. **Start the app** with `python main.py`
2. The default puzzle is pre-loaded: `2 8 3 / 1 6 4 / 7 0 5`
3. **Select an algorithm** from the dropdown (default: A\* Manhattan)
4. Click **Solve** to find the solution
5. Use **Next Move** to step through the solution, or **Auto Solve** to animate
6. Click **Random** to generate a new puzzle at your chosen difficulty
7. Click **Enter Puzzle** to type in a custom configuration
8. Click **Compare** to benchmark all three algorithms on the same puzzle

### Manual Play

Click any tile adjacent to the blank space to swap it. Try solving the puzzle yourself!

---

## 📊 Example Input/Output

### Input
```
Initial State:
2  8  3
1  6  4
7  0  5
```

### Output (A\* Manhattan Distance)
```
Algorithm:        A* Search
Heuristic:        Manhattan Distance
Solution:         Found ✅
Moves:            5
States Explored:  7
Execution Time:   0.12 ms
```

---

## 📈 Algorithm Comparison

Running all three algorithms on the same puzzle demonstrates why heuristics matter:

| Algorithm | Heuristic | Moves | States Explored | Time |
|-----------|-----------|-------|-----------------|------|
| BFS | None | 5 | 20 | 0.50 ms |
| A\* | Misplaced Tiles | 5 | 8 | 0.15 ms |
| A\* | Manhattan Distance | 5 | 7 | 0.12 ms |

> **Note:** Actual results vary by puzzle. Manhattan Distance generally explores fewer states because it provides a more informed estimate.

---

## 🔮 Future Improvements

- Add IDA\* (Iterative Deepening A\*) for memory-efficient solving
- Extend to 15-puzzle (4×4 grid)
- Add DFS (Depth-First Search) for comparison
- Add solution path export
- Add puzzle state save/load
- Add visual graph of states explored over time
- Add support for custom goal states

---

## 📝 License

This project is created for educational purposes. Free to use and modify.
