import random
import threading
from typing import Any

try:
    from . import algorithms
except ImportError:
    import problems.knights_tour.algorithms as algorithms

try:
    from ...utils.string_matching import strings_are_similar
except ImportError:
    from utils.string_matching import strings_are_similar

try:
    from ..n_queens.templates import BaseQuestionTemplate
except ImportError:
    from problems.n_queens.templates import BaseQuestionTemplate

# --- Template 2.1: Theory (Warnsdorff's Rule Name) ---


class KT_TheoryWarnsdorffName(BaseQuestionTemplate):
    id = "kt_theory_warnsdorff_name"
    problem_type = "knights_tour"
    question_type = "Theory"

    def generate(self) -> dict[str, str]:
        self.question_text = "Consider the following heuristic for the Knight's Tour problem: 'Always move to the unvisited square that has the *fewest* valid onward moves.' What is the name of this heuristic?"
        self.answer_prompt = "Please enter the name of the rule (e.g., 'Smith's Rule')."
        self.correct_answer = "Warnsdorff's Rule"
        return {
            "question_text": self.question_text,
            "answer_prompt": self.answer_prompt,
        }

    def evaluate(self, user_answer: str) -> tuple[int, str, str]:
        if strings_are_similar(user_answer, self.correct_answer, max_distance=3):
            score = 100
            explanation = "Correct! The answer is **Warnsdorff's Rule**. It is a highly effective heuristic that guides the knight toward the 'harder' squares first, preventing it from getting trapped."
        else:
            score = 0
            explanation = f"Your answer was '{user_answer}'. The correct answer is **Warnsdorff's Rule**. This heuristic guides the knight toward the 'harder' squares first, preventing it from getting trapped."
        return (score, self.correct_answer, explanation)


# --- Template 2.2: Validation (Move Viability) ---


class KT_ValidationViability(BaseQuestionTemplate):
    id = "kt_validation_viability"
    problem_type = "knights_tour"
    question_type = "Validation"

    def generate(self) -> dict[str, str]:
        n = random.choice([5, 8])
        # Generate a short, valid path
        move_list = [(0, 0), (1, 2), (2, 0)]
        last_move = move_list[-1]

        # 50% chance of a valid next move, 50% invalid
        if random.random() < 0.5:
            # Pick a valid next move
            next_move = (3, 2)  # Valid from (2, 0)
            self.correct_answer = "yes"
            self.params["reason"] = (
                f"The move from {last_move} to {next_move} is a valid L-shape to an unvisited square."
            )
        else:
            # Pick an invalid move
            invalid_type = random.choice(["shape", "visited"])
            if invalid_type == "shape":
                next_move = (3, 3)  # Not an L-shape
                self.params["reason"] = (
                    f"The move from {last_move} to {next_move} is not a valid L-shape knight's move."
                )
            else:
                next_move = (0, 0)  # Already visited
                self.params["reason"] = (
                    f"The square {next_move} has already been visited in this tour."
                )
            self.correct_answer = "no"

        self.params["move_list"] = move_list
        self.params["last_move"] = last_move
        self.params["next_move"] = next_move

        self.question_text = f"On a {n}x{n} board, given the partial tour: `{move_list}`, is the move from `{last_move}` to `{next_move}` a valid next step?"
        self.answer_prompt = "Please answer 'Yes' or 'No'."

        return {
            "question_text": self.question_text,
            "answer_prompt": self.answer_prompt,
        }

    def evaluate(self, user_answer: str) -> tuple[int, str, str]:
        user_ans_clean = user_answer.strip().lower()
        correct_str = self.correct_answer.capitalize()

        if user_ans_clean == self.correct_answer:
            score = 100
            explanation = (
                f"Correct! The answer is **{correct_str}**. {self.params['reason']}"
            )
        else:
            score = 0
            explanation = f"Your answer was '{user_answer}'. The correct answer is **{correct_str}**. {self.params['reason']}"
        return (score, correct_str, explanation)


# --- Template 2.3: Computation (Find Tour) ---


