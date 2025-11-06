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
        n = random.choice([5, 6, 7, 8])

        # Generate a random valid path using partial backtracking
        path_length = random.randint(3, 8)
        move_list = self._generate_valid_path(n, path_length)

        if not move_list or len(move_list) < 2:
            # Fallback to simple path if generation fails
            move_list = [(0, 0), (1, 2), (2, 0)]

        last_move = move_list[-1]

        # 50% chance of a valid next move, 50% invalid
        if random.random() < 0.5:
            # Find valid next moves
            valid_moves = self._get_valid_moves(last_move, n, set(move_list))
            if valid_moves:
                next_move = random.choice(valid_moves)
                self.correct_answer = "yes"
                self.params["reason"] = (
                    f"The move from {last_move} to {next_move} is a valid L-shape to an unvisited square."
                )
            else:
                # No valid moves available, force invalid
                next_move = (0, 0) if (0, 0) in move_list else last_move
                self.correct_answer = "no"
                self.params["reason"] = (
                    f"The square {next_move} has already been visited in this tour."
                )
        else:
            # Pick an invalid move
            invalid_type = random.choice(["shape", "visited"])
            if invalid_type == "shape":
                # Not an L-shape move
                candidates = [
                    (last_move[0] + dx, last_move[1] + dy)
                    for dx in [-2, -1, 0, 1, 2]
                    for dy in [-2, -1, 0, 1, 2]
                    if (dx, dy)
                    not in [
                        (2, 1),
                        (2, -1),
                        (-2, 1),
                        (-2, -1),
                        (1, 2),
                        (1, -2),
                        (-1, 2),
                        (-1, -2),
                    ]
                    and (dx != 0 or dy != 0)
                    and 0 <= last_move[0] + dx < n
                    and 0 <= last_move[1] + dy < n
                ]
                if candidates:
                    next_move = random.choice(candidates)
                else:
                    next_move = (last_move[0], last_move[1])
                self.params["reason"] = (
                    f"The move from {last_move} to {next_move} is not a valid L-shape knight's move."
                )
            else:
                # Already visited
                next_move = (
                    random.choice(move_list[:-1])
                    if len(move_list) > 1
                    else move_list[0]
                )
                self.params["reason"] = (
                    f"The square {next_move} has already been visited in this tour."
                )
            self.correct_answer = "no"

        self.params["move_list"] = move_list
        self.params["last_move"] = last_move
        self.params["next_move"] = next_move
        self.params["n"] = n

        self.question_text = f"On a {n}x{n} board, given the partial tour: `{move_list}`, is the move from `{last_move}` to `{next_move}` a valid next step?"
        self.answer_prompt = "Please answer 'Yes' or 'No'."

        return {
            "question_text": self.question_text,
            "answer_prompt": self.answer_prompt,
        }

    def _get_valid_moves(self, pos, n, visited):
        """Get all valid knight moves from position that haven't been visited."""
        moves = []
        deltas = [
            (2, 1),
            (2, -1),
            (-2, 1),
            (-2, -1),
            (1, 2),
            (1, -2),
            (-1, 2),
            (-1, -2),
        ]
        for dr, dc in deltas:
            new_r, new_c = pos[0] + dr, pos[1] + dc
            if 0 <= new_r < n and 0 <= new_c < n and (new_r, new_c) not in visited:
                moves.append((new_r, new_c))
        return moves

    def _generate_valid_path(self, n, length):
        """Generate a valid partial knight's tour path using backtracking."""
        # Start from random position
        start_r = random.randint(0, n - 1)
        start_c = random.randint(0, n - 1)
        path = [(start_r, start_c)]
        visited = {(start_r, start_c)}

        attempts = 0
        max_attempts = 100

        while len(path) < length and attempts < max_attempts:
            current = path[-1]
            valid_moves = self._get_valid_moves(current, n, visited)

            if valid_moves:
                # Choose random valid move
                next_pos = random.choice(valid_moves)
                path.append(next_pos)
                visited.add(next_pos)
                attempts = 0
            else:
                # Backtrack
                if len(path) > 1:
                    removed = path.pop()
                    visited.remove(removed)
                    attempts += 1
                else:
                    break

        return path

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
        n = random.choice([3, 4, 5, 6, 7])  # Wider range, some unsolvable
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
        n = random.choice([5, 6, 7, 8])  # Wider range for more variety
        self.params["n"] = n

        # Randomly choose which algorithms to compare (2-3 algorithms)
        all_algorithms = ["Backtracking", "Warnsdorff's Rule", "Random Walk"]
        num_algorithms = random.choice([2, 3])
        self.params["algorithms"] = random.sample(all_algorithms, num_algorithms)

        algo_list = " vs ".join(self.params["algorithms"])
        self.question_text = f"For a {n}x{n} board (N={n}), which algorithm will find a *single* (open) tour first: {algo_list}?"
        self.answer_prompt = (
            f"Please enter one of: {', '.join(self.params['algorithms'])}."
        )

        return {
            "question_text": self.question_text,
            "answer_prompt": self.answer_prompt,
        }

    def evaluate(self, user_answer: str) -> tuple[int, str, str]:
        n = self.params["n"]
        algorithms_to_test = self.params["algorithms"]
        results = {}
        threads = []

        # Define runner functions for each algorithm
        def run_bt():
            _, time_taken = algorithms.solve_kt_bt(n)
            results["Backtracking"] = time_taken

        def run_warnsdorff():
            _, time_taken = algorithms.solve_kt_warnsdorff(n)
            results["Warnsdorff's Rule"] = time_taken

        def run_random_walk():
            # Random walk with multiple attempts
            best_time = float("inf")
            for attempt in range(3):
                path, time_taken = algorithms.solve_kt_random_walk(n, max_attempts=50)
                if path and time_taken < best_time:
                    best_time = time_taken
                    break
            results["Random Walk"] = (
                best_time if best_time != float("inf") else float("inf")
            )

        # Map algorithm names to their runner functions
        algo_runners = {
            "Backtracking": run_bt,
            "Warnsdorff's Rule": run_warnsdorff,
            "Random Walk": run_random_walk,
        }

        # Start threads for selected algorithms
        for algo_name in algorithms_to_test:
            if algo_name in algo_runners:
                t = threading.Thread(target=algo_runners[algo_name])
                t.start()
                threads.append(t)

        # Wait for all threads to complete
        for t in threads:
            t.join()

        # Find the fastest algorithm
        fastest_time = float("inf")
        fastest_algo = None
        for algo_name in algorithms_to_test:
            algo_time = results.get(algo_name, float("inf"))
            if algo_time < fastest_time:
                fastest_time = algo_time
                fastest_algo = algo_name

        self.correct_answer = fastest_algo if fastest_algo else algorithms_to_test[0]

        explanation = f"The fastest algorithm for this instance (N={n}) was **{self.correct_answer}**.\n\n"
        explanation += "--- Results ---\n"
        for algo_name in algorithms_to_test:
            algo_time = results.get(algo_name, float("inf"))
            if algo_time == float("inf"):
                explanation += f"{algo_name}: Failed to find solution\n"
            else:
                explanation += f"{algo_name}: {algo_time:.6f}s\n"

        explanation += "\n(Note: Warnsdorff's Rule uses a heuristic to prioritize moves, often outperforming backtracking. Random Walk can be fast but is unreliable.)"

        if strings_are_similar(user_answer, self.correct_answer, max_distance=4):
            score = 100
            explanation = "Correct!\n" + explanation
        else:
            score = 0
            explanation = f"Your answer was '{user_answer}'.\n" + explanation

        return (score, self.correct_answer, explanation)
