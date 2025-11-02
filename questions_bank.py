from dataclasses import dataclass
from typing import Callable, TypeVar, List, Optional, Final
import random
from enum import Enum, auto


class QuestionType(Enum):
    """Types of N-Queens related questions"""

    SOLUTION = auto()
    ATTACK_CHECK = auto()


T = TypeVar("T")
Position = tuple[int, int]
Board = List[List[int]]
Solution = List[int]  # row positions for each column


@dataclass(frozen=True)
class NQueensParams:
    """Parameters for N-Queens questions"""

    N: int
    positions: Optional[List[Position]] = None  # For attack check questions
    current_state: Optional[Solution] = None  # For next move questions
    next_col: Optional[int] = None  # For next move questions


@dataclass(frozen=True)
class Question:
    """Represents a generated question instance"""

    id: str
    type: QuestionType
    name: str
    prompt: str
    params: NQueensParams
    answer_format: str
    solution: Optional[Solution] = None


@dataclass(frozen=True)
class QuestionTemplate:
    """Template for generating questions"""

    type: QuestionType
    name: str
    prompt_template: str
    answer_format_template: str
    param_generator: Callable[[], NQueensParams]
    solution_generator: Optional[Callable[[NQueensParams], Solution]] = None

    def generate(self) -> Question:
        """Generate a question instance from this template"""
        params = self.param_generator()
        positions = params.positions if params.positions else []
        prompt = self.prompt_template.format(
            N=params.N,
            existing=positions[:-1],
            target=positions[-1] if positions else (0, 0),
        )
        answer_format = self.answer_format_template.format(
            N=params.N, max_pos=params.N - 1
        )
        solution = self.solution_generator(params) if self.solution_generator else None

        return Question(
            id=f"{self.type.name}_{params.N}",
            type=self.type,
            name=self.name,
            prompt=prompt,
            params=params,
            answer_format=answer_format,
            solution=solution,
        )


def generate_solution_params() -> NQueensParams:
    """Generate parameters for solution-finding questions"""
    return NQueensParams(N=random.randint(4, 8))


def generate_attack_check_params() -> NQueensParams:
    """Generate parameters for attack-checking questions"""
    N = random.randint(4, 8)
    # Generate 2-3 random queen positions
    num_queens = random.randint(2, 3)
    positions: List[Position] = []

    for _ in range(num_queens):
        while True:
            pos = (random.randint(0, N - 1), random.randint(0, N - 1))
            # Check if position conflicts with existing queens
            valid = True
            for existing in positions:
                if (
                    pos[0] == existing[0]  # same row
                    or pos[1] == existing[1]  # same column
                    or abs(pos[0] - existing[0]) == abs(pos[1] - existing[1])
                ):  # diagonal
                    valid = False
                    break
            if valid:
                positions.append(pos)
                break

    return NQueensParams(N=N, positions=positions)


def solve_n_queens(params: NQueensParams) -> Optional[Solution]:
    """Generate a valid N-Queens solution"""
    N: Final[int] = params.N

    def is_safe(board: Board, row: int, col: int) -> bool:
        # Check row on left side
        for j in range(col):
            if board[row][j] == 1:
                return False

        # Check upper diagonal on left side
        for i, j in zip(range(row, -1, -1), range(col, -1, -1)):
            if board[i][j] == 1:
                return False

        # Check lower diagonal on left side
        for i, j in zip(range(row, N, 1), range(col, -1, -1)):
            if board[i][j] == 1:
                return False

        return True

    def solve_util(board: Board, col: int) -> tuple[bool, Board]:
        if col >= N:
            return True, board

        for i in range(N):
            if is_safe(board, i, col):
                board[i][col] = 1
                success, result = solve_util(board, col + 1)
                if success:
                    return True, result
                board[i][col] = 0

        return False, board

    # Initialize board
    board: Board = [[0 for _ in range(N)] for _ in range(N)]

    # Find solution
    success, solution = solve_util(board, 0)

    if not success:
        return None

    # Convert to column representation [row indices for each column]
    result: Solution = []
    for j in range(N):
        for i in range(N):
            if solution[i][j] == 1:
                result.append(i)
                break

    return result


# Define question templates
QUESTION_TEMPLATES: Final[dict[QuestionType, QuestionTemplate]] = {
    QuestionType.SOLUTION: QuestionTemplate(
        type=QuestionType.SOLUTION,
        name="N-Queens Solution",
        prompt_template="Find a valid solution for the {N}-Queens problem. Place {N} queens on a {N}x{N} chessboard so that no two queens threaten each other.",
        answer_format_template="Provide a list of {N} integers [row1,row2,...,row{N}] where each number represents the row position (0 to {max_pos}) of the queen in that column.",
        param_generator=generate_solution_params,
        solution_generator=solve_n_queens,
    ),
    QuestionType.ATTACK_CHECK: QuestionTemplate(
        type=QuestionType.ATTACK_CHECK,
        name="N-Queens Attack Check",
        prompt_template="Given a {N}x{N} chessboard with queens at positions {existing}, would placing a new queen at position {target} be valid (no attacks)?",
        answer_format_template="Answer with 'Yes' or 'No' followed by your explanation of why, checking rows, columns, and diagonals.",
        param_generator=generate_attack_check_params,
    ),
}


def generate_question(question_type: QuestionType) -> Question:
    """Generate a question instance of the specified type"""
    if question_type not in QUESTION_TEMPLATES:
        raise ValueError(f"Unknown question type: {question_type}")

    template = QUESTION_TEMPLATES[question_type]
    return template.generate()
