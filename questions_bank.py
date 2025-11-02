from dataclasses import dataclass
from enum import Enum, auto
from typing import Callable, List, Optional, Final, TypeVar, Dict
import random


class Topic(Enum):
    """Available problem-solving topics"""

    N_QUEENS = auto()
    HANOI = auto()
    GRAPH_COLORING = auto()
    KNIGHTS_TOUR = auto()

    @classmethod
    def get_display_name(cls, topic: "Topic") -> str:
        return {
            cls.N_QUEENS: "N-Queens Problem",
            cls.HANOI: "Generalized Tower of Hanoi",
            cls.GRAPH_COLORING: "Graph Coloring",
            cls.KNIGHTS_TOUR: "Knight's Tour",
        }[topic]


class QuestionType(Enum):
    """Types of questions that can be asked about each topic"""

    SOLUTION = auto()  # Find a solution for a specific instance
    VALIDITY = auto()  # Check if a given solution/move is valid
    NEXT_MOVE = auto()  # Determine the next valid move
    COMPLEXITY = auto()  # Analyze time/space complexity
    STRATEGY = auto()  # Explain the solving strategy


Position = tuple[int, int]
Board = List[List[int]]
Solution = List[int]


@dataclass(frozen=True)
class NQueensParams:
    """Parameters for N-Queens questions"""

    N: int
    positions: Optional[List[Position]] = None
    partial_solution: Optional[Solution] = None


@dataclass(frozen=True)
class HanoiParams:
    """Parameters for Tower of Hanoi questions"""

    num_disks: int
    num_pegs: int
    current_state: Optional[List[List[int]]] = None
    source: Optional[int] = None
    target: Optional[int] = None


@dataclass(frozen=True)
class GraphColoringParams:
    """Parameters for Graph Coloring questions"""

    num_vertices: int
    edges: List[tuple[int, int]]
    num_colors: int
    partial_coloring: Optional[List[int]] = None


@dataclass(frozen=True)
class KnightsTourParams:
    """Parameters for Knight's Tour questions"""

    board_size: tuple[int, int]
    start_pos: Optional[Position] = None
    current_path: Optional[List[Position]] = None


@dataclass(frozen=True)
class Question:
    """Represents a generated question instance"""

    id: str
    topic: Topic
    type: QuestionType
    name: str
    prompt: str
    answer_format: str
    params: NQueensParams | HanoiParams | GraphColoringParams | KnightsTourParams
    solution: Optional[any] = None


@dataclass(frozen=True)
class QuestionTemplate:
    """Template for generating questions"""

    topic: Topic
    type: QuestionType
    name: str
    prompt_template: str
    answer_format_template: str
    param_generator: Callable[
        [], NQueensParams | HanoiParams | GraphColoringParams | KnightsTourParams
    ]
    solution_generator: Optional[Callable[[any], any]] = None

    def generate(self) -> Question:
        """Generate a question instance from this template"""
        params = self.param_generator()

        # Format prompt based on parameter type
        if isinstance(params, NQueensParams):
            prompt = self._format_nqueens_prompt(params)
        elif isinstance(params, HanoiParams):
            prompt = self._format_hanoi_prompt(params)
        elif isinstance(params, GraphColoringParams):
            prompt = self._format_graph_prompt(params)
        elif isinstance(params, KnightsTourParams):
            prompt = self._format_knights_prompt(params)
        else:
            raise ValueError(f"Unsupported parameter type: {type(params)}")

        # Format answer format template
        answer_format = self._format_answer_template(params)

        # Generate solution if needed
        solution = self.solution_generator(params) if self.solution_generator else None

        return Question(
            id=f"{self.topic.name}_{self.type.name}_{hash(str(params)) % 10000}",
            topic=self.topic,
            type=self.type,
            name=self.name,
            prompt=prompt,
            answer_format=answer_format,
            params=params,
            solution=solution,
        )

    def _format_nqueens_prompt(self, params: NQueensParams) -> str:
        return self.prompt_template.format(
            N=params.N,
            positions=params.positions if params.positions else [],
            partial=params.partial_solution if params.partial_solution else [],
        )

    def _format_hanoi_prompt(self, params: HanoiParams) -> str:
        return self.prompt_template.format(
            disks=params.num_disks,
            pegs=params.num_pegs,
            state=params.current_state if params.current_state else [],
            source=params.source if params.source is not None else 0,
            target=params.target if params.target is not None else params.num_pegs - 1,
        )

    def _format_graph_prompt(self, params: GraphColoringParams) -> str:
        return self.prompt_template.format(
            V=params.num_vertices,
            E=params.edges,
            colors=params.num_colors,
            partial=params.partial_coloring if params.partial_coloring else [],
        )

    def _format_knights_prompt(self, params: KnightsTourParams) -> str:
        rows, cols = params.board_size
        return self.prompt_template.format(
            size=f"{rows}x{cols}",
            start=params.start_pos if params.start_pos else (0, 0),
            path=params.current_path if params.current_path else [],
        )

    def _format_answer_template(self, params: any) -> str:
        if isinstance(params, NQueensParams):
            return self.answer_format_template.format(N=params.N, max_pos=params.N - 1)
        elif isinstance(params, HanoiParams):
            return self.answer_format_template.format(pegs=params.num_pegs - 1)
        elif isinstance(params, GraphColoringParams):
            return self.answer_format_template.format(
                colors=params.num_colors - 1, V=params.num_vertices
            )
        elif isinstance(params, KnightsTourParams):
            rows, cols = params.board_size
            return self.answer_format_template.format(rows=rows, cols=cols)
        else:
            raise ValueError(f"Unsupported parameter type: {type(params)}")


