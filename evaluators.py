from dataclasses import dataclass
from typing import List, Tuple, Optional, Final, Dict, Any
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

from questions_bank import (
    Topic,
    QuestionType,
    Question,
    NQueensParams,
    HanoiParams,
    GraphColoringParams,
    KnightsTourParams,
    Position,
    Board,
    Solution,
)


@dataclass
class EvaluationResult:
    """Result of evaluating an answer"""

    score: int
    feedback: List[str]
    is_correct: bool
    optimal_solution: Optional[str] = None

    def format_feedback(self) -> str:
        """Format feedback list into a string"""
        if self.optimal_solution:
            self.feedback.append(f"\nOptimal solution: {self.optimal_solution}")
        return "\n".join(self.feedback)


def evaluate_answer(question: Question, answer: str) -> tuple[float, str]:
    """Main evaluation function that routes to specific evaluators and includes optimal solutions"""
    evaluator_map: Final[Dict[Topic, Dict[QuestionType, Any]]] = {
        Topic.N_QUEENS: {
            QuestionType.SOLUTION: evaluate_nqueens_solution,
            QuestionType.COMPLEXITY: evaluate_nqueens_complexity,
        },
        Topic.HANOI: {
            QuestionType.SOLUTION: evaluate_hanoi_solution,
            QuestionType.COMPLEXITY: evaluate_hanoi_complexity,
        },
        Topic.GRAPH_COLORING: {
            QuestionType.SOLUTION: evaluate_graph_coloring_solution,
            QuestionType.STRATEGY: evaluate_graph_coloring_strategy,
        },
        Topic.KNIGHTS_TOUR: {
            QuestionType.SOLUTION: evaluate_knights_tour_solution,
            QuestionType.STRATEGY: evaluate_knights_tour_strategy,
        },
    }

    topic_evaluators = evaluator_map.get(question.topic)
    if not topic_evaluators:
        raise ValueError(f"No evaluators found for topic: {question.topic}")

    evaluator = topic_evaluators.get(question.type)
    if not evaluator:
        raise ValueError(
            f"No evaluator found for topic {question.topic} and type {question.type}"
        )

    # Create evaluator result with optimal solution if available
    result = evaluator(question, answer.strip())
    if question.solution is not None:
        result.optimal_solution = str(question.solution)

    return result.score, result.format_feedback()


# N-Queens Evaluators
def is_valid_nqueens_solution(N: int, solution: Solution) -> bool:
    """Validate a N-Queens solution"""
    if len(solution) != N:
        return False

    if not all(isinstance(x, int) and 0 <= x < N for x in solution):
        return False

    # Check for attacks
    for i in range(N):
        for j in range(i + 1, N):
            # Same row check
            if solution[i] == solution[j]:
                return False
            # Diagonal check
            if abs(solution[i] - solution[j]) == abs(i - j):
                return False

    return True


def find_nqueens_solutions(
    N: int, max_solutions: int = 4, timeout: int = 5
) -> List[Solution]:
    """Find multiple solutions for N-Queens problem using parallel search"""
    solutions: List[Solution] = []

    def solve_from_start(start_pos: int) -> List[Solution]:
        local_solutions: List[Solution] = []

        def can_place(board: List[int], col: int, row: int) -> bool:
            for i in range(col):
                if board[i] == row or abs(board[i] - row) == abs(i - col):
                    return False
            return True

        def solve_util(board: List[int], col: int) -> None:
            if col == N:
                local_solutions.append(board[:])
                return

            if col == 0:
                rows = [start_pos]
            else:
                rows = range(N)

            for row in rows:
                if can_place(board, col, row):
                    board[col] = row
                    solve_util(board, col + 1)
                    if len(local_solutions) >= max_solutions:
                        return

        board = [-1] * N
        solve_util(board, 0)
        return local_solutions

    with ThreadPoolExecutor(max_workers=N) as executor:
        future_to_pos = {executor.submit(solve_from_start, i): i for i in range(N)}
        try:
            for future in as_completed(future_to_pos, timeout=timeout):
                solutions.extend(future.result())
                if len(solutions) >= max_solutions:
                    break
        except TimeoutError:
            if not solutions:
                print(f"Warning: N-Queens solution search timed out after {timeout}s")

    return solutions[:max_solutions]


