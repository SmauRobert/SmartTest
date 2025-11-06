import time

# --- 1. Recursive Algorithm ---


def solve_hanoi_recursive(n: int) -> tuple[list[tuple[str, str]], float]:
    """
    Generates all moves for 3-peg Hanoi using recursion.
    Returns: (list_of_moves, time_taken_sec)
    """
    start_time = time.perf_counter()
    moves = []

    def solve(count: int, source: str, destination: str, auxiliary: str):
        if count == 1:
            moves.append((source, destination))
            return

        # 1. Move n-1 from A to B
        solve(count - 1, source, auxiliary, destination)

        # 2. Move 1 from A to C
        moves.append((source, destination))

        # 3. Move n-1 from B to C
        solve(count - 1, auxiliary, destination, source)

    solve(n, "A", "C", "B")

    end_time = time.perf_counter()
    return (moves, end_time - start_time)


# --- 2. Iterative Algorithm ---


def solve_hanoi_iterative(n: int) -> tuple[list[tuple[str, str]], float]:
    """
    Generates all moves for 3-peg Hanoi using an iterative (stack-based) approach.
    Returns: (list_of_moves, time_taken_sec)
    """
    start_time = time.perf_counter()
    moves = []

    # We simulate the call stack
    # Each item is a "task": (count, source, destination, auxiliary)
    stack = []

    # Initial task: Move N from A to C
    stack.append((n, "A", "C", "B"))

    while stack:
        task = stack.pop()
        count, source, destination, auxiliary = task

        if count == 1:
            # Base case: Just make the move
            moves.append((source, destination))
        else:
            # We add tasks in REVERSE order of execution
            # 3. Move n-1 from B to C
            stack.append((count - 1, auxiliary, destination, source))

            # 2. Move 1 from A to C
            stack.append((1, source, destination, auxiliary))

            # 1. Move n-1 from A to B
            stack.append((count - 1, source, auxiliary, destination))

    end_time = time.perf_counter()
    return (moves, end_time - start_time)


# --- Core Validation Logic ---


def is_hanoi_move_valid(
    pegs: dict[str, list[int]], peg_from: str, peg_to: str
) -> tuple[bool, str]:
    """
    Checks if a single Hanoi move is valid.
    Pegs: {'A': [5, 3], 'B': [4, 2], 'C': [1]} (bottom-to-top)
    """
    if not pegs.get(peg_from):
        return (False, f"Peg {peg_from} is empty.")

    disk_to_move = pegs[peg_from][-1]  # Get top disk

    if not pegs.get(peg_to) or not pegs[peg_to]:
        # Moving to an empty peg is always valid
        return (True, "")

    top_disk_on_to = pegs[peg_to][-1]

    if disk_to_move > top_disk_on_to:
        return (
            False,
            f"You cannot place disk {disk_to_move} on top of the smaller disk {top_disk_on_to}.",
        )

    return (True, "")
