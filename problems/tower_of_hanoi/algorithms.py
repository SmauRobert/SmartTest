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


# --- 3. Memoized Recursive Algorithm ---


def solve_hanoi_memoized(n: int) -> tuple[list[tuple[str, str]], float]:
    """
    Generates all moves for 3-peg Hanoi using memoized recursion.
    Note: Hanoi doesn't have overlapping subproblems, so this won't be faster,
    but it's included for comparison purposes.
    Returns: (list_of_moves, time_taken_sec)
    """
    start_time = time.perf_counter()
    moves = []
    memo = {}

    def solve(count: int, source: str, destination: str, auxiliary: str):
        # Memoization key (though Hanoi doesn't really benefit from it)
        key = (count, source, destination, auxiliary)
        if key in memo:
            # Return cached moves
            for move in memo[key]:
                moves.append(move)
            return

        local_moves = []
        if count == 1:
            local_moves.append((source, destination))
            moves.append((source, destination))
        else:
            # 1. Move n-1 from source to auxiliary
            solve(count - 1, source, auxiliary, destination)

            # 2. Move 1 from source to destination
            local_moves.append((source, destination))
            moves.append((source, destination))

            # 3. Move n-1 from auxiliary to destination
            solve(count - 1, auxiliary, destination, source)

        memo[key] = local_moves

    solve(n, "A", "C", "B")

    end_time = time.perf_counter()
    return (moves, end_time - start_time)


# --- 4. Binary Pattern Algorithm ---


def solve_hanoi_binary_pattern(n: int) -> tuple[list[tuple[str, str]], float]:
    """
    Generates all moves for 3-peg Hanoi using the binary pattern method.
    This is a non-recursive approach based on the observation that the sequence
    of moves follows a pattern related to binary counting.
    Returns: (list_of_moves, time_taken_sec)
    """
    start_time = time.perf_counter()
    moves = []
    total_moves = (2**n) - 1

    # Peg names
    pegs = ["A", "C", "B"]  # For odd disk count on first move
    if n % 2 == 0:
        pegs = ["A", "B", "C"]  # For even disk count

    for i in range(1, total_moves + 1):
        # Find which disk to move (the rightmost bit set in i)
        disk = 0
        temp = i
        while temp % 2 == 0:
            disk += 1
            temp //= 2

        # Determine source and destination based on disk number and move count
        if disk % 2 == 0:
            # Even disk (or disk 0)
            if n % 2 == 1:
                # Odd number of disks
                source = pegs[((i - 1) // (2**disk)) % 3]
                dest = pegs[(((i - 1) // (2**disk)) + 1) % 3]
            else:
                # Even number of disks
                source = pegs[((i - 1) // (2**disk)) % 3]
                dest = pegs[(((i - 1) // (2**disk)) + 1) % 3]
        else:
            # Odd disk
            if n % 2 == 1:
                # Odd number of disks
                source = pegs[((i - 1) // (2**disk)) % 3]
                dest = pegs[(((i - 1) // (2**disk)) + 2) % 3]
            else:
                # Even number of disks
                source = pegs[((i - 1) // (2**disk)) % 3]
                dest = pegs[(((i - 1) // (2**disk)) + 2) % 3]

        # For simplicity, use a basic pattern
        # The pattern alternates based on which disk moves
        from_peg = (i & (i - 1)) % 3
        to_peg = ((i | (i - 1)) + 1) % 3

        # Map indices to peg names
        peg_names = {0: "A", 1: "B", 2: "C"}
        if n % 2 == 0:
            peg_names = {0: "A", 1: "C", 2: "B"}

        moves.append((peg_names[from_peg], peg_names[to_peg]))

    end_time = time.perf_counter()
    return (moves, end_time - start_time)