def evaluate_nqueens_solution(question: Question, answer: str) -> EvaluationResult:
    """Evaluate N-Queens solution"""
    params = question.params
    if not isinstance(params, NQueensParams):
        raise ValueError("Invalid parameter type for N-Queens solution")

    N: Final[int] = params.N
    feedback: List[str] = []

    try:
        solution = json.loads(answer.replace(" ", ""))
        if not isinstance(solution, list):
            return EvaluationResult(
                score=0,
                feedback=["Answer must be a list of row positions"],
                is_correct=False,
            )

        # Validate format and solution
        if len(solution) != N:
            return EvaluationResult(
                score=0,
                feedback=[f"Solution must contain exactly {N} positions"],
                is_correct=False,
            )

        if not all(isinstance(x, int) and 0 <= x < N for x in solution):
            return EvaluationResult(
                score=0,
                feedback=[f"All positions must be integers between 0 and {N - 1}"],
                is_correct=False,
            )

        if is_valid_nqueens_solution(N, solution):
            feedback.append("✓ Valid solution provided!")
            other_solutions = find_nqueens_solutions(N)

            if other_solutions:
                if solution in other_solutions:
                    feedback.append(
                        "✓ Your solution matches one of our known solutions"
                    )
                else:
                    feedback.append("✓ You found a different valid solution!")
                    feedback.append(f"Reference solution: {other_solutions[0]}")

            return EvaluationResult(score=100, feedback=feedback, is_correct=True)
        else:
            return EvaluationResult(
                score=0,
                feedback=[
                    "× Invalid solution - queens can attack each other",
                    "\nChecks performed:",
                    "- Row attacks",
                    "- Diagonal attacks",
                    "\nTry visualizing your solution on a chessboard",
                ],
                is_correct=False,
            )

    except json.JSONDecodeError:
        return EvaluationResult(
            score=0,
            feedback=[
                f"× Invalid format. Expected format: [row1,row2,...,row{N}]",
                "Example: [1,3,0,2] for N=4",
            ],
            is_correct=False,
        )
    except Exception as e:
        return EvaluationResult(
            score=0,
            feedback=[f"× Error evaluating solution: {str(e)}"],
            is_correct=False,
        )


def evaluate_nqueens_complexity(question: Question, answer: str) -> EvaluationResult:
    """Evaluate N-Queens complexity analysis"""
    params = question.params
    if not isinstance(params, NQueensParams):
        raise ValueError("Invalid parameter type for N-Queens complexity")

    N: Final[int] = params.N
    feedback: List[str] = []
    score = 0

    # Expected key components in the answer
    components = {
        "O(N!)": "time complexity",
        "recursive": "recursive nature",
        "backtrack": "backtracking concept",
        f"{N}!": "specific case analysis",
        "solutions": "multiple solutions discussion",
    }

    answer_lower = answer.lower()
    for key, description in components.items():
        if key.lower() in answer_lower:
            score += 20
            feedback.append(f"✓ Correctly discussed {description}")
        else:
            feedback.append(f"× Missing discussion of {description}")

    is_correct = score >= 80
    if is_correct:
        feedback.append("\n✓ Excellent understanding of the complexity!")
    else:
        feedback.append("\nSuggested improvements:")
        feedback.append("- Discuss both time and space complexity")
        feedback.append("- Explain why it's factorial complexity")
        feedback.append("- Mention how branching factor affects the search space")

    return EvaluationResult(score=score, feedback=feedback, is_correct=is_correct)


# Hanoi Tower Evaluators
def evaluate_hanoi_solution(question: Question, answer: str) -> EvaluationResult:
    """Evaluate Generalized Tower of Hanoi solution"""
    params = question.params
    if not isinstance(params, HanoiParams):
        raise ValueError("Invalid parameter type for Hanoi solution")

    feedback: List[str] = []
    score = 0

    try:
        moves = json.loads(answer.replace(" ", ""))
        if not isinstance(moves, list):
            return EvaluationResult(
                score=0, feedback=["Answer must be a list of moves"], is_correct=False
            )

        # Validate moves
        valid_moves = True
        invalid_reasons = []
        for move in moves:
            if not isinstance(move, list) or len(move) != 2:
                valid_moves = False
                invalid_reasons.append("Each move must be a pair [from_peg, to_peg]")
                break
            from_peg, to_peg = move
            if not (0 <= from_peg < params.num_pegs and 0 <= to_peg < params.num_pegs):
                valid_moves = False
                invalid_reasons.append(
                    f"Pegs must be between 0 and {params.num_pegs - 1}"
                )
                break

        if valid_moves:
            # Check if solution is optimal
            min_moves = 2**params.num_disks - 1
            if len(moves) == min_moves:
                score = 100
                feedback.append("✓ Perfect! You found the optimal solution")
            elif len(moves) <= min_moves * 1.5:
                score = 80
                feedback.append("✓ Good solution, but not optimal")
                feedback.append(f"Optimal solution uses {min_moves} moves")
            else:
                score = 50
                feedback.append("× Solution uses too many moves")
                feedback.append(f"Your solution: {len(moves)} moves")
                feedback.append(f"Optimal solution: {min_moves} moves")
        else:
            feedback.extend(["× Invalid move format"] + invalid_reasons)
            return EvaluationResult(score=0, feedback=feedback, is_correct=False)

    except json.JSONDecodeError:
        return EvaluationResult(
            score=0,
            feedback=[
                "× Invalid format. Expected a list of moves: [[from_peg, to_peg], ...]"
            ],
            is_correct=False,
        )

    return EvaluationResult(score=score, feedback=feedback, is_correct=score >= 80)