# Parameter generators
def solve_nqueens(n: int) -> list[int]:
    """Find a valid N-Queens solution"""

    def is_safe(board: list[int], row: int, col: int) -> bool:
        for i in range(col):
            if board[i] == row or abs(board[i] - row) == abs(i - col):
                return False
        return True

    def solve(board: list[int], col: int) -> bool:
        if col >= len(board):
            return True
        for row in range(len(board)):
            if is_safe(board, row, col):
                board[col] = row
                if solve(board, col + 1):
                    return True
                board[col] = -1
        return False

    solution = [-1] * n
    solve(solution, 0)
    return solution


def generate_nqueens_params() -> NQueensParams:
    """Generate parameters for N-Queens questions"""
    N = random.randint(4, 8)
    solution = solve_nqueens(N)
    return NQueensParams(N=N, partial_solution=None, positions=None)


def solve_hanoi(n: int, source: int, target: int, aux: int) -> list[tuple[int, int]]:
    """Solve Tower of Hanoi for 3 pegs"""
    if n == 1:
        return [(source, target)]
    moves = []
    moves.extend(solve_hanoi(n - 1, source, aux, target))
    moves.append((source, target))
    moves.extend(solve_hanoi(n - 1, aux, target, source))
    return moves


def generate_hanoi_params() -> HanoiParams:
    """Generate parameters for Hanoi questions"""
    num_disks = random.randint(3, 5)
    num_pegs = random.randint(3, 4)
    source = 0
    target = num_pegs - 1
    solution = solve_hanoi(num_disks, source, target, 1) if num_pegs == 3 else None
    return HanoiParams(
        num_disks=num_disks, num_pegs=num_pegs, source=source, target=target
    )


def solve_graph_coloring(
    V: int, edges: list[tuple[int, int]], num_colors: int
) -> list[int]:
    """Find a valid graph coloring"""

    def is_safe(graph: list[list[int]], colors: list[int], v: int, c: int) -> bool:
        for i in range(len(graph)):
            if graph[v][i] and colors[i] == c:
                return False
        return True

    def solve_util(graph: list[list[int]], m: int, colors: list[int], v: int) -> bool:
        if v == len(graph):
            return True
        for c in range(m):
            if is_safe(graph, colors, v, c):
                colors[v] = c
                if solve_util(graph, m, colors, v + 1):
                    return True
                colors[v] = -1
        return False

    # Create adjacency matrix
    graph = [[0] * V for _ in range(V)]
    for u, v in edges:
        graph[u][v] = graph[v][u] = 1

    colors = [-1] * V
    if solve_util(graph, num_colors, colors, 0):
        return colors
    return [-1] * V  # No solution found


def generate_graph_params() -> GraphColoringParams:
    """Generate parameters for Graph Coloring questions"""
    V = random.randint(4, 6)
    edges = []
    # Generate random edges (simple connected graph)
    for i in range(V):
        for j in range(i + 1, V):
            if random.random() < 0.7:  # 70% chance of edge
                edges.append((i, j))
    num_colors = random.randint(2, 4)
    solution = solve_graph_coloring(V, edges, num_colors)
    return GraphColoringParams(num_vertices=V, edges=edges, num_colors=num_colors)


def generate_knights_params() -> KnightsTourParams:
    """Generate parameters for Knight's Tour questions"""
    size = random.randint(5, 6)
    return KnightsTourParams(board_size=(size, size))


