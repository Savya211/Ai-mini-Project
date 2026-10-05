"""
utils.py - Helper / Utility Functions

Contains:
  - State formatting for display
  - Timing utilities
  - Validation helpers
"""


def format_state_string(state: tuple) -> str:
    """
    Format a puzzle state tuple into a readable 3×3 grid string.

    Example output:
        2  8  3
        1  6  4
        7  0  5
    """
    rows = []
    for r in range(3):
        row = []
        for c in range(3):
            tile = state[r * 3 + c]
            if tile == 0:
                row.append("  ")
            else:
                row.append(f"{tile:2d}")
        rows.append("  ".join(row))
    return "\n".join(rows)


def format_time(seconds: float) -> str:
    """Format execution time into a human-friendly string."""
    if seconds < 0.001:
        return f"{seconds * 1_000_000:.0f} µs"
    elif seconds < 1:
        return f"{seconds * 1_000:.2f} ms"
    else:
        return f"{seconds:.3f} s"


def state_to_grid(state: tuple) -> list:
    """
    Convert a flat state tuple to a 2D grid (list of lists).

    Example:
        (1,2,3,4,5,6,7,8,0)  ->  [[1,2,3],[4,5,6],[7,8,0]]
    """
    return [list(state[i * 3:(i + 1) * 3]) for i in range(3)]


def grid_to_state(grid: list) -> tuple:
    """
    Convert a 2D grid to a flat state tuple.

    Example:
        [[1,2,3],[4,5,6],[7,8,0]]  ->  (1,2,3,4,5,6,7,8,0)
    """
    return tuple(tile for row in grid for tile in row)
