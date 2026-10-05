"""
gui.py - Tkinter GUI for the AI-Based 8-Puzzle Solver

Provides:
  - 3×3 interactive puzzle board with clickable tiles
  - Algorithm selection dropdown
  - Difficulty selection
  - Solve / Auto Solve / Next Move / Random / Reset / Clear / Compare buttons
  - Animation speed control
  - Statistics panel
  - AI explanation panel
  - Search information during solving
  - Algorithm comparison table
  - About Project dialog
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading

from puzzle import (
    GOAL_STATE, is_solvable, is_goal, generate_random_puzzle,
    validate_input, get_neighbors, find_blank, MOVES,
)
from algorithms import bfs, astar, SearchResult
from heuristics import manhattan_distance, misplaced_tiles
from utils import format_time, format_state_string

# ──────────────────────── Color Palette ────────────────────────
BG_COLOR       = "#1e1e2e"       # dark background
PANEL_BG       = "#282840"       # panel background
TILE_COLOR     = "#4a6fa5"       # tile fill
TILE_HOVER     = "#5a8fc5"       # tile hover
BLANK_COLOR    = "#1e1e2e"       # blank tile (matches bg)
TILE_TEXT       = "#ffffff"       # tile number color
HEADER_COLOR   = "#cdd6f4"       # header text
ACCENT_COLOR   = "#89b4fa"       # accent / links
BUTTON_BG      = "#45475a"       # button background
BUTTON_FG      = "#cdd6f4"       # button text
BUTTON_ACTIVE  = "#585b70"       # button active bg
SUCCESS_COLOR  = "#a6e3a1"       # green for success
WARNING_COLOR  = "#f9e2af"       # yellow for warnings
ERROR_COLOR    = "#f38ba8"       # red for errors
STAT_LABEL     = "#a6adc8"       # stat label color
STAT_VALUE     = "#cdd6f4"       # stat value color
BORDER_COLOR   = "#45475a"       # border / separator
GOAL_TILE      = "#40a060"       # tile color when in goal position


class PuzzleApp:
    """Main application class for the 8-Puzzle Solver GUI."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("AI-Based 8-Puzzle Solver")
        self.root.configure(bg=BG_COLOR)
        self.root.resizable(True, True)
        self.root.minsize(960, 720)

        # ── State variables ──
        self.current_state = (1, 8, 2, 0, 4, 3, 7, 6, 5)  # default initial (solvable)
        self.initial_state = self.current_state
        self.solution_path = []
        self.solution_step = 0
        self.is_solving = False
        self.auto_running = False
        self.last_result = None       # most recent SearchResult
        self.input_mode = False       # True when user is entering a puzzle
        self.tile_buttons = []        # 3×3 grid of tile button widgets
        self.input_entries = []       # 3×3 grid of Entry widgets (input mode)
        self.animation_speed = 300    # ms between auto-solve steps
        self.difficulty = "medium"

        # ── Styles ──
        self._setup_styles()

        # ── Build UI ──
        self._build_ui()

        # ── Initial board render ──
        self._update_board()

    # ================================================================
    #  STYLES
    # ================================================================
    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background=BG_COLOR)
        style.configure("Panel.TFrame", background=PANEL_BG)
        style.configure("TLabel", background=BG_COLOR, foreground=HEADER_COLOR,
                         font=("Segoe UI", 10))
        style.configure("Header.TLabel", font=("Segoe UI", 20, "bold"),
                         foreground=ACCENT_COLOR, background=BG_COLOR)
        style.configure("Sub.TLabel", font=("Segoe UI", 11),
                         foreground=STAT_LABEL, background=BG_COLOR)
        style.configure("Stat.TLabel", font=("Segoe UI", 10),
                         foreground=STAT_LABEL, background=PANEL_BG)
        style.configure("StatVal.TLabel", font=("Segoe UI", 10, "bold"),
                         foreground=STAT_VALUE, background=PANEL_BG)
        style.configure("Success.TLabel", foreground=SUCCESS_COLOR,
                         background=PANEL_BG, font=("Segoe UI", 10, "bold"))
        style.configure("Error.TLabel", foreground=ERROR_COLOR,
                         background=PANEL_BG, font=("Segoe UI", 10, "bold"))
        style.configure("TButton", font=("Segoe UI", 10), padding=6)
        style.configure("Accent.TButton", font=("Segoe UI", 10, "bold"))
        style.configure("TCombobox", font=("Segoe UI", 10))

    # ================================================================
    #  BUILD UI
    # ================================================================
    def _build_ui(self):
        # Main container with scrollable canvas for smaller screens
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # ── HEADER ──
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(header_frame, text="AI-Based 8-Puzzle Solver",
                  style="Header.TLabel").pack()
        ttk.Label(header_frame, text="Solve the 8-Puzzle using Artificial Intelligence",
                  style="Sub.TLabel").pack()

        # ── BODY: left (board + controls) | right (info panels) ──
        body = ttk.Frame(self.main_frame)
        body.pack(fill=tk.BOTH, expand=True)

        left = ttk.Frame(body)
        left.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 10))

        right = ttk.Frame(body)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # ── PUZZLE BOARD ──
        self._build_board(left)

        # ── CONTROLS ──
        self._build_controls(left)

        # ── STATUS BAR ──
        self._build_status(left)

        # ── RIGHT PANELS ──
        self._build_stats_panel(right)
        self._build_ai_panel(right)
        self._build_search_panel(right)
        self._build_comparison_panel(right)

    # ──────────────── Board ────────────────
    def _build_board(self, parent):
        board_frame = tk.Frame(parent, bg=PANEL_BG, bd=2, relief=tk.GROOVE,
                               padx=10, pady=10)
        board_frame.pack(pady=(0, 10))

        self.board_container = tk.Frame(board_frame, bg=PANEL_BG)
        self.board_container.pack()

        self.tile_buttons = []
        for r in range(3):
            row_btns = []
            for c in range(3):
                btn = tk.Button(
                    self.board_container,
                    text="", font=("Segoe UI", 28, "bold"),
                    width=3, height=1,
                    bg=TILE_COLOR, fg=TILE_TEXT,
                    activebackground=TILE_HOVER, activeforeground=TILE_TEXT,
                    relief=tk.RAISED, bd=3,
                    command=lambda r=r, c=c: self._tile_clicked(r, c),
                )
                btn.grid(row=r, column=c, padx=3, pady=3)
                row_btns.append(btn)
            self.tile_buttons.append(row_btns)

        # Step label under board
        self.step_label = ttk.Label(board_frame, text="", style="Sub.TLabel")
        self.step_label.configure(background=PANEL_BG)
        self.step_label.pack(pady=(5, 0))

    # ──────────────── Controls ────────────────
    def _build_controls(self, parent):
        ctrl = tk.Frame(parent, bg=PANEL_BG, bd=2, relief=tk.GROOVE, padx=10, pady=10)
        ctrl.pack(fill=tk.X, pady=(0, 10))

        # Row 1: Algorithm + Difficulty
        row1 = tk.Frame(ctrl, bg=PANEL_BG)
        row1.pack(fill=tk.X, pady=(0, 6))

        tk.Label(row1, text="Algorithm:", bg=PANEL_BG, fg=STAT_LABEL,
                 font=("Segoe UI", 10)).pack(side=tk.LEFT)
        self.algo_var = tk.StringVar(value="A* - Manhattan Distance")
        algo_combo = ttk.Combobox(row1, textvariable=self.algo_var,
                                   values=["A* - Manhattan Distance",
                                           "A* - Misplaced Tiles",
                                           "BFS"],
                                   state="readonly", width=24)
        algo_combo.pack(side=tk.LEFT, padx=(5, 15))

        tk.Label(row1, text="Difficulty:", bg=PANEL_BG, fg=STAT_LABEL,
                 font=("Segoe UI", 10)).pack(side=tk.LEFT)
        self.diff_var = tk.StringVar(value="Medium")
        diff_combo = ttk.Combobox(row1, textvariable=self.diff_var,
                                   values=["Easy", "Medium", "Hard"],
                                   state="readonly", width=10)
        diff_combo.pack(side=tk.LEFT, padx=(5, 0))

        # Row 2: Speed
        row2 = tk.Frame(ctrl, bg=PANEL_BG)
        row2.pack(fill=tk.X, pady=(0, 8))

        tk.Label(row2, text="Animation Speed:", bg=PANEL_BG, fg=STAT_LABEL,
                 font=("Segoe UI", 10)).pack(side=tk.LEFT)
        self.speed_var = tk.StringVar(value="300 ms")
        speed_combo = ttk.Combobox(row2, textvariable=self.speed_var,
                                    values=["100 ms", "250 ms", "300 ms",
                                            "500 ms", "1000 ms"],
                                    state="readonly", width=10)
        speed_combo.pack(side=tk.LEFT, padx=(5, 0))
        speed_combo.bind("<<ComboboxSelected>>", self._speed_changed)

        # Row 3-4: Buttons
        btn_rows = tk.Frame(ctrl, bg=PANEL_BG)
        btn_rows.pack(fill=tk.X)

        buttons_top = [
            ("🔍 Solve", self._solve),
            ("▶ Auto Solve", self._auto_solve),
            ("⏭ Next Move", self._next_move),
        ]
        buttons_bot = [
            ("🎲 Random", self._random_puzzle),
            ("↺ Reset", self._reset),
            ("✎ Enter Puzzle", self._enter_puzzle),
            ("📊 Compare", self._compare_algorithms),
        ]

        r3 = tk.Frame(btn_rows, bg=PANEL_BG)
        r3.pack(fill=tk.X, pady=(0, 4))
        for text, cmd in buttons_top:
            tk.Button(r3, text=text, command=cmd, font=("Segoe UI", 10),
                      bg=BUTTON_BG, fg=BUTTON_FG,
                      activebackground=BUTTON_ACTIVE, activeforeground=BUTTON_FG,
                      relief=tk.RAISED, bd=2, padx=8, pady=4,
                      ).pack(side=tk.LEFT, padx=2, expand=True, fill=tk.X)

        r4 = tk.Frame(btn_rows, bg=PANEL_BG)
        r4.pack(fill=tk.X)
        for text, cmd in buttons_bot:
            tk.Button(r4, text=text, command=cmd, font=("Segoe UI", 10),
                      bg=BUTTON_BG, fg=BUTTON_FG,
                      activebackground=BUTTON_ACTIVE, activeforeground=BUTTON_FG,
                      relief=tk.RAISED, bd=2, padx=8, pady=4,
                      ).pack(side=tk.LEFT, padx=2, expand=True, fill=tk.X)

        # About button
        r5 = tk.Frame(btn_rows, bg=PANEL_BG)
        r5.pack(fill=tk.X, pady=(4, 0))
        tk.Button(r5, text="ℹ About Project", command=self._show_about,
                  font=("Segoe UI", 9), bg=BUTTON_BG, fg=STAT_LABEL,
                  activebackground=BUTTON_ACTIVE, relief=tk.FLAT, padx=6, pady=2,
                  ).pack(side=tk.RIGHT)

    # ──────────────── Status Bar ────────────────
    def _build_status(self, parent):
        self.status_var = tk.StringVar(value="Ready. Select an algorithm and click Solve.")
        status_bar = tk.Label(parent, textvariable=self.status_var,
                              bg=PANEL_BG, fg=ACCENT_COLOR,
                              font=("Segoe UI", 10), anchor=tk.W,
                              padx=8, pady=4, relief=tk.SUNKEN)
        status_bar.pack(fill=tk.X)

    # ──────────────── Statistics Panel ────────────────
    def _build_stats_panel(self, parent):
        frame = tk.LabelFrame(parent, text=" Statistics ", bg=PANEL_BG,
                               fg=ACCENT_COLOR, font=("Segoe UI", 11, "bold"),
                               bd=2, relief=tk.GROOVE, padx=10, pady=8)
        frame.pack(fill=tk.X, pady=(0, 8))

        self.stat_labels = {}
        stats = [
            ("Algorithm", "—"),
            ("Heuristic", "—"),
            ("Solution", "—"),
            ("Moves", "—"),
            ("States Explored", "—"),
            ("Execution Time", "—"),
        ]
        for label_text, default in stats:
            row = tk.Frame(frame, bg=PANEL_BG)
            row.pack(fill=tk.X, pady=1)
            tk.Label(row, text=f"{label_text}:", bg=PANEL_BG, fg=STAT_LABEL,
                     font=("Segoe UI", 10), width=16, anchor=tk.W).pack(side=tk.LEFT)
            val = tk.Label(row, text=default, bg=PANEL_BG, fg=STAT_VALUE,
                           font=("Segoe UI", 10, "bold"), anchor=tk.W)
            val.pack(side=tk.LEFT, fill=tk.X)
            self.stat_labels[label_text] = val

    # ──────────────── AI Explanation Panel ────────────────
    def _build_ai_panel(self, parent):
        frame = tk.LabelFrame(parent, text=" AI Explanation ", bg=PANEL_BG,
                               fg=ACCENT_COLOR, font=("Segoe UI", 11, "bold"),
                               bd=2, relief=tk.GROOVE, padx=10, pady=8)
        frame.pack(fill=tk.X, pady=(0, 8))

        self.ai_text = tk.Text(frame, height=6, bg=BG_COLOR, fg=HEADER_COLOR,
                                font=("Consolas", 9), wrap=tk.WORD,
                                relief=tk.FLAT, padx=6, pady=4)
        self.ai_text.pack(fill=tk.X)
        self.ai_text.insert(tk.END,
            "AI evaluates puzzle states using:\n\n"
            "  f(n) = g(n) + h(n)\n\n"
            "g(n) = moves so far\n"
            "h(n) = estimated moves remaining (heuristic)\n\n"
            "The state with the lowest f(n) is explored next.\n"
            "This ensures the optimal solution is found first."
        )
        self.ai_text.config(state=tk.DISABLED)

    # ──────────────── Search Information Panel ────────────────
    def _build_search_panel(self, parent):
        frame = tk.LabelFrame(parent, text=" Search Information ", bg=PANEL_BG,
                               fg=ACCENT_COLOR, font=("Segoe UI", 11, "bold"),
                               bd=2, relief=tk.GROOVE, padx=10, pady=8)
        frame.pack(fill=tk.X, pady=(0, 8))

        self.search_info_labels = {}
        fields = [("Current Step", "—"), ("g(n)", "—"), ("h(n)", "—"),
                  ("f(n)", "—"), ("States Explored", "—")]
        for label_text, default in fields:
            row = tk.Frame(frame, bg=PANEL_BG)
            row.pack(fill=tk.X, pady=1)
            tk.Label(row, text=f"{label_text}:", bg=PANEL_BG, fg=STAT_LABEL,
                     font=("Segoe UI", 10), width=16, anchor=tk.W).pack(side=tk.LEFT)
            val = tk.Label(row, text=default, bg=PANEL_BG, fg=STAT_VALUE,
                           font=("Segoe UI", 10, "bold"), anchor=tk.W)
            val.pack(side=tk.LEFT, fill=tk.X)
            self.search_info_labels[label_text] = val

    # ──────────────── Comparison Panel ────────────────
    def _build_comparison_panel(self, parent):
        frame = tk.LabelFrame(parent, text=" Algorithm Comparison ", bg=PANEL_BG,
                               fg=ACCENT_COLOR, font=("Segoe UI", 11, "bold"),
                               bd=2, relief=tk.GROOVE, padx=10, pady=8)
        frame.pack(fill=tk.X, pady=(0, 8))

        # Table header
        header = tk.Frame(frame, bg=BORDER_COLOR)
        header.pack(fill=tk.X, pady=(0, 2))
        cols = ["Algorithm", "Heuristic", "Moves", "Explored", "Time"]
        widths = [12, 16, 7, 10, 12]
        for col, w in zip(cols, widths):
            tk.Label(header, text=col, bg=BORDER_COLOR, fg=ACCENT_COLOR,
                     font=("Segoe UI", 9, "bold"), width=w,
                     anchor=tk.W).pack(side=tk.LEFT, padx=2)

        # Data rows (3 algorithm rows)
        self.comparison_rows = []
        for _ in range(3):
            row_frame = tk.Frame(frame, bg=PANEL_BG)
            row_frame.pack(fill=tk.X, pady=1)
            row_labels = []
            for w in widths:
                lbl = tk.Label(row_frame, text="—", bg=PANEL_BG, fg=STAT_VALUE,
                               font=("Segoe UI", 9), width=w, anchor=tk.W)
                lbl.pack(side=tk.LEFT, padx=2)
                row_labels.append(lbl)
            self.comparison_rows.append(row_labels)

    # ================================================================
    #  BOARD RENDERING
    # ================================================================
    def _update_board(self, highlight_index: int = -1):
        """Redraw the puzzle board to reflect self.current_state."""
        for r in range(3):
            for c in range(3):
                idx = r * 3 + c
                tile = self.current_state[idx]
                btn = self.tile_buttons[r][c]
                if tile == 0:
                    btn.config(text="", bg=BLANK_COLOR, relief=tk.FLAT,
                               activebackground=BLANK_COLOR)
                else:
                    # Highlight tiles that are in goal position
                    goal_val = GOAL_STATE[idx]
                    if tile == goal_val:
                        bg = GOAL_TILE
                    elif idx == highlight_index:
                        bg = TILE_HOVER
                    else:
                        bg = TILE_COLOR
                    btn.config(text=str(tile), bg=bg, relief=tk.RAISED,
                               activebackground=TILE_HOVER)

    # ================================================================
    #  TILE CLICK (manual move)
    # ================================================================
    def _tile_clicked(self, row: int, col: int):
        """Handle clicking a tile to swap it with the adjacent blank."""
        if self.auto_running or self.input_mode:
            return

        idx = row * 3 + col
        blank_idx = find_blank(self.current_state)

        # Check if the clicked tile is adjacent to the blank
        if idx in MOVES[blank_idx]:
            new_state = list(self.current_state)
            new_state[blank_idx], new_state[idx] = new_state[idx], new_state[blank_idx]
            self.current_state = tuple(new_state)
            self._update_board()

            # Clear any existing solution since the board changed
            self.solution_path = []
            self.solution_step = 0

            if is_goal(self.current_state):
                self.status_var.set("🎉 Congratulations! Puzzle solved!")

    # ================================================================
    #  SPEED CHANGE
    # ================================================================
    def _speed_changed(self, event=None):
        text = self.speed_var.get()
        self.animation_speed = int(text.replace(" ms", ""))

    # ================================================================
    #  SOLVE
    # ================================================================
    def _solve(self):
        """Run the selected algorithm in a background thread."""
        if self.is_solving:
            self.status_var.set("Already solving...")
            return

        state = self.current_state

        # Check solvability
        if not is_solvable(state):
            messagebox.showwarning(
                "Unsolvable Puzzle",
                "This puzzle is not solvable.\n"
                "Please enter a different configuration."
            )
            self.status_var.set("Puzzle is not solvable.")
            return

        if is_goal(state):
            self._show_result_already_solved()
            return

        self.is_solving = True
        self.status_var.set("🔄 Solving... please wait.")
        self.initial_state = state

        # Run in background thread to keep GUI responsive
        thread = threading.Thread(target=self._run_solver, daemon=True)
        thread.start()

    def _run_solver(self):
        """Execute the selected algorithm (runs in background thread)."""
        try:
            algo_name = self.algo_var.get()
            state = self.initial_state

            if algo_name == "BFS":
                result = bfs(state)
            elif "Misplaced" in algo_name:
                result = astar(state, misplaced_tiles, "Misplaced Tiles")
            else:  # A* - Manhattan Distance (default)
                result = astar(state, manhattan_distance, "Manhattan Distance")

            # Schedule GUI update on main thread
            self.root.after(0, lambda: self._solver_done(result))
        except Exception as e:
            # Ensure is_solving is reset even if an error occurs
            self.root.after(0, lambda: self._solver_error(str(e)))

    def _solver_error(self, error_msg: str):
        """Handle solver errors (called on main thread)."""
        self.is_solving = False
        self.status_var.set(f"Error: {error_msg}")
        messagebox.showerror("Solver Error", f"An error occurred:\n{error_msg}")

    def _solver_done(self, result: SearchResult):
        """Handle solver completion (called on main thread)."""
        self.is_solving = False
        self.last_result = result

        if result.found:
            self.solution_path = result.path
            self.solution_step = 0
            self.current_state = self.solution_path[0]
            self._update_board()
            self._update_stats(result)
            self._update_search_info(0, result)
            self.step_label.config(text=f"Step 0 / {result.moves}")
            self.status_var.set(
                f"✅ Solution found! {result.moves} moves. Auto-playing..."
            )
            # Automatically start animation
            self.auto_running = True
            self.root.after(self.animation_speed, self._auto_step)
        else:
            self.status_var.set("❌ No solution found.")
            self._clear_stats()

    def _show_result_already_solved(self):
        """Handle the case where the puzzle is already solved."""
        self.stat_labels["Algorithm"].config(text=self.algo_var.get())
        self.stat_labels["Heuristic"].config(text="—")
        self.stat_labels["Solution"].config(text="Already Solved", fg=SUCCESS_COLOR)
        self.stat_labels["Moves"].config(text="0")
        self.stat_labels["States Explored"].config(text="0")
        self.stat_labels["Execution Time"].config(text="0 µs")
        self.status_var.set("🎉 Puzzle is already in the goal state!")
        self.solution_path = [self.current_state]
        self.solution_step = 0

    # ================================================================
    #  NEXT MOVE
    # ================================================================
    def _next_move(self):
        """Show the next step in the solution path."""
        if not self.solution_path:
            self.status_var.set("No solution loaded. Click 'Solve' first.")
            return

        if self.solution_step < len(self.solution_path) - 1:
            self.solution_step += 1
            self.current_state = self.solution_path[self.solution_step]
            self._update_board()
            self._update_search_info(self.solution_step, self.last_result)
            self.step_label.config(
                text=f"Step {self.solution_step} / {len(self.solution_path) - 1}")

            if self.solution_step == len(self.solution_path) - 1:
                self.status_var.set("🎉 Goal state reached!")
        else:
            self.status_var.set("Already at the goal state.")

    # ================================================================
    #  AUTO SOLVE
    # ================================================================
    def _auto_solve(self):
        """Animate the solution step-by-step."""
        if not self.solution_path:
            # If no solution yet, solve first then wait for result
            if not is_solvable(self.current_state):
                messagebox.showwarning(
                    "Unsolvable Puzzle",
                    "This puzzle is not solvable.\n"
                    "Please enter a different configuration."
                )
                self.status_var.set("Puzzle is not solvable.")
                return
            self._solve()
            # Wait for solver to finish, then start auto (only once)
            self.root.after(800, self._try_start_auto)
            return

        if self.auto_running:
            self.auto_running = False
            self.status_var.set("Animation paused.")
            return

        self.auto_running = True
        self.status_var.set("▶ Auto-solving...")
        self._auto_step()

    def _try_start_auto(self):
        """Start auto animation only if a solution was found (avoids infinite loop)."""
        if self.solution_path and not self.auto_running:
            self.auto_running = True
            self.status_var.set("▶ Auto-solving...")
            self._auto_step()

    def _auto_step(self):
        """Take one animation step."""
        if not self.auto_running:
            return

        if self.solution_step < len(self.solution_path) - 1:
            self.solution_step += 1
            self.current_state = self.solution_path[self.solution_step]
            self._update_board()
            self._update_search_info(self.solution_step, self.last_result)
            self.step_label.config(
                text=f"Step {self.solution_step} / {len(self.solution_path) - 1}")
            self.root.after(self.animation_speed, self._auto_step)
        else:
            self.auto_running = False
            self.status_var.set("🎉 Goal state reached!")

    # ================================================================
    #  RANDOM PUZZLE
    # ================================================================
    def _random_puzzle(self):
        """Generate a random solvable puzzle based on selected difficulty."""
        self.auto_running = False
        diff = self.diff_var.get().lower()
        self.difficulty = diff
        state = generate_random_puzzle(diff)
        self.current_state = state
        self.initial_state = state
        self.solution_path = []
        self.solution_step = 0
        self._update_board()
        self._clear_stats()
        self._clear_search_info()
        self.step_label.config(text="")
        self.status_var.set(
            f"🎲 Random puzzle generated (Difficulty: {diff.capitalize()}). "
            f"Click 'Solve' to find the solution."
        )

    # ================================================================
    #  RESET
    # ================================================================
    def _reset(self):
        """Reset the board to the initial state."""
        self.auto_running = False
        self.current_state = self.initial_state
        self.solution_step = 0
        self._update_board()
        self.step_label.config(text="")
        if self.solution_path:
            self.status_var.set("Board reset to initial state. Solution still loaded.")
        else:
            self.status_var.set("Board reset to initial state.")

    # ================================================================
    #  ENTER PUZZLE (Input Mode)
    # ================================================================
    def _enter_puzzle(self):
        """Toggle input mode: show Entry widgets for manual puzzle entry."""
        if self.input_mode:
            # Collect values and validate
            values = []
            for r in range(3):
                for c in range(3):
                    values.append(self.input_entries[r][c].get().strip())

            valid, state, error = validate_input(values)
            if not valid:
                messagebox.showerror("Invalid Input", error)
                return

            # Exit input mode
            self.input_mode = False
            self._destroy_input_entries()
            self._show_tile_buttons()

            self.current_state = state
            self.initial_state = state
            self.solution_path = []
            self.solution_step = 0
            self._update_board()
            self._clear_stats()
            self._clear_search_info()
            self.step_label.config(text="")
            self.status_var.set("Custom puzzle entered. Click 'Solve' to find the solution.")
        else:
            # Enter input mode
            self.auto_running = False
            self.input_mode = True
            self.solution_path = []
            self._hide_tile_buttons()
            self._create_input_entries()
            self.status_var.set(
                "Enter numbers 0-8 (0 = blank). Click 'Enter Puzzle' to confirm."
            )

    def _hide_tile_buttons(self):
        for r in range(3):
            for c in range(3):
                self.tile_buttons[r][c].grid_remove()

    def _show_tile_buttons(self):
        for r in range(3):
            for c in range(3):
                self.tile_buttons[r][c].grid()

    def _create_input_entries(self):
        self.input_entries = []
        for r in range(3):
            row_entries = []
            for c in range(3):
                idx = r * 3 + c
                e = tk.Entry(
                    self.board_container, font=("Segoe UI", 28, "bold"),
                    width=3, justify=tk.CENTER,
                    bg=BG_COLOR, fg=TILE_TEXT,
                    insertbackground=TILE_TEXT,
                    relief=tk.SUNKEN, bd=3,
                )
                # Pre-fill with current state
                val = self.current_state[idx]
                e.insert(0, str(val))
                e.grid(row=r, column=c, padx=3, pady=3)
                row_entries.append(e)
            self.input_entries.append(row_entries)

    def _destroy_input_entries(self):
        for r in range(3):
            for c in range(3):
                self.input_entries[r][c].destroy()
        self.input_entries = []

    # ================================================================
    #  COMPARE ALGORITHMS
    # ================================================================
    def _compare_algorithms(self):
        """Run all three algorithms and display a comparison table."""
        state = self.current_state

        if not is_solvable(state):
            messagebox.showwarning(
                "Unsolvable Puzzle",
                "Cannot compare algorithms on an unsolvable puzzle."
            )
            return

        if is_goal(state):
            messagebox.showinfo("Already Solved",
                                "Puzzle is already in the goal state (0 moves).")
            return

        self.status_var.set("🔄 Running comparison... please wait.")
        self.root.update_idletasks()

        # Run in background thread
        thread = threading.Thread(
            target=self._run_comparison, args=(state,), daemon=True
        )
        thread.start()

    def _run_comparison(self, state):
        results = []
        results.append(bfs(state))
        results.append(astar(state, misplaced_tiles, "Misplaced Tiles"))
        results.append(astar(state, manhattan_distance, "Manhattan Distance"))
        self.root.after(0, lambda: self._comparison_done(results))

    def _comparison_done(self, results):
        for i, result in enumerate(results):
            row = self.comparison_rows[i]
            row[0].config(text=result.algorithm)
            row[1].config(text=result.heuristic)
            if result.found:
                row[2].config(text=str(result.moves))
                row[3].config(text=str(result.states_explored))
                row[4].config(text=format_time(result.execution_time))
            else:
                row[2].config(text="N/A")
                row[3].config(text="N/A")
                row[4].config(text="N/A")

        self.status_var.set("📊 Comparison complete! See the table on the right.")

    # ================================================================
    #  UPDATE PANELS
    # ================================================================
    def _update_stats(self, result: SearchResult):
        self.stat_labels["Algorithm"].config(text=result.algorithm)
        self.stat_labels["Heuristic"].config(text=result.heuristic)
        if result.found:
            self.stat_labels["Solution"].config(text="Found ✅", fg=SUCCESS_COLOR)
        else:
            self.stat_labels["Solution"].config(text="Not Found ❌", fg=ERROR_COLOR)
        self.stat_labels["Moves"].config(text=str(result.moves))
        self.stat_labels["States Explored"].config(text=str(result.states_explored))
        self.stat_labels["Execution Time"].config(text=format_time(result.execution_time))

    def _clear_stats(self):
        for key in self.stat_labels:
            self.stat_labels[key].config(text="—", fg=STAT_VALUE)

    def _update_search_info(self, step: int, result: SearchResult):
        """Update the search info panel for the current step."""
        if not result or not result.found:
            return
        self.search_info_labels["Current Step"].config(text=f"{step} / {result.moves}")
        g = step
        # Compute h for current state
        algo = self.algo_var.get()
        state = self.solution_path[step] if step < len(self.solution_path) else self.current_state
        if "Manhattan" in algo:
            h = manhattan_distance(state)
        elif "Misplaced" in algo:
            h = misplaced_tiles(state)
        else:
            h = 0  # BFS has no heuristic
        f = g + h
        self.search_info_labels["g(n)"].config(text=str(g))
        self.search_info_labels["h(n)"].config(text=str(h))
        self.search_info_labels["f(n)"].config(text=str(f))
        self.search_info_labels["States Explored"].config(
            text=str(result.states_explored))

    def _clear_search_info(self):
        for key in self.search_info_labels:
            self.search_info_labels[key].config(text="—")

    # ================================================================
    #  ABOUT DIALOG
    # ================================================================
    def _show_about(self):
        about_text = (
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "   AI-Based 8-Puzzle Solver\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "Technology:    Python + Tkinter\n"
            "AI Technique:  A* Search Algorithm\n"
            "Heuristics:    Manhattan Distance,\n"
            "               Misplaced Tiles\n"
            "Problem Type:  State-Space Search\n\n"
            "Goal: Find an optimal sequence of\n"
            "moves from an initial state to the\n"
            "goal state using AI search.\n\n"
            "Algorithms: BFS, A* (Manhattan),\n"
            "            A* (Misplaced Tiles)\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        )
        messagebox.showinfo("About Project", about_text)
