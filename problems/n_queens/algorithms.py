import time
import random

# --- Core Validation Logic ---


def is_safe(board: list[int], row: int, col: int) -> tuple[bool, str]:
    """
    Checks if placing a queen at board[row] = col is safe.
    `board` is a partial solution, e.g., [1, 3, 0] for N=4, row=3
    This means we are checking (row, col) against queens at (0, 1), (1, 3), (2, 0).

    Returns: (is_safe, conflict_reason)
    """
    # We only need to check queens in previous rows
    for r in range(row):
        # Check column conflict
        if board[r] == col:
            return (False, f"conflicts with queen at ({r}, {col}) on the same column")

        # Check diagonal conflict
        if abs(r - row) == abs(board[r] - col):
            return (
                False,
                f"conflicts with queen at ({r}, {board[r]}) on the same diagonal",
            )

    return (True, "")


# --- 1. Backtracking Algorithm ---


def solve_n_queens_bt(n: int) -> tuple[list[list[int]], float]:
    """
    Finds ALL solutions for N-Queens using backtracking.
    Returns: (list_of_solutions, time_taken_sec)
    """
    start_time = time.perf_counter()
    solutions = []

    def solve(row: int, board: list[int]):
        if row == n:
            # Found a complete solution
            solutions.append(list(board))
            return

        for col in range(n):
            safe, _ = is_safe(board, row, col)
            if safe:
                board[row] = col
                solve(row + 1, board)
                # Backtrack - this line is implicitly handled
                # by the loop overwriting board[row]
                # but good to remember. board[row] = -1

    # Initialize board with -1 (or any invalid position)
    initial_board = [-1] * n
    solve(0, initial_board)

    end_time = time.perf_counter()
    return (solutions, end_time - start_time)


def find_one_n_queens_bt(n: int) -> tuple[list[int] | None, float]:
    """
    Finds ONE solution for N-Queens using backtracking.
    Returns: (solution, time_taken_sec)
    """
    start_time = time.perf_counter()
    solution = None

    def solve(row: int, board: list[int]) -> bool:
        nonlocal solution
        if row == n:
            solution = list(board)
            return True  # Found, stop searching

        for col in range(n):
            safe, _ = is_safe(board, row, col)
            if safe:
                board[row] = col
                if solve(row + 1, board):
                    return True  # Propagate "found" signal

        return False  # No solution from this path

    initial_board = [-1] * n
    solve(0, initial_board)

    end_time = time.perf_counter()
    return (solution, end_time - start_time)


# --- 2. Local Search: Hill Climbing (Steepest Ascent) ---


def _calculate_conflicts(board: list[int]) -> int:
    """Helper for local search. Counts total number of conflicting pairs."""
    n = len(board)
    conflicts = 0
    for r in range(n):
        for c in range(r + 1, n):
            # Column conflicts (not possible in this representation)
            # if board[r] == board[c]: conflicts += 1

            # Diagonal conflicts
            if abs(r - c) == abs(board[r] - board[c]):
                conflicts += 1
    return conflicts


def _get_best_neighbor(board: list[int]) -> list[int]:
    """
    Helper for Hill Climbing.
    Finds the single-move neighbor with the FEWEST conflicts.
    """
    n = len(board)
    current_conflicts = _calculate_conflicts(board)
    best_board = list(board)
    best_conflicts = current_conflicts

    for row in range(n):
        original_col = board[row]
        for col in range(n):
            if col == original_col:
                continue

            board[row] = col  # Make a move
            new_conflicts = _calculate_conflicts(board)

            if new_conflicts < best_conflicts:
                best_conflicts = new_conflicts
                best_board = list(board)

        board[row] = original_col  # Move back

    return best_board


def solve_n_queens_hc(n: int, max_restarts: int = 10) -> tuple[list[int] | None, float]:
    """
    Finds ONE solution using Hill Climbing with random restarts.
    Returns: (solution, time_taken_sec)
    """
    start_time = time.perf_counter()

    for _ in range(max_restarts):
        # Start with a random board
        current_board = list(range(n))
        random.shuffle(current_board)

        while True:
            current_conflicts = _calculate_conflicts(current_board)
            if current_conflicts == 0:
                # Found a solution
                end_time = time.perf_counter()
                return (current_board, end_time - start_time)

            neighbor_board = _get_best_neighbor(current_board)
            neighbor_conflicts = _calculate_conflicts(neighbor_board)

            if neighbor_conflicts >= current_conflicts:
                # Local maximum (or plateau) reached, restart.
                break

            current_board = neighbor_board

    end_time = time.perf_counter()
    return (None, end_time - start_time)  # Failed to find a solution


# --- 3. Local Search: Simulated Annealing ---


def solve_n_queens_sa(
    n: int, initial_temp: float = 1000, cooling_rate: float = 0.99
) -> tuple[list[int] | None, float]:
    """
    Finds ONE solution using Simulated Annealing.
    Returns: (solution, time_taken_sec)
    """
    start_time = time.perf_counter()

    # Start with a random board
    current_board = list(range(n))
    random.shuffle(current_board)
    current_conflicts = _calculate_conflicts(current_board)

    temp = initial_temp

    while temp > 0.1 and current_conflicts > 0:
        if current_conflicts == 0:
            break

        # Pick a random neighbor (swap two random rows' positions)
        next_board = list(current_board)
        r1, r2 = random.sample(range(n), 2)
        next_board[r1], next_board[r2] = next_board[r2], next_board[r1]

        next_conflicts = _calculate_conflicts(next_board)

        # Calculate acceptance probability
        delta_energy = next_conflicts - current_conflicts

        if delta_energy < 0:
            # Better solution, always accept
            current_board = next_board
            current_conflicts = next_conflicts
        else:
            # Worse solution, accept with probability
            if random.random() < pow(2.71828, -delta_energy / temp):
                current_board = next_board
                current_conflicts = next_conflicts

        temp *= cooling_rate  # Cool down

    end_time = time.perf_counter()

    if current_conflicts == 0:
        return (current_board, end_time - start_time)
    else:
        return (None, end_time - start_time)  # Failed to find