# Question Templates
QUESTION_TEMPLATES: Final[Dict[Topic, List[QuestionTemplate]]] = {
    Topic.N_QUEENS: [
        QuestionTemplate(
            topic=Topic.N_QUEENS,
            type=QuestionType.SOLUTION,
            name="N-Queens Solution",
            prompt_template="Find a valid solution for the {N}-Queens problem. Place {N} queens on a {N}x{N} chessboard so that no two queens threaten each other. If no solution exists, return [-1] * {N}.",
            answer_format_template="Provide a list in format: [row1,row2,...,row{N}] where each number represents the row position (0 to {max_pos}) of the queen in that column. For impossible cases, use [-1,-1,...] ({N} times).",
            param_generator=generate_nqueens_params,
            solution_generator=lambda p: solve_nqueens(p.N),
        ),
        QuestionTemplate(
            topic=Topic.N_QUEENS,
            type=QuestionType.COMPLEXITY,
            name="N-Queens Complexity",
            prompt_template="For the {N}-Queens problem:\n1. What is the time complexity of the backtracking solution?\n2. How many valid solutions exist for N={N}?",
            answer_format_template="Provide your answer in the format:\nTime Complexity: O(...)\nNumber of Solutions: ...\nExplanation: ...",
            param_generator=generate_nqueens_params,
        ),
    ],
    Topic.HANOI: [
        QuestionTemplate(
            topic=Topic.HANOI,
            type=QuestionType.SOLUTION,
            name="Generalized Hanoi Steps",
            prompt_template="Solve the Tower of Hanoi with {disks} disks and {pegs} pegs. Move all disks from peg {source} to peg {target}. If no solution exists, return an empty list [].",
            answer_format_template="List the moves in format: [[from_peg, to_peg], ...] where pegs are numbered 0 to {pegs}. For impossible cases, use [].",
            param_generator=generate_hanoi_params,
            solution_generator=lambda p: solve_hanoi(p.num_disks, p.source, p.target, 1)
            if p.num_pegs == 3
            else None,
        ),
        QuestionTemplate(
            topic=Topic.HANOI,
            type=QuestionType.COMPLEXITY,
            name="Generalized Hanoi Complexity",
            prompt_template="For the Tower of Hanoi with {disks} disks and {pegs} pegs:\n1. What is the minimum number of moves required?\n2. What is the time complexity for {disks} disks?",
            answer_format_template="Provide your answer in the format:\nMinimum Moves: ...\nTime Complexity: O(...)\nExplanation: ...",
            param_generator=generate_hanoi_params,
        ),
    ],
    Topic.GRAPH_COLORING: [
        QuestionTemplate(
            topic=Topic.GRAPH_COLORING,
            type=QuestionType.SOLUTION,
            name="Graph Coloring Solution",
            prompt_template="Color a graph with {V} vertices and edges {E} using at most {colors} colors. No adjacent vertices should have the same color. If no valid coloring exists, return [-1] * {V}.",
            answer_format_template="List colors in format: [color1,color2,...] where each number is 0 to {colors}. Example: [0,1,0,2]. For impossible cases, use a list of {V} -1's.",
            param_generator=generate_graph_params,
            solution_generator=lambda p: solve_graph_coloring(
                p.num_vertices, p.edges, p.num_colors
            ),
        ),
        QuestionTemplate(
            topic=Topic.GRAPH_COLORING,
            type=QuestionType.STRATEGY,
            name="Graph Coloring Strategy",
            prompt_template="For a graph with {V} vertices and edges {E}:\n1. Describe the best strategy to color it with minimum colors.\n2. Is coloring with {colors} or fewer colors possible? Why or why not?",
            answer_format_template="Structure your answer as:\nStrategy: ...\nPossible: Yes/No\nExplanation: ...",
            param_generator=generate_graph_params,
        ),
    ],
    Topic.KNIGHTS_TOUR: [
        QuestionTemplate(
            topic=Topic.KNIGHTS_TOUR,
            type=QuestionType.SOLUTION,
            name="Knight's Tour Path",
            prompt_template="Find a knight's tour on a {size} chessboard starting from position {start}. The tour must visit each square exactly once. If no tour exists, return an empty list [].",
            answer_format_template="List positions in format: [[row1,col1], [row2,col2], ...] where positions are 0-based indices. For impossible cases, use [].",
            param_generator=generate_knights_params,
        ),
        QuestionTemplate(
            topic=Topic.KNIGHTS_TOUR,
            type=QuestionType.STRATEGY,
            name="Knight's Tour Strategy",
            prompt_template="For a knight's tour on a {size} board:\n1. What is the best strategy to find a solution?\n2. Why might some starting positions be better than others?",
            answer_format_template="Structure your answer as:\nStrategy: ...\nStarting Positions Analysis: ...\nExplanation: ...",
            param_generator=generate_knights_params,
        ),
    ],
}


def generate_question(topic: Topic, q_type: Optional[QuestionType] = None) -> Question:
    """Generate a question for the specified topic and optional type"""
    if topic not in QUESTION_TEMPLATES:
        raise ValueError(f"Unknown topic: {topic}")

    templates = QUESTION_TEMPLATES[topic]
    if q_type:
        templates = [t for t in templates if t.type == q_type]
        if not templates:
            raise ValueError(f"No templates found for topic {topic} and type {q_type}")

    template = random.choice(templates)
    return template.generate()
