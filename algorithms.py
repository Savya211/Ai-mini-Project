"""
algorithms.py - Search Algorithms for the 8-Puzzle

Implements:
  1. BFS (Breadth-First Search) - uninformed baseline.
  2. A* Search               - informed search using a heuristic.

Both algorithms track the number of states explored, the solution
path, and support a visited/closed set to prevent re-expansion.
"""

import heapq
from collections import deque
import time

from puzzle import GOAL_STATE, get_neighbors, is_goal


class SearchResult:
    """Stores the result of a search algorithm run."""

    def __init__(self):
        self.path = []               # list of states from initial to goal
        self.moves = 0               # number of moves in the solution
        self.states_explored = 0     # total nodes expanded
        self.execution_time = 0.0    # time in seconds
        self.found = False           # whether a solution was found
        self.algorithm = ""          # name of the algorithm
        self.heuristic = ""          # name of the heuristic (if any)


def reconstruct_path(came_from: dict, current: tuple) -> list:
    """
    Trace back from the goal state to the initial state
    using the came_from dictionary.

    Returns a list of states from start to goal (inclusive).
    """
    path = [current]
    while current in came_from:
        current = came_from[current]
        path.append(current)
    path.reverse()
    return path


# ─────────────────────────── BFS ───────────────────────────

def bfs(initial_state: tuple) -> SearchResult:
    """
    Breadth-First Search.

    Explores states level by level. Guarantees the shortest path
    (fewest moves) but does not use a heuristic, so it may explore
    many more states than A*.

    Parameters:
        initial_state: Starting puzzle configuration.

    Returns:
        A SearchResult object with the solution details.
    """
    result = SearchResult()
    result.algorithm = "BFS"
    result.heuristic = "None"

    start_time = time.time()

    if is_goal(initial_state):
        result.path = [initial_state]
        result.moves = 0
        result.found = True
        result.execution_time = time.time() - start_time
        return result

    # Queue holds states to explore; came_from tracks the path.
    queue = deque([initial_state])
    visited = {initial_state}
    came_from = {}

    while queue:
        current = queue.popleft()
        result.states_explored += 1

        for neighbor in get_neighbors(current):
            if neighbor in visited:
                continue
            visited.add(neighbor)
            came_from[neighbor] = current

            if is_goal(neighbor):
                result.path = reconstruct_path(came_from, neighbor)
                result.moves = len(result.path) - 1
                result.found = True
                result.execution_time = time.time() - start_time
                return result

            queue.append(neighbor)

    # No solution found (should not happen for solvable puzzles)
    result.execution_time = time.time() - start_time
    return result


# ─────────────────────── A* Search ─────────────────────────

def astar(initial_state: tuple, heuristic_fn, heuristic_name: str = "Manhattan Distance") -> SearchResult:
    """
    A* Search Algorithm.

    Uses f(n) = g(n) + h(n) to guide the search.
      g(n) = cost from the start to the current state (number of moves).
      h(n) = estimated cost to the goal (heuristic).

    A* with an admissible heuristic (both Manhattan and Misplaced
    Tiles are admissible) guarantees an optimal solution.

    Parameters:
        initial_state:  Starting puzzle configuration.
        heuristic_fn:   A function that takes a state tuple and returns h(n).
        heuristic_name: Human-readable name of the heuristic.

    Returns:
        A SearchResult object with the solution details.
    """
    result = SearchResult()
    result.algorithm = "A* Search"
    result.heuristic = heuristic_name

    start_time = time.time()

    if is_goal(initial_state):
        result.path = [initial_state]
        result.moves = 0
        result.found = True
        result.execution_time = time.time() - start_time
        return result

    # Priority queue entries: (f, counter, g, state)
    # The counter is a tie-breaker so Python never compares tuples directly.
    counter = 0
    h = heuristic_fn(initial_state)
    open_set = [(h, counter, 0, initial_state)]  # (f, counter, g, state)
    heapq.heapify(open_set)

    # Best known g-cost to each state.
    g_score = {initial_state: 0}

    # For path reconstruction.
    came_from = {}

    while open_set:
        f, _, g, current = heapq.heappop(open_set)

        # Skip if we already found a better path to this state.
        if g > g_score.get(current, float('inf')):
            continue

        result.states_explored += 1

        if is_goal(current):
            result.path = reconstruct_path(came_from, current)
            result.moves = len(result.path) - 1
            result.found = True
            result.execution_time = time.time() - start_time
            return result

        for neighbor in get_neighbors(current):
            tentative_g = g + 1
            if tentative_g < g_score.get(neighbor, float('inf')):
                # This path to neighbor is better than any previous one.
                g_score[neighbor] = tentative_g
                came_from[neighbor] = current
                h = heuristic_fn(neighbor)
                f = tentative_g + h
                counter += 1
                heapq.heappush(open_set, (f, counter, tentative_g, neighbor))

    # No solution (should not happen for solvable puzzles)
    result.execution_time = time.time() - start_time
    return result
