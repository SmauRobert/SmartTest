import random
import threading
import time
from typing import Any

try:
    from . import algorithms
except ImportError:
    import problems.graph_coloring.algorithms as algorithms

try:
    from ...utils.string_matching import strings_are_similar
except ImportError:
    from utils.string_matching import strings_are_similar

try:
    from ..n_queens.templates import BaseQuestionTemplate
except ImportError:
    from problems.n_queens.templates import BaseQuestionTemplate

# --- Template 3.1: Theory (Chromatic Number Definition) ---


class GC_TheoryDefinitionName(BaseQuestionTemplate):
    id = "gc_theory_definition_name"
    problem_type = "graph_coloring"
    question_type = "Theory"

    def generate(self) -> dict[str, str]:
        self.question_text = "Consider a graph G. The 'minimum number of colors needed to color the vertices of G so that no two adjacent vertices share the same color' is known by what name?"
        self.answer_prompt = "Please enter the name (e.g., 'Color Count')."
        self.correct_answer = "Chromatic Number"
        return {
            "question_text": self.question_text,
            "answer_prompt": self.answer_prompt,
        }

    def evaluate(self, user_answer: str) -> tuple[int, str, str]:
        if strings_are_similar(user_answer, self.correct_answer, max_distance=3):
            score = 100
            explanation = "Correct! The answer is the **Chromatic Number**, often written as χ(G). It is a fundamental property of a graph."
        else:
            score = 0
            explanation = f"Your answer was '{user_answer}'. The correct answer is the **Chromatic Number**, often written as χ(G)."
        return (score, self.correct_answer, explanation)


# --- Template 3.2: Computation (Find Chromatic Number) ---


class GC_ComputationFindChi(BaseQuestionTemplate):
    id = "gc_computation_find_chi"
    problem_type = "graph_coloring"
    question_type = "Computation (Async)"

    def generate(self) -> dict[str, str]:
        # Generate a small graph
        graph_type = random.choice(["k3", "c5", "k4"])
        if graph_type == "k3":
            # Complete graph K3 (triangle)
            graph = {0: [1, 2], 1: [0, 2], 2: [0, 1]}
            self.params["type"] = "a K3 (triangle)"
            self.params["chi"] = 3
        elif graph_type == "c5":
            # Cycle C5
            graph = {0: [1, 4], 1: [0, 2], 2: [1, 3], 3: [2, 4], 4: [3, 0]}
            self.params["type"] = "a C5 (5-cycle)"
            self.params["chi"] = 3
        else:
            # Complete graph K4
            graph = {0: [1, 2, 3], 1: [0, 2, 3], 2: [0, 1, 3], 3: [0, 1, 2]}
            self.params["type"] = "a K4 (complete graph on 4 vertices)"
            self.params["chi"] = 4

        self.params["graph"] = graph
        self.question_text = (
            f"What is the chromatic number for the following graph: `{graph}`?"
        )
        self.answer_prompt = "Please enter a single integer."

        return {
            "question_text": self.question_text,
            "answer_prompt": self.answer_prompt,
        }

    def evaluate(self, user_answer: str) -> tuple[int, str, str]:
        user_ans_clean = user_answer.strip().lower()
        correct_answer = self.params["chi"]
        correct_answer_str = str(correct_answer)

        # We can run the optimal solver since N is tiny
        # _, time_taken = algorithms.solve_gc_optimal(self.params['graph'])
        # print(f"Optimal solver took {time_taken}s")

        try:
            user_num = int(user_ans_clean)
            if user_num == correct_answer:
                score = 100
                explanation = f"Correct! The chromatic number is **{correct_answer}**. This graph is {self.params['type']}, which requires {correct_answer} colors."
            else:
                score = 0
                explanation = f"Your answer was '{user_num}'. The correct chromatic number is **{correct_answer}**. This graph is {self.params['type']}, which requires {correct_answer} colors."
        except ValueError:
            score = 0
            explanation = f"Your answer '{user_answer}' is not a valid integer. The correct answer is **{correct_answer}**."

        return (score, correct_answer_str, explanation)


