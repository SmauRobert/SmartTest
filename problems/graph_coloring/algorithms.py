import time
import random

# --- Graph Representation ---
# We'll use an adjacency list:
# G = {
#   0: [1, 2],
#   1: [0, 2],
#   2: [0, 1]
# }


def generate_random_graph(n: int, m: int) -> dict[int, list[int]]:
    """Generates a random graph with N nodes and M edges."""
    if m > n * (n - 1) / 2:
        m = n * (n - 1) // 2  # Max edges

    graph = {i: [] for i in range(n)}
    edges = set()

    while len(edges) < m:
        u, v = random.sample(range(n), 2)
        if u > v:
            u, v = v, u  # Consistent edge representation

        if (u, v) not in edges:
            edges.add((u, v))
            graph[u].append(v)
            graph[v].append(u)

    return graph


# --- Core Validation Logic ---


def is_coloring_valid(
    graph: dict[int, list[int]], coloring: dict[int, int]
) -> tuple[bool, str]:
    """Checks if a given coloring is valid."""
    if not coloring:
        return (False, "Coloring map is empty.")

    for u, neighbors in graph.items():
        if u not in coloring:
            return (False, f"Node {u} has not been colored.")

        u_color = coloring[u]
        for v in neighbors:
            if v in coloring and coloring[v] == u_color:
                return (
                    False,
                    f"Conflict: Node {u} and Node {v} are adjacent but both have color {u_color}.",
                )

    return (True, "Coloring is valid.")


# --- 1. Simple Greedy Coloring ---


def solve_gc_greedy(graph: dict[int, list[int]]) -> tuple[dict[int, int], float]:
    """
    Finds a valid (non-optimal) coloring using a simple greedy algorithm.
    Returns: (coloring_map, time_taken_sec)
    """
    start_time = time.perf_counter()
    n = len(graph)
    coloring = {}  # node -> color (0, 1, 2...)

    for u in range(n):
        neighbor_colors = set()
        for v in graph[u]:
            if v in coloring:
                neighbor_colors.add(coloring[v])

        # Find the smallest available color
        color = 0
        while color in neighbor_colors:
            color += 1

        coloring[u] = color

    end_time = time.perf_counter()
    return (coloring, end_time - start_time)


# --- 2. Welsh-Powell Algorithm (Largest-Degree-First) ---


def solve_gc_welsh_powell(graph: dict[int, list[int]]) -> tuple[dict[int, int], float]:
    """
    Finds a valid (non-optimal) coloring using Welsh-Powell.
    Returns: (coloring_map, time_taken_sec)
    """
    start_time = time.perf_counter()
    n = len(graph)
    coloring = {}

    # Sort nodes by degree, descending
    nodes_by_degree = sorted(graph.keys(), key=lambda u: len(graph[u]), reverse=True)

    color = 0
    nodes_to_color = set(nodes_by_degree)

    while nodes_to_color:
        # Get the first uncolored node (highest degree)
        u = next(iter(n for n in nodes_by_degree if n in nodes_to_color))

        coloring[u] = color
        nodes_to_color.remove(u)

        # Find other nodes that can also be this color
        colored_neighbors = set()
        for v in nodes_by_degree:
            if v in nodes_to_color and v not in colored_neighbors:
                # Check if v is adjacent to any node *already* colored with `color`
                is_adjacent = False
                for w in graph[v]:
                    if w in coloring and coloring[w] == color:
                        is_adjacent = True
                        break

                if not is_adjacent:
                    coloring[v] = color
                    nodes_to_color.remove(v)
                    # Add v's neighbors to the "can't use" list for this pass
                    colored_neighbors.update(graph[v])

        color += 1  # Move to the next color

    end_time = time.perf_counter()
    return (coloring, end_time - start_time)


# --- 3. Chromatic Number (Optimal) - Brute-force Backtracking ---


def solve_gc_optimal(graph: dict[int, list[int]]) -> tuple[int, float]:
    """
    Finds the *optimal* chromatic number (m) using backtracking.
    Extremely slow, only use for N < 15.
    Returns: (chromatic_number, time_taken_sec)
    """
    start_time = time.perf_counter()
    n = len(graph)

    def is_safe_to_color(u: int, color: int, coloring: dict[int, int]) -> bool:
        for v in graph[u]:
            if v in coloring and coloring[v] == color:
                return False
        return True

    def solve_for_m(m: int) -> bool:
        """Tries to color the graph with `m` colors."""
        coloring = {}

        def solve_recursive(u: int) -> bool:
            if u == n:
                return True  # All nodes colored

            for color in range(m):
                if is_safe_to_color(u, color, coloring):
                    coloring[u] = color
                    if solve_recursive(u + 1):
                        return True
                    del coloring[u]  # Backtrack

            return False  # No color works for this node

        return solve_recursive(0)

    # Try 1 color, then 2, then 3... up to N
    for m in range(1, n + 2):
        if solve_for_m(m):
            end_time = time.perf_counter()
            return (m, end_time - start_time)

    end_time = time.perf_counter()
    return (n, end_time - start_time)  # Should not be reached
