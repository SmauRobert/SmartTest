import random
import threading
from typing import Any

try:
    from . import algorithms
except ImportError:
    import problems.tower_of_hanoi.algorithms as algorithms

try:
    from ...utils.string_matching import strings_are_similar
except ImportError:
    from utils.string_matching import strings_are_similar

try:
    from ..n_queens.templates import BaseQuestionTemplate
except ImportError:
    from problems.n_queens.templates import BaseQuestionTemplate

# --- Template 4.1: Theory (Standard 3-Peg Moves) ---


class Hanoi_Theory3PegMoves(BaseQuestionTemplate):
    id = "hanoi_theory_3peg_moves"
    problem_type = "towers_of_hanoi"
    question_type = "Theory"

    def generate(self) -> dict[str, str]:
        n = random.randint(3, 10)
        self.params["n"] = n
        self.correct_answer = (2**n) - 1

        self.question_text = f"What is the minimum number of moves required to solve the standard Towers of Hanoi problem with {n} disks and 3 pegs?"
        self.answer_prompt = "Please enter a single integer."

        return {
            "question_text": self.question_text,
            "answer_prompt": self.answer_prompt,
        }

    def evaluate(self, user_answer: str) -> tuple[int, str, str]:
        user_ans_clean = user_answer.strip().lower()
        correct_answer_str = str(self.correct_answer)

        try:
            user_num = int(user_ans_clean)
            if user_num == self.correct_answer:
                score = 100
                explanation = f"Correct! The formula for {self.params['n']} disks and 3 pegs is 2<sup>N</sup> - 1. So, 2<sup>{self.params['n']}</sup> - 1 = **{self.correct_answer}**."
            else:
                score = 0
                explanation = f"Your answer was '{user_num}'. The correct answer is **{self.correct_answer}**. The formula is 2<sup>N</sup> - 1."
        except ValueError:
            score = 0
            explanation = f"Your answer '{user_answer}' is not a valid integer. The correct answer is **{self.correct_answer}**."

        return (score, correct_answer_str, explanation)


# --- Template 4.2: Theory (Recursive Step) ---


class Hanoi_TheoryRecursiveStep(BaseQuestionTemplate):
    id = "hanoi_theory_recursive_step"
    problem_type = "towers_of_hanoi"
    question_type = "Theory"

    def generate(self) -> dict[str, str]:
        n = random.randint(5, 10)
        self.params["n"] = n
        self.correct_answer = "B"

        self.question_text = f"In the optimal recursive solution for moving {n} disks from Peg A to Peg C (using Peg B as auxiliary), where must the top {n - 1} disks be moved *first*?"
        self.answer_prompt = "Please enter the destination peg ('A', 'B', or 'C')."

        return {
            "question_text": self.question_text,
            "answer_prompt": self.answer_prompt,
        }

    def evaluate(self, user_answer: str) -> tuple[int, str, str]:
        user_ans_clean = user_answer.strip().upper()

        if user_ans_clean == self.correct_answer or user_ans_clean == "AUXILIARY":
            score = 100
            explanation = f"Correct. The first step is to move the top {self.params['n'] - 1} disks to the **auxiliary peg (B)**."
        else:
            score = 0
            explanation = f"Your answer was '{user_answer}'. The correct answer is **B (the auxiliary peg)**."

        explanation += "\nThe 3-step solution is:\n1. Move N-1 disks from A to B.\n2. Move 1 disk from A to C.\n3. Move N-1 disks from B to C."
        return (score, self.correct_answer, explanation)


# --- Template 4.3: Validation (Move Viability) ---


class Hanoi_ValidationViability(BaseQuestionTemplate):
    id = "hanoi_validation_viability"
    problem_type = "towers_of_hanoi"
    question_type = "Validation"

    def generate(self) -> dict[str, str]:
        # Pegs: {'A': [5, 3], 'B': [4, 2], 'C': [1]} (bottom-to-top)
        pegs = {"A": [5, 3], "B": [4, 2], "C": [1]}

        move_type = random.choice(["valid", "invalid_size", "invalid_empty"])

        if move_type == "valid":
            # Move 1 from C to A
            peg_from, peg_to = "C", "A"
            self.correct_answer = "yes"
            self.params["reason"] = (
                f"Moving disk 1 (from {peg_from}) onto disk 3 (on {peg_to}) is a valid move."
            )
        elif move_type == "invalid_size":
            # Move 2 from B to C
            peg_from, peg_to = "B", "C"
            self.correct_answer = "no"
            self.params["reason"] = (
                f"You cannot place disk 2 (from {peg_from}) on top of the smaller disk 1 (on {peg_to})."
            )
        else:
            # Move from an empty peg (e.g., 'D')
            pegs = {"A": [3, 2, 1], "B": [], "C": []}
            peg_from, peg_to = "B", "A"
            self.correct_answer = "no"
            self.params["reason"] = f"Peg {peg_from} is empty."

        self.params["pegs"] = pegs
        self.params["from"] = peg_from
        self.params["to"] = peg_to

        self.question_text = f"Consider a Hanoi game. The pegs are: `{pegs}` (bottom-to-top). Is it a valid move to take the top disk from Peg '{peg_from}' and place it on Peg '{peg_to}'?"
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