# --- Template 3.3: Validation (Coloring Viability) ---


class GC_ValidationViability(BaseQuestionTemplate):
    id = "gc_validation_viability"
    problem_type = "graph_coloring"
    question_type = "Validation"

    def generate(self) -> dict[str, str]:
        # Graph: 0-1, 1-2, 2-0 (triangle)
        graph = {0: [1, 2], 1: [0, 2], 2: [0, 1]}
        self.params["graph"] = graph

        # 50% chance of valid, 50% invalid
        if random.random() < 0.5:
            # Valid: {0: 0, 1: 1, 2: 2} (Colors 0, 1, 2)
            coloring = {0: 0, 1: 1, 2: 2}
            self.correct_answer = "yes"
            self.params["reason"] = (
                "All adjacent nodes (0-1, 1-2, 2-0) have different colors."
            )
        else:
            # Invalid: {0: 0, 1: 1, 2: 1}
            coloring = {0: 0, 1: 1, 2: 1}
            self.correct_answer = "no"
            self.params["reason"] = (
                "There is a conflict: Node 1 and Node 2 are adjacent but both have color 1."
            )

        self.params["coloring"] = coloring
        self.question_text = f"For the graph `{graph}`, is the following coloring valid: `{coloring}`? (0=Red, 1=Green, 2=Blue)"
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


# --- Template 3.4: Experimental (Algorithm Race) ---


class GC_ExperimentalRace(BaseQuestionTemplate):
    id = "gc_experimental_race"
    problem_type = "graph_coloring"
    question_type = "Experimental (Async)"

    def generate(self) -> dict[str, str]:
        n = random.randint(50, 100)
        m = random.randint(n, n * (n - 1) // 4)  # Moderately dense
        self.params["n"] = n
        self.params["m"] = m

        # We pre-generate the graph here, so evaluation is just running algorithms
        self.params["graph"] = algorithms.generate_random_graph(n, m)

        self.question_text = f"For the graph with {n} nodes and {m} edges, which algorithm will find a valid (not necessarily optimal) coloring *first*: Simple Greedy or Welsh-Powell (Largest-Degree-First)?"
        self.answer_prompt = "Please enter 'Simple Greedy' or 'Welsh-Powell'."

        return {
            "question_text": self.question_text,
            "answer_prompt": self.answer_prompt,
        }

    def evaluate(self, user_answer: str) -> tuple[int, str, str]:
        graph = self.params["graph"]
        results = {}

        def run_greedy():
            _, time_taken = algorithms.solve_gc_greedy(graph)
            results["Simple Greedy"] = time_taken

        def run_welsh_powell():
            _, time_taken = algorithms.solve_gc_welsh_powell(graph)
            results["Welsh-Powell"] = time_taken

        t_greedy = threading.Thread(target=run_greedy)
        t_wp = threading.Thread(target=run_welsh_powell)

        t_greedy.start()
        t_wp.start()

        t_greedy.join()
        t_wp.join()

        greedy_time = results.get("Simple Greedy", float("inf"))
        wp_time = results.get("Welsh-Powell", float("inf"))

        self.correct_answer = (
            "Simple Greedy" if greedy_time < wp_time else "Welsh-Powell"
        )

        explanation = f"The fastest algorithm for this instance was **{self.correct_answer}**.\n\n"
        explanation += "--- Results ---\n"
        explanation += f"Simple Greedy: {greedy_time:.6f}s\n"
        explanation += f"Welsh-Powell: {wp_time:.6f}s\n"
        explanation += "\n(Note: Welsh-Powell must first sort the vertices by degree, which adds O(N log N) overhead. Simple Greedy is O(N+M) or O(N^2) depending on implementation, so for some graph structures, it can be faster.)"

        if strings_are_similar(user_answer, self.correct_answer, max_distance=3):
            score = 100
            explanation = "Correct!\n" + explanation
        else:
            score = 0
            explanation = f"Your answer was '{user_answer}'.\n" + explanation

        return (score, self.correct_answer, explanation)