class KT_ComputationFindTour(BaseQuestionTemplate):
    id = "kt_computation_find_tour"
    problem_type = "knights_tour"
    question_type = "Computation (Async)"

    def generate(self) -> dict[str, str]:
        n = random.choice([5, 6])  # 5 or 6 is solvable
        self.params["n"] = n
        self.params["start"] = (0, 0)

        self.question_text = (
            f"Find an *open* Knight's Tour on a {n}x{n} board, starting at (0, 0)."
        )
        self.answer_prompt = f"Please provide the solution as an array of {n * n} tuples (e.g., `[(0,0), (1,2), ...]`). If no solution exists, write 'impossible'."

        return {
            "question_text": self.question_text,
            "answer_prompt": self.answer_prompt,
        }

    def evaluate(self, user_answer: str) -> tuple[int, str, str]:
        n = self.params["n"]
        user_ans_clean = user_answer.strip().lower()

        # Get a correct solution
        correct_solution, _ = algorithms.solve_kt_warnsdorff(n)
        correct_answer_str = str(correct_solution)

        if correct_solution is None:
            if user_ans_clean == "impossible":
                return (
                    100,
                    "impossible",
                    f"Correct! No solution exists for N={n} from (0,0).",
                )
            else:
                return (
                    0,
                    "impossible",
                    f"Your answer was '{user_answer}'. The correct answer is 'impossible'.",
                )

        # Try to parse user's answer
        try:
            # Use eval for tuple list, this is generally unsafe but ok in this context
            user_path = eval(user_answer)
            if not isinstance(user_path, list) or not all(
                isinstance(t, tuple) for t in user_path
            ):
                raise ValueError("Not a list of tuples")

            # 1. Check length
            if len(user_path) != n * n:
                return (
                    0,
                    correct_answer_str,
                    f"Your tour is not valid. It must have {n * n} moves, but yours has {len(user_path)}.",
                )

            # 2. Check start
            if user_path[0] != (0, 0):
                return (
                    0,
                    correct_answer_str,
                    f"Your tour must start at (0, 0), but yours starts at {user_path[0]}.",
                )

            # 3. Check uniqueness
            if len(set(user_path)) != n * n:
                return (
                    0,
                    correct_answer_str,
                    f"Your tour is not valid. You have visited at least one square twice.",
                )

            # 4. Check all moves
            for i in range(n * n - 1):
                r1, c1 = user_path[i]
                r2, c2 = user_path[i + 1]
                if not (0 <= r1 < n and 0 <= c1 < n and 0 <= r2 < n and 0 <= c2 < n):
                    return (
                        0,
                        correct_answer_str,
                        f"Your tour is not valid. Move {i + 1} from {user_path[i]} to {user_path[i + 1]} goes off the {n}x{n} board.",
                    )
                if not algorithms.is_l_shape(r1, c1, r2, c2):
                    return (
                        0,
                        correct_answer_str,
                        f"Your tour is not valid. Move {i + 1} from {user_path[i]} to {user_path[i + 1]} is not a valid knight's move.",
                    )

            # All checks passed
            return (100, str(user_path), "Excellent! Your tour is 100% valid.")

        except Exception as e:
            return (
                0,
                correct_answer_str,
                f"Your answer '{user_answer}' could not be parsed as a list of tuples (e.g., [(0,0), (1,2)]).\nA correct solution is **{correct_answer_str}**.",
            )


# --- Template 2.4: Experimental (Algorithm Race) ---


class KT_ExperimentalRace(BaseQuestionTemplate):
    id = "kt_experimental_race"
    problem_type = "knights_tour"
    question_type = "Experimental (Async)"

    def generate(self) -> dict[str, str]:
        n = random.choice([6, 7])  # 7 is slow for BT, good for comparison
        self.params["n"] = n

        self.question_text = f"For a {n}x{n} board (N={n}), which algorithm will find a *single* (open) tour first: standard Backtracking or Backtracking with Warnsdorff's Rule?"
        self.answer_prompt = "Please enter 'Backtracking' or 'Warnsdorff's Rule'."

        return {
            "question_text": self.question_text,
            "answer_prompt": self.answer_prompt,
        }

    def evaluate(self, user_answer: str) -> tuple[int, str, str]:
        n = self.params["n"]
        results = {}

        def run_bt():
            _, time_taken = algorithms.solve_kt_bt(n)
            results["Backtracking"] = time_taken

        def run_warnsdorff():
            _, time_taken = algorithms.solve_kt_warnsdorff(n)
            results["Warnsdorff's Rule"] = time_taken

        t_bt = threading.Thread(target=run_bt)
        t_warn = threading.Thread(target=run_warnsdorff)

        t_bt.start()
        t_warn.start()

        t_bt.join()
        t_warn.join()

        bt_time = results.get("Backtracking", float("inf"))
        warn_time = results.get("Warnsdorff's Rule", float("inf"))

        # Warnsdorff's will almost certainly win
        self.correct_answer = (
            "Warnsdorff's Rule" if warn_time < bt_time else "Backtracking"
        )

        explanation = f"The fastest algorithm for this instance (N={n}) was **{self.correct_answer}**.\n\n"
        explanation += "--- Results ---\n"
        explanation += f"Warnsdorff's Rule: {warn_time:.6f}s\n"
        explanation += f"Backtracking: {bt_time:.6f}s\n"
        explanation += "\n(Note: Warnsdorff's Rule is a powerful heuristic that drastically prunes the search tree, making it much faster than simple backtracking.)"

        if strings_are_similar(user_answer, self.correct_answer, max_distance=4):
            score = 100
            explanation = "Correct!\n" + explanation
        else:
            score = 0
            explanation = f"Your answer was '{user_answer}'.\n" + explanation

        return (score, self.correct_answer, explanation)