# --- Template 4.4: Theory (Generalized Moves) ---


class Hanoi_Theory4PegEffect(BaseQuestionTemplate):
    id = "hanoi_theory_4peg_effect"
    problem_type = "towers_of_hanoi"
    question_type = "Theory"

    def generate(self) -> dict[str, str]:
        n = random.randint(20, 64)
        self.params["n"] = n
        self.correct_answer = "decreases"

        self.question_text = f"Compared to the 3-peg problem, what effect does adding a 4th peg have on the minimum number of moves required to move {n} disks?"
        self.answer_prompt = (
            "Please answer with 'Increases', 'Decreases', or 'No Effect'."
        )

        return {
            "question_text": self.question_text,
            "answer_prompt": self.answer_prompt,
        }

    def evaluate(self, user_answer: str) -> tuple[int, str, str]:
        user_ans_clean = user_answer.strip().lower()

        if user_ans_clean == self.correct_answer:
            score = 100
            explanation = f"Correct! The number of moves **Decreases** dramatically. For {self.params['n']} disks, 3 pegs takes 2<sup>{self.params['n']}</sup>-1 moves (a massive number), while the optimal 4-peg solution is much faster."
        else:
            score = 0
            explanation = f"Your answer was '{user_answer}'. The correct answer is **Decreases**. Adding pegs always reduces (or at worst, keeps equal) the number of moves."

        return (score, self.correct_answer.capitalize(), explanation)


# --- Template 4.5: Experimental (Algorithm Race) ---


class Hanoi_ExperimentalRace(BaseQuestionTemplate):
    id = "hanoi_experimental_race"
    problem_type = "towers_of_hanoi"
    question_type = "Experimental (Async)"

    def generate(self) -> dict[str, str]:
        n = random.randint(18, 22)  # Large enough to be slow
        move_count = (2**n) - 1
        self.params["n"] = n
        self.params["move_count"] = f"{move_count:,}"  # Formatted

        self.question_text = f"To generate all {self.params['move_count']} moves for a {n}-disk, 3-peg Hanoi problem, which algorithm will finish *first*: the standard Recursive algorithm or an Iterative (stack-based) algorithm?"
        self.answer_prompt = "Please enter 'Recursive' or 'Iterative'."

        return {
            "question_text": self.question_text,
            "answer_prompt": self.answer_prompt,
        }

    def evaluate(self, user_answer: str) -> tuple[int, str, str]:
        n = self.params["n"]
        results = {}

        def run_recursive():
            _, time_taken = algorithms.solve_hanoi_recursive(n)
            results["Recursive"] = time_taken

        def run_iterative():
            _, time_taken = algorithms.solve_hanoi_iterative(n)
            results["Iterative"] = time_taken

        t_rec = threading.Thread(target=run_recursive)
        t_iter = threading.Thread(target=run_iterative)

        t_rec.start()
        t_iter.start()

        t_rec.join()
        t_iter.join()

        rec_time = results.get("Recursive", float("inf"))
        iter_time = results.get("Iterative", float("inf"))

        self.correct_answer = "Recursive" if rec_time < iter_time else "Iterative"

        explanation = f"The fastest algorithm for this instance was **{self.correct_answer}**.\n\n"
        explanation += "--- Results ---\n"
        explanation += f"Recursive: {rec_time:.6f}s\n"
        explanation += f"Iterative: {iter_time:.6f}s\n"
        explanation += "\n(Note: In Python, a deep recursion can be slower due to function call overhead. An iterative approach, while more complex to write, can sometimes be faster by avoiding this.)"

        if strings_are_similar(user_answer, self.correct_answer, max_distance=3):
            score = 100
            explanation = "Correct!\n" + explanation
        else:
            score = 0
            explanation = f"Your answer was '{user_answer}'.\n" + explanation

        return (score, self.correct_answer, explanation)