def evaluate_hanoi_complexity(question: Question, answer: str) -> EvaluationResult:
    """Evaluate Hanoi complexity analysis"""
    params = question.params
    if not isinstance(params, HanoiParams):
        raise ValueError("Invalid parameter type for Hanoi complexity")

    feedback: List[str] = []
    score = 0

    # Check for key concepts
    concepts = {
        "2^n": "exponential growth",
        "O(2^n)": "time complexity",
        "recursive": "recursive solution",
        "optimal": "optimality discussion",
        f"{params.num_pegs}": "number of pegs consideration",
    }

    answer_lower = answer.lower()
    for concept, description in concepts.items():
        if concept.lower() in answer_lower:
            score += 20
            feedback.append(f"✓ Correctly discussed {description}")
        else:
            feedback.append(f"× Missing discussion of {description}")

    is_correct = score >= 80
    if not is_correct:
        feedback.append("\nSuggestion: Include discussion of:")
        feedback.append("- How the number of moves grows with n")
        feedback.append("- Why it's exponential")
        feedback.append("- How additional pegs affect the solution")

    return EvaluationResult(score=score, feedback=feedback, is_correct=is_correct)


# Graph Coloring Evaluators
def evaluate_graph_coloring_solution(
    question: Question, answer: str
) -> EvaluationResult:
    """Evaluate Graph Coloring solution"""
    params = question.params
    if not isinstance(params, GraphColoringParams):
        raise ValueError("Invalid parameter type for Graph Coloring solution")

    feedback: List[str] = []
    score = 0

    try:
        colors = json.loads(answer.replace(" ", ""))
        if not isinstance(colors, list):
            return EvaluationResult(
                score=0,
                feedback=["Answer must be a list of color indices"],
                is_correct=False,
            )

        # Validate format
        if len(colors) != params.num_vertices:
            return EvaluationResult(
                score=0,
                feedback=[
                    f"Solution must assign colors to all {params.num_vertices} vertices"
                ],
                is_correct=False,
            )

        if not all(isinstance(c, int) and 0 <= c < params.num_colors for c in colors):
            return EvaluationResult(
                score=0,
                feedback=[
                    f"All colors must be integers between 0 and {params.num_colors - 1}"
                ],
                is_correct=False,
            )

        # Check if coloring is valid
        is_valid = True
        conflicts = []
        for v1, v2 in params.edges:
            if colors[v1] == colors[v2]:
                is_valid = False
                conflicts.append(
                    f"Vertices {v1} and {v2} have the same color {colors[v1]}"
                )

        if is_valid:
            num_colors_used = len(set(colors))
            if num_colors_used <= params.num_colors - 1:
                score = 100
                feedback.append(f"✓ Perfect! Used only {num_colors_used} colors")
            else:
                score = 90
                feedback.append(
                    "✓ Valid solution, but might be possible to use fewer colors"
                )
        else:
            feedback.append("× Invalid coloring - adjacent vertices have same color:")
            feedback.extend(conflicts)
            return EvaluationResult(score=0, feedback=feedback, is_correct=False)

    except json.JSONDecodeError:
        return EvaluationResult(
            score=0,
            feedback=["× Invalid format. Expected a list of color indices [c1,c2,...]"],
            is_correct=False,
        )

    return EvaluationResult(score=score, feedback=feedback, is_correct=score >= 90)


