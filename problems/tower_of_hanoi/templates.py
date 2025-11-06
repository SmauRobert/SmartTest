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
        num_pegs = random.choice([3, 4])  # Randomize number of pegs
        self.params["n"] = n
        self.params["pegs"] = num_pegs

        if num_pegs == 3:
            self.correct_answer = (2**n) - 1
            formula = "2^N - 1"
        else:  # 4 pegs - Frame-Stewart algorithm (approximation)
            # For 4 pegs, use Frame-Stewart optimal solution
            # T(n) ≈ 2*sqrt(n) * 2^sqrt(n) but for small n we can compute exactly
            # Simplified: we'll use a lookup or recursive formula
            # For simplicity, we'll use the known optimal values for small n
            optimal_4peg = {3: 5, 4: 9, 5: 13, 6: 17, 7: 21, 8: 25, 9: 29, 10: 33}
            self.correct_answer = optimal_4peg.get(n, (2**n) - 1)
            formula = "Frame-Stewart algorithm"

        self.question_text = f"What is the minimum number of moves required to solve the Towers of Hanoi problem with {n} disks and {num_pegs} pegs?"
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
                if self.params["pegs"] == 3:
                    explanation = f"Correct! The formula for {self.params['n']} disks and 3 pegs is 2^N - 1. So, 2^{self.params['n']} - 1 = **{self.correct_answer}**."
                else:
                    explanation = f"Correct! For {self.params['n']} disks and 4 pegs, the Frame-Stewart algorithm gives **{self.correct_answer}** moves (much better than the 3-peg solution of {(2 ** self.params['n']) - 1} moves)."
            else:
                score = 0
                if self.params["pegs"] == 3:
                    explanation = f"Your answer was '{user_num}'. The correct answer is **{self.correct_answer}**. The formula is 2^N - 1."
                else:
                    explanation = f"Your answer was '{user_num}'. The correct answer is **{self.correct_answer}**. With 4 pegs, the Frame-Stewart algorithm finds a much more efficient solution than the standard 3-peg approach."
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
        # Generate a random valid configuration
        num_disks = random.randint(3, 6)  # Total number of disks
        pegs = {"A": [], "B": [], "C": []}
        available_disks = list(range(1, num_disks + 1))

        # Randomly distribute disks while maintaining validity
        while available_disks:
            # Choose a random peg that can accept the disk
            valid_pegs = []
            disk = available_disks[-1]  # Largest available disk

            for peg in pegs:
                # A peg is valid if it's empty or its top disk is larger than current disk
                if not pegs[peg] or pegs[peg][-1] > disk:
                    valid_pegs.append(peg)

            if valid_pegs:
                chosen_peg = random.choice(valid_pegs)
                pegs[chosen_peg].append(available_disks.pop())

        # Generate a move (valid or invalid)
        move_type = random.choice(["valid", "invalid_size", "invalid_empty"])

        # Find all possible source pegs (non-empty pegs)
        source_pegs = [peg for peg in pegs if pegs[peg]]

        if move_type == "valid":
            # Find a valid move
            peg_from = random.choice(source_pegs)
            moving_disk = pegs[peg_from][-1]
            valid_destinations = [
                peg for peg in pegs if not pegs[peg] or pegs[peg][-1] > moving_disk
            ]
            if valid_destinations:
                peg_to = random.choice(valid_destinations)
                self.correct_answer = "yes"
                top_disk_to = (
                    f"disk {pegs[peg_to][-1]} (on {peg_to})"
                    if pegs[peg_to]
                    else f"empty peg {peg_to}"
                )
                self.params["reason"] = (
                    f"Moving disk {moving_disk} (from {peg_from}) onto {top_disk_to} is a valid move."
                )
            else:
                # Fallback in case no valid moves exist
                move_type = "invalid_size"

        if move_type == "invalid_size":
            # Find an invalid size move
            peg_from = random.choice(source_pegs)
            moving_disk = pegs[peg_from][-1]
            invalid_destinations = [
                peg for peg in pegs if pegs[peg] and pegs[peg][-1] < moving_disk
            ]
            if invalid_destinations:
                peg_to = random.choice(invalid_destinations)
                self.correct_answer = "no"
                self.params["reason"] = (
                    f"You cannot place disk {moving_disk} (from {peg_from}) on top of the smaller disk {pegs[peg_to][-1]} (on {peg_to})."
                )
            else:
                move_type = "invalid_empty"

        if move_type == "invalid_empty":
            # Try to move from an empty peg
            empty_pegs = [peg for peg in pegs if not pegs[peg]]
            if empty_pegs:
                peg_from = random.choice(empty_pegs)
                peg_to = random.choice([peg for peg in pegs if peg != peg_from])
            else:
                # If no empty pegs, create one
                pegs = {"A": [], "B": [3, 2, 1], "C": []}
                peg_from = "A"
                peg_to = "B"
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
        n = random.randint(15, 20)  # Varied range for different comparisons
        move_count = (2**n) - 1
        self.params["n"] = n
        self.params["move_count"] = f"{move_count:,}"  # Formatted

        # Randomly choose which algorithms to compare (2-3 algorithms)
        all_algorithms = [
            "Recursive",
            "Iterative",
            "Memoized Recursive",
            "Binary Pattern",
        ]
        num_algorithms = random.choice([2, 3])
        self.params["algorithms"] = random.sample(all_algorithms, num_algorithms)

        algo_list = " vs ".join(self.params["algorithms"])
        self.question_text = f"To generate all {self.params['move_count']} moves for a {n}-disk, 3-peg Hanoi problem, which algorithm will finish *first*: {algo_list}?"
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
        def run_recursive():
            _, time_taken = algorithms.solve_hanoi_recursive(n)
            results["Recursive"] = time_taken

        def run_iterative():
            _, time_taken = algorithms.solve_hanoi_iterative(n)
            results["Iterative"] = time_taken

        def run_memoized():
            _, time_taken = algorithms.solve_hanoi_memoized(n)
            results["Memoized Recursive"] = time_taken

        def run_binary():
            _, time_taken = algorithms.solve_hanoi_binary_pattern(n)
            results["Binary Pattern"] = time_taken

        # Map algorithm names to their runner functions
        algo_runners = {
            "Recursive": run_recursive,
            "Iterative": run_iterative,
            "Memoized Recursive": run_memoized,
            "Binary Pattern": run_binary,
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

        explanation = f"The fastest algorithm for this instance was **{self.correct_answer}**.\n\n"
        explanation += "--- Results ---\n"
        for algo_name in algorithms_to_test:
            algo_time = results.get(algo_name, float("inf"))
            if algo_time == float("inf"):
                explanation += f"{algo_name}: Failed\n"
            else:
                explanation += f"{algo_name}: {algo_time:.6f}s\n"

        explanation += "\n(Note: Iterative and Binary Pattern approaches avoid recursion overhead. Memoization helps with repeated subproblems but Hanoi doesn't have much overlap.)"

        if strings_are_similar(user_answer, self.correct_answer, max_distance=3):
            score = 100
            explanation = "Correct!\n" + explanation
        else:
            score = 0
            explanation = f"Your answer was '{user_answer}'.\n" + explanation

        return (score, self.correct_answer, explanation)
