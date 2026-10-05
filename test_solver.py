"""
Quick test script to verify all modules import correctly and
the core logic works without launching the GUI.
"""

import sys
import os

# Add project dir to path
sys.path.insert(0, os.path.dirname(__file__))

from puzzle import (
    GOAL_STATE, is_solvable, is_goal, generate_random_puzzle,
    validate_input, get_neighbors, count_inversions
)
from algorithms import bfs, astar
from heuristics import manhattan_distance, misplaced_tiles
from utils import format_state_string, format_time

print("=" * 50)
print("  AI 8-Puzzle Solver - Module Test")
print("=" * 50)

# Test 1: Already solved
print("\n--- Test 1: Already solved puzzle ---")
result = astar(GOAL_STATE, manhattan_distance, "Manhattan Distance")
assert result.found == True
assert result.moves == 0
print(f"  Moves: {result.moves}  States: {result.states_explored}  ✅")

# Test 2: 1 move puzzle
print("\n--- Test 2: One-move puzzle ---")
state = (1, 2, 3, 4, 5, 6, 7, 0, 8)
result = astar(state, manhattan_distance, "Manhattan Distance")
assert result.found == True
assert result.moves == 1
print(f"  Moves: {result.moves}  States: {result.states_explored}  ✅")

# Test 3: Default puzzle (2,8,3,1,6,4,7,0,5)
print("\n--- Test 3: Default puzzle ---")
state = (2, 8, 3, 1, 6, 4, 7, 0, 5)
assert is_solvable(state) == True
result = astar(state, manhattan_distance, "Manhattan Distance")
assert result.found == True
# Verify path reaches goal
assert result.path[-1] == GOAL_STATE
print(f"  Solvable: True")
print(f"  Moves: {result.moves}  States: {result.states_explored}  Time: {format_time(result.execution_time)}  ✅")

# Test 4: Unsolvable puzzle
print("\n--- Test 4: Unsolvable puzzle ---")
unsolvable = (1, 2, 3, 4, 5, 6, 8, 7, 0)
assert is_solvable(unsolvable) == False
print(f"  Solvable: False  ✅")

# Test 5: Invalid input
print("\n--- Test 5: Invalid input ---")
ok, _, err = validate_input(["1", "2", "3", "4", "5", "6", "7", "7", "0"])
assert ok == False
print(f"  Duplicate detected: '{err}'  ✅")

ok, _, err = validate_input(["1", "2", "3", "4", "5", "6", "7", "8", "9"])
assert ok == False
print(f"  Out of range: '{err}'  ✅")

# Test 6: Random puzzle generation
print("\n--- Test 6: Random puzzle generation ---")
for diff in ["easy", "medium", "hard"]:
    p = generate_random_puzzle(diff)
    assert is_solvable(p)
    assert len(p) == 9
    assert set(p) == set(range(9))
    print(f"  {diff.capitalize()} puzzle generated and solvable  ✅")

# Test 7: BFS
print("\n--- Test 7: BFS ---")
state = (1, 2, 3, 4, 5, 6, 7, 0, 8)
result_bfs = bfs(state)
assert result_bfs.found == True
assert result_bfs.moves == 1
print(f"  BFS moves: {result_bfs.moves}  ✅")

# Test 8: A* Misplaced
print("\n--- Test 8: A* Misplaced Tiles ---")
state = (2, 8, 3, 1, 6, 4, 7, 0, 5)
result_mis = astar(state, misplaced_tiles, "Misplaced Tiles")
assert result_mis.found == True
assert result_mis.path[-1] == GOAL_STATE
print(f"  Moves: {result_mis.moves}  States: {result_mis.states_explored}  ✅")

# Test 9: Compare all 3
print("\n--- Test 9: Algorithm Comparison ---")
state = (2, 8, 3, 1, 6, 4, 7, 0, 5)
r_bfs = bfs(state)
r_mis = astar(state, misplaced_tiles, "Misplaced Tiles")
r_man = astar(state, manhattan_distance, "Manhattan Distance")
print(f"  {'Algorithm':<25} {'Moves':>6} {'Explored':>10} {'Time':>12}")
print(f"  {'─'*25} {'─'*6} {'─'*10} {'─'*12}")
for r in [r_bfs, r_mis, r_man]:
    name = f"{r.algorithm} ({r.heuristic})"
    print(f"  {name:<25} {r.moves:>6} {r.states_explored:>10} {format_time(r.execution_time):>12}")
# All should find the same number of moves (optimal)
assert r_bfs.moves == r_mis.moves == r_man.moves
print(f"  All algorithms found optimal solution: {r_man.moves} moves  ✅")

# Test 10: Heuristic values
print("\n--- Test 10: Heuristic sanity ---")
h_man = manhattan_distance(GOAL_STATE)
h_mis = misplaced_tiles(GOAL_STATE)
assert h_man == 0
assert h_mis == 0
print(f"  Goal state Manhattan: {h_man}  Misplaced: {h_mis}  ✅")

state = (2, 8, 3, 1, 6, 4, 7, 0, 5)
h_man = manhattan_distance(state)
h_mis = misplaced_tiles(state)
print(f"  Test state Manhattan: {h_man}  Misplaced: {h_mis}  ✅")
assert h_man > 0
assert h_mis > 0

print("\n" + "=" * 50)
print("  ALL TESTS PASSED ✅")
print("=" * 50)