def evaluate_graph_coloring_strategy(
    question: Question, answer: str
) -> EvaluationResult:
    """Evaluate Graph Coloring strategy explanation"""
    params = question.params
    if not isinstance(params, GraphColoringParams):
        raise ValueError("Invalid parameter type for Graph Coloring strategy")

    feedback: List[str] = []
    score = 0

    # Key concepts to look for
    concepts = {
        "greedy": "greedy approach",
        "degree": "vertex degree consideration",
        "welsh-powell": "Welsh-Powell algorithm",
        "backtrack": "backtracking possibility",
        "chromatic": "chromatic number",
    }

    answer_lower = answer.lower()
    for concept, description in concepts.items():
        if concept in answer_lower:
            score += 20
            feedback.append(f"✓ Mentioned {description}")
        else:
            feedback.append(f"× Did not discuss {description}")

    is_correct = score >= 60
    if not is_correct:
        feedback.append("\nSuggested improvements:")
        feedback.append("- Discuss different coloring algorithms")
        feedback.append("- Explain how to choose vertex ordering")
        feedback.append("- Analyze the trade-offs between approaches")

    return EvaluationResult(score=score, feedback=feedback, is_correct=is_correct)


# Knight's Tour Evaluators
def evaluate_knights_tour_solution(question: Question, answer: str) -> EvaluationResult:
    """Evaluate Knight's Tour solution"""
    params = question.params
    if not isinstance(params, KnightsTourParams):
        raise ValueError("Invalid parameter type for Knight's Tour solution")

    rows, cols = params.board_size
    feedback: List[str] = []
    score = 0

    try:
        path = json.loads(answer.replace(" ", ""))
        if not isinstance(path, list):
            return EvaluationResult(
                score=0,
                feedback=["Answer must be a list of positions"],
                is_correct=False,
            )

        # Validate format
        if len(path) != rows * cols:
            return EvaluationResult(
                score=0,
                feedback=[f"Tour must visit all {rows * cols} squares exactly once"],
                is_correct=False,
            )

        # Check if moves are valid knight moves and within board
        is_valid = True
        invalid_moves = []
        visited = set()

        for i, pos in enumerate(path):
            if not isinstance(pos, list) or len(pos) != 2:
                return EvaluationResult(
                    score=0,
                    feedback=["Each position must be a pair [row, col]"],
                    is_correct=False,
                )

            r, c = pos
            if not (0 <= r < rows and 0 <= c < cols):
                is_valid = False
                invalid_moves.append(f"Position {pos} is outside the board")
                break

            pos_tuple = (r, c)
            if pos_tuple in visited:
                is_valid = False
                invalid_moves.append(f"Square {pos} is visited multiple times")
                break
            visited.add(pos_tuple)

            if i > 0:
                prev_r, prev_c = path[i - 1]
                dr = abs(r - prev_r)
                dc = abs(c - prev_c)
                if not ((dr == 2 and dc == 1) or (dr == 1 and dc == 2)):
                    is_valid = False
                    invalid_moves.append(
                        f"Invalid knight move from {path[i - 1]} to {pos}"
                    )
                    break

        if is_valid:
            score = 100
            feedback.append("✓ Valid knight's tour found!")
            if path[0] == path[-1]:
                feedback.append("✓ Bonus: Tour is closed (ends where it started)")
        else:
            feedback.append("× Invalid tour:")
            feedback.extend(invalid_moves)
            return EvaluationResult(score=0, feedback=feedback, is_correct=False)

    except json.JSONDecodeError:
        return EvaluationResult(
            score=0,
            feedback=[
                "× Invalid format. Expected a list of positions: [[row1,col1], ...]"
            ],
            is_correct=False,
        )

    return EvaluationResult(score=score, feedback=feedback, is_correct=score == 100)


def evaluate_knights_tour_strategy(question: Question, answer: str) -> EvaluationResult:
    """Evaluate Knight's Tour strategy explanation"""
    params = question.params
    if not isinstance(params, KnightsTourParams):
        raise ValueError("Invalid parameter type for Knight's Tour strategy")

    feedback: List[str] = []
    score = 0

    # Key concepts to look for
    concepts = {
        "warnsdorff": "Warnsdorff's rule",
        "heuristic": "heuristic approach",
        "backtrack": "backtracking",
        "closed": "closed tour consideration",
        "degree": "accessibility/degree heuristic",
    }

    answer_lower = answer.lower()
    for concept, description in concepts.items():
        if concept in answer_lower:
            score += 20
            feedback.append(f"✓ Discussed {description}")
        else:
            feedback.append(f"× Did not mention {description}")

    is_correct = score >= 60
    if not is_correct:
        feedback.append("\nSuggested improvements:")
        feedback.append("- Explain Warnsdorff's rule")
        feedback.append("- Discuss importance of starting position")
        feedback.append("- Consider corner and edge cases")

    return EvaluationResult(score=score, feedback=feedback, is_correct=is_correct)
