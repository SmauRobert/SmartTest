from dataclasses import dataclass
from typing import Optional, List, Tuple, Final
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from questions_bank import (
    Question,
    QuestionType,
    NQueensParams,
    Position,
    Solution,
    Board,
)


@dataclass(frozen=True)
class EvaluationResult:
    """Result of evaluating an answer"""

    score: int
    feedback: List[str]
    is_correct: bool = False

    def format_feedback(self) -> str:
        """Format feedback list into a string"""
        return "\n".join(self.feedback)


def is_valid_n_queens_solution(N: int, solution: Solution) -> bool:
    """
    Validate a N-Queens solution.
    solution: list where index is column and value is row position
    """
    if len(solution) != N:
        return False

    if not all(isinstance(x, int) and 0 <= x < N for x in solution):
        return False

    # Check for attacks
    for i in range(N):
        for j in range(i + 1, N):
            # Same row
            if solution[i] == solution[j]:
                return False
            # Diagonal
            if abs(solution[i] - solution[j]) == abs(i - j):
                return False

    return True


def find_n_queens_solutions(
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

            if col == 0:  # Force first queen placement
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

    # Create parallel tasks starting from different positions
    with ThreadPoolExecutor(max_workers=N) as executor:
        future_to_pos = {executor.submit(solve_from_start, i): i for i in range(N)}

        try:
            for future in as_completed(future_to_pos, timeout=timeout):
                solutions.extend(future.result())
                if len(solutions) >= max_solutions:
                    break
        except TimeoutError:
            if not solutions:  # Only warn if we found no solutions
                print(f"Warning: N-Queens solution search timed out after {timeout}s")

    return solutions[:max_solutions]


def evaluate_n_queens_solution(question: Question, answer: str) -> Tuple[int, str]:
    """Evaluate a solution to the N-Queens problem"""
    feedback: List[str] = []
    N: Final[int] = question.params.N

    try:
        # Parse user solution
        solution = json.loads(answer.replace(" ", ""))

        if not isinstance(solution, list):
            return 0, "Answer must be a list of row positions"

        # Basic format validation
        if len(solution) != N:
            return 0, f"Solution must contain exactly {N} positions"

        if not all(isinstance(x, int) and 0 <= x < N for x in solution):
            return 0, f"All positions must be integers between 0 and {N - 1}"

        # Validate solution
        if is_valid_n_queens_solution(N, solution):
            feedback.append("✓ Valid solution provided!")

            # Find other valid solutions for comparison
            other_solutions = find_n_queens_solutions(N)
            if other_solutions:
                if solution in other_solutions:
                    feedback.append(
                        "✓ Your solution matches one of our known solutions"
                    )
                else:
                    feedback.append("✓ You found a different valid solution!")
                    feedback.append(f"Reference solution: {other_solutions[0]}")

            return 100, "\n".join(feedback)
        else:
            feedback.extend(
                [
                    "× Invalid solution - queens can attack each other",
                    "\nChecks performed:",
                    "- Row attacks",
                    "- Diagonal attacks",
                    "\nTry visualizing your solution on a chessboard",
                ]
            )
            return 0, "\n".join(feedback)

    except json.JSONDecodeError:
        return 0, (
            f"× Invalid format. Expected format: [row1,row2,...,row{N}]\n"
            "Example: [1,3,0,2] for N=4"
        )
    except Exception as e:
        return 0, f"× Error evaluating solution: {str(e)}"


def evaluate_attack_check(question: Question, answer: str) -> Tuple[int, str]:
    """Evaluate answer about queen attack possibility"""
    feedback: List[str] = []
    score: int = 0

    N: Final[int] = question.params.N
    positions: Final[List[Position]] = (
        question.params.positions if question.params.positions else []
    )
    target_pos: Final[Position] = positions[-1]  # Last position is the target

    # Calculate correct answer
    def is_valid_position(pos: Position) -> bool:
        row, col = pos
        for queen_row, queen_col in positions[:-1]:  # Exclude target position
            if (
                row == queen_row
                or col == queen_col
                or abs(row - queen_row) == abs(col - queen_col)
            ):
                return False
        return True

    correct_answer: bool = is_valid_position(target_pos)

    # Evaluate user's answer
    answer_text = answer.lower().strip()
    if not answer_text:
        return 0, "No answer provided"

    user_says_valid = answer_text.startswith("yes")

    # Check answer correctness
    if user_says_valid == correct_answer:
        score += 50
        feedback.append("✓ Correct assessment of position validity")
    else:
        feedback.append("× Incorrect assessment of position validity")

    # Check explanation
    keywords: Final[dict[str, str]] = {
        "row": "row attacks",
        "column": "column attacks",
        "diagonal": "diagonal attacks",
    }

    explanation_score = 0
    for keyword, description in keywords.items():
        if keyword in answer_text:
            explanation_score += 15
            feedback.append(f"✓ Correctly considered {description}")
        else:
            feedback.append(f"× Did not mention {description}")

    score += min(50, explanation_score)

    return score, "\n".join(feedback)


def evaluate_answer(question: Question, answer: str) -> Tuple[int, str]:
    """Main evaluation function that routes to specific evaluators"""
    evaluator_map: Final[dict[QuestionType, callable]] = {
        QuestionType.SOLUTION: evaluate_n_queens_solution,
        QuestionType.ATTACK_CHECK: evaluate_attack_check,
    }

    evaluator = evaluator_map.get(question.type)
    if not evaluator:
        raise ValueError(f"No evaluator found for question type: {question.type}")

    return evaluator(question, answer.strip())
