"""
heuristics.py - Heuristic Functions for A* Search

Contains two heuristics used to estimate the cost from the current
state to the goal state:
  1. Manhattan Distance - sum of horizontal + vertical distances
     of each tile from its goal position.
  2. Misplaced Tiles  - count of tiles not in their goal position.

The blank tile (0) is excluded from both calculations.
"""

# Goal state: the position each tile should occupy.
# Tile value -> (row, col) in the goal grid.
GOAL_POSITIONS = {
    1: (0, 0), 2: (0, 1), 3: (0, 2),
    4: (1, 0), 5: (1, 1), 6: (1, 2),
    7: (2, 0), 8: (2, 1), 0: (2, 2),
}


def manhattan_distance(state: tuple) -> int:
    """
    Calculate the Manhattan Distance heuristic.

    For every non-blank tile, compute:
        |current_row - goal_row| + |current_col - goal_col|

    Then return the total sum.

    Parameters:
        state: A tuple of 9 integers representing the puzzle
               in row-major order (index 0 = top-left).

    Returns:
        The total Manhattan distance (int).
    """
    distance = 0
    for index, tile in enumerate(state):
        if tile == 0:
            continue  # skip blank tile
        current_row, current_col = divmod(index, 3)
        goal_row, goal_col = GOAL_POSITIONS[tile]
        distance += abs(current_row - goal_row) + abs(current_col - goal_col)
    return distance


def misplaced_tiles(state: tuple) -> int:
    """
    Calculate the Misplaced Tiles heuristic.

    Count how many non-blank tiles are NOT in their goal position.

    Parameters:
        state: A tuple of 9 integers representing the puzzle
               in row-major order.

    Returns:
        The number of misplaced tiles (int).
    """
    goal = (1, 2, 3, 4, 5, 6, 7, 8, 0)
    count = 0
    for i in range(9):
        if state[i] != 0 and state[i] != goal[i]:
            count += 1
    return count
