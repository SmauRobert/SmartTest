import time

# --- Core Validation Logic ---


def is_valid_move(n: int, board: list[list[int]], r: int, c: int) -> bool:
    """Checks if a square (r, c) is on the board and unvisited."""
    return 0 <= r < n and 0 <= c < n and board[r][c] == -1


def is_l_shape(r1: int, c1: int, r2: int, c2: int) -> bool:
    """Checks if the move from (r1, c1) to (r2, c2) is a valid L-shape."""
    dr = abs(r1 - r2)
    dc = abs(c1 - c2)
    return (dr == 2 and dc == 1) or (dr == 1 and dc == 2)


def get_valid_moves(
    n: int, board: list[list[int]], r: int, c: int
) -> list[tuple[int, int]]:
    """Gets all valid knight moves from (r, c)."""
    possible_moves = [
        (r - 2, c - 1),
        (r - 2, c + 1),
        (r - 1, c - 2),
        (r - 1, c + 2),
        (r + 1, c - 2),
        (r + 1, c + 2),
        (r + 2, c - 1),
        (r + 2, c + 1),
    ]

    valid = []
    for move in possible_moves:
        if is_valid_move(n, board, move[0], move[1]):
            valid.append(move)
    return valid


# --- 1. Backtracking Algorithm ---


def solve_kt_bt(n: int) -> tuple[list[tuple[int, int]] | None, float]:
    """
    Finds ONE open Knight's Tour using simple backtracking.
    Returns: (list_of_moves, time_taken_sec)
    """
    start_time = time.perf_counter()
    board = [[-1 for _ in range(n)] for _ in range(n)]

    def solve(r: int, c: int, move_count: int, path: list[tuple[int, int]]) -> bool:
        board[r][c] = move_count
        path.append((r, c))

        if move_count == n * n:
            return True  # Solved

        for next_r, next_c in get_valid_moves(n, board, r, c):
            if solve(next_r, next_c, move_count + 1, path):
                return True

        # Backtrack
        board[r][c] = -1
        path.pop()
        return False

    final_path = []
    # Start at (0, 0)
    if solve(0, 0, 1, final_path):
        end_time = time.perf_counter()
        return (final_path, end_time - start_time)
    else:
        end_time = time.perf_counter()
        return (None, end_time - start_time)  # No solution found


# --- 2. Warnsdorff's Rule Algorithm ---


def solve_kt_warnsdorff(n: int) -> tuple[list[tuple[int, int]] | None, float]:
    """
    Finds ONE open Knight's Tour using Warnsdorff's Rule heuristic.
    Returns: (list_of_moves, time_taken_sec)
    """
    start_time = time.perf_counter()
    board = [[-1 for _ in range(n)] for _ in range(n)]

    def get_onward_moves_count(r: int, c: int) -> int:
        """Counts valid moves from (r, c) - helper for Warnsdorff."""
        count = 0
        possible_moves = [
            (r - 2, c - 1),
            (r - 2, c + 1),
            (r - 1, c - 2),
            (r - 1, c + 2),
            (r + 1, c - 2),
            (r + 1, c + 2),
            (r + 2, c - 1),
            (r + 2, c + 1),
        ]
        for move in possible_moves:
            if is_valid_move(n, board, move[0], move[1]):
                count += 1
        return count

    def solve(r: int, c: int, move_count: int, path: list[tuple[int, int]]) -> bool:
        board[r][c] = move_count
        path.append((r, c))

        if move_count == n * n:
            return True

        # Sort valid moves by their onward move count (Warnsdorff's)
        valid_moves = get_valid_moves(n, board, r, c)
        sorted_moves = sorted(
            valid_moves, key=lambda move: get_onward_moves_count(move[0], move[1])
        )

        for next_r, next_c in sorted_moves:
            if solve(next_r, next_c, move_count + 1, path):
                return True

        # Backtrack
        board[r][c] = -1
        path.pop()
        return False

    final_path = []
    # Start at (0, 0)
    if solve(0, 0, 1, final_path):
        end_time = time.perf_counter()
        return (final_path, end_time - start_time)
    else:
        end_time = time.perf_counter()
        return (None, end_time - start_time)


# --- 3. Random Walk Algorithm ---


def solve_kt_random_walk(
    n: int, max_attempts: int = 100
) -> tuple[list[tuple[int, int]] | None, float]:
    """
    Attempts to find an open Knight's Tour using random walk.
    This is fast but unreliable - may not find a solution even if one exists.
    Returns: (list_of_moves, time_taken_sec)
    """
    import random

    start_time = time.perf_counter()

    for attempt in range(max_attempts):
        board = [[-1 for _ in range(n)] for _ in range(n)]
        path = []
        r, c = 0, 0
        move_count = 1

        board[r][c] = move_count
        path.append((r, c))

        while move_count < n * n:
            valid_moves = get_valid_moves(n, board, r, c)
            if not valid_moves:
                break  # Dead end

            # Choose random move
            next_r, next_c = random.choice(valid_moves)
            move_count += 1
            board[next_r][next_c] = move_count
            path.append((next_r, next_c))
            r, c = next_r, next_c

        if move_count == n * n:
            # Found a complete tour!
            end_time = time.perf_counter()
            return (path, end_time - start_time)

    end_time = time.perf_counter()
    return (None, end_time - start_time)  # Failed to find solution
