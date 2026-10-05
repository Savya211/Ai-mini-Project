"""
puzzle.py - Puzzle State Representation and Logic

Handles:
  - Puzzle state representation (tuple of 9 integers)
  - Finding valid moves from a given state
  - Generating successor/neighbor states
  - Checking if a puzzle is solvable (inversion count)
  - Generating random solvable puzzles at various difficulties
"""

import random

# The goal state as a tuple (row-major order).
GOAL_STATE = (1, 2, 3, 4, 5, 6, 7, 8, 0)

# Possible moves for each position of the blank tile (index).
# For a 3x3 grid laid out as indices 0-8:
#   0 1 2
#   3 4 5
#   6 7 8
# Each entry lists the indices the blank can swap with.
MOVES = {
    0: [1, 3],
    1: [0, 2, 4],
    2: [1, 5],
    3: [0, 4, 6],
    4: [1, 3, 5, 7],
    5: [2, 4, 8],
    6: [3, 7],
    7: [4, 6, 8],
    8: [5, 7],
}


def find_blank(state: tuple) -> int:
    """Return the index of the blank tile (0) in the state."""
    return state.index(0)


def get_neighbors(state: tuple) -> list:
    """
    Generate all valid successor states from the current state.

    Returns a list of tuples, each being a new puzzle state
    obtained by swapping the blank tile with one of its neighbors.
    """
    blank = find_blank(state)
    neighbors = []
    for target in MOVES[blank]:
        # Swap blank with the target tile
        new_state = list(state)
        new_state[blank], new_state[target] = new_state[target], new_state[blank]
        neighbors.append(tuple(new_state))
    return neighbors


def count_inversions(state: tuple) -> int:
    """
    Count the number of inversions in the puzzle.

    An inversion is a pair (a, b) where a appears before b in the
    flattened puzzle, a != 0, b != 0, and a > b.
    """
    tiles = [t for t in state if t != 0]
    inversions = 0
    for i in range(len(tiles)):
        for j in range(i + 1, len(tiles)):
            if tiles[i] > tiles[j]:
                inversions += 1
    return inversions


def is_solvable(state: tuple) -> bool:
    """
    Check whether the given puzzle state is solvable.

    For a 3x3 puzzle (odd grid width), the puzzle is solvable
    if and only if the number of inversions is even.
    """
    return count_inversions(state) % 2 == 0


def is_goal(state: tuple) -> bool:
    """Check if the given state matches the goal state."""
    return state == GOAL_STATE


def generate_random_puzzle(difficulty: str = "medium") -> tuple:
    """
    Generate a random SOLVABLE puzzle of a given difficulty.

    Works by starting from the goal state and performing a number
    of random valid moves. Avoids immediate reversal to get
    meaningful shuffles.

    Difficulty levels:
      - easy:   5-10 random moves
      - medium: 15-25 random moves
      - hard:   50-100 random moves (produces harder puzzles)

    Returns:
        A solvable puzzle state as a tuple.
    """
    move_counts = {
        "easy": random.randint(5, 10),
        "medium": random.randint(15, 25),
        "hard": random.randint(50, 100),
    }
    num_moves = move_counts.get(difficulty, random.randint(15, 25))

    state = list(GOAL_STATE)
    previous_blank = -1  # track last blank position to avoid reversal

    for _ in range(num_moves):
        blank = state.index(0)
        possible = MOVES[blank][:]
        # Avoid immediately undoing the last move
        if previous_blank in possible and len(possible) > 1:
            possible.remove(previous_blank)
        target = random.choice(possible)
        previous_blank = blank
        state[blank], state[target] = state[target], state[blank]

    return tuple(state)


def validate_input(values: list) -> tuple:
    """
    Validate user-entered puzzle values.

    Parameters:
        values: A list of 9 values (strings or ints).

    Returns:
        (True, state_tuple, "") if valid,
        (False, None, error_message) if invalid.
    """
    # Check that we have exactly 9 values
    if len(values) != 9:
        return False, None, "Exactly 9 values are required."

    # Convert to integers
    int_values = []
    for v in values:
        try:
            num = int(v)
            int_values.append(num)
        except (ValueError, TypeError):
            return False, None, f"Invalid value: '{v}'. Only numbers 0-8 are allowed."

    # Check range
    for num in int_values:
        if num < 0 or num > 8:
            return False, None, f"Value {num} is out of range. Use numbers 0-8 only."

    # Check for duplicates
    if len(set(int_values)) != 9:
        seen = set()
        for num in int_values:
            if num in seen:
                return False, None, f"Duplicate value: {num}. Each number must appear exactly once."
            seen.add(num)

    state = tuple(int_values)
    return True, state, ""
