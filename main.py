"""
main.py - Application Entry Point

AI-Based 8-Puzzle Solver
========================
A desktop GUI application that uses A* Search, BFS, Manhattan
Distance, and Misplaced Tiles heuristics to solve the classic
8-puzzle problem.

Run with:
    python main.py
"""

import tkinter as tk
from gui import PuzzleApp


def main():
    """Create the Tkinter root window and launch the application."""
    root = tk.Tk()

    # Set window icon title and initial geometry
    root.geometry("1050x780")

    # Center window on screen
    root.update_idletasks()
    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()
    win_w = 1050
    win_h = 780
    x = (screen_w - win_w) // 2
    y = (screen_h - win_h) // 2
    root.geometry(f"{win_w}x{win_h}+{x}+{y}")

    # Create and run the app
    app = PuzzleApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
