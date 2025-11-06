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
        # Generate a random small graph
        n = random.randint(4, 7)  # 4-7 nodes
        graph_type = random.choice(["complete", "cycle", "bipartite", "random"])

        if graph_type == "complete":
            # Complete graph Kn
            graph = {i: [j for j in range(n) if j != i] for i in range(n)}
            self.params["type"] = f"a K{n} (complete graph)"
            self.params["chi"] = n
        elif graph_type == "cycle":
            # Cycle Cn
            graph = {i: [(i - 1) % n, (i + 1) % n] for i in range(n)}
            self.params["type"] = f"a C{n} ({n}-cycle)"
            self.params["chi"] = 3 if n % 2 == 1 else 2
        elif graph_type == "bipartite":
            # Random bipartite graph
            n1 = random.randint(2, n // 2 + 1)
            n2 = n - n1
            graph = {}
            # Create bipartite structure
            for i in range(n1):
                # Connect to random nodes in second partition
                num_connections = random.randint(1, min(n2, 3))
                connections = random.sample(range(n1, n), num_connections)
                graph[i] = connections
            for i in range(n1, n):
                # Connect back to first partition
                connections = [j for j in range(n1) if i in graph.get(j, [])]
                graph[i] = connections
            self.params["type"] = f"a bipartite graph"
            self.params["chi"] = 2
        else:
            # Random graph with moderate edge density
            graph = {i: [] for i in range(n)}
            num_edges = random.randint(n, n * (n - 1) // 4)
            edges_added = 0
            attempts = 0
            while edges_added < num_edges and attempts < num_edges * 3:
                u, v = random.sample(range(n), 2)
                if v not in graph[u]:
                    graph[u].append(v)
                    graph[v].append(u)
                    edges_added += 1
                attempts += 1
            self.params["type"] = f"a random graph"
            # Calculate chromatic number using greedy algorithm as approximation
            coloring, _ = algorithms.solve_gc_greedy(graph)
            if coloring:
                self.params["chi"] = len(set(coloring.values()))
            else:
                self.params["chi"] = 1

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
        # Generate a random small graph
        n = random.randint(4, 6)
        graph = {i: [] for i in range(n)}

        # Generate random edges
        num_edges = random.randint(n, n * (n - 1) // 3)
        for _ in range(num_edges):
            u, v = random.sample(range(n), 2)
            if v not in graph[u]:
                graph[u].append(v)
                graph[v].append(u)

        self.params["graph"] = graph

        # Generate a coloring (50% chance valid, 50% invalid)
        if random.random() < 0.5:
            # Generate valid coloring using greedy algorithm
            coloring, _ = algorithms.solve_gc_greedy(graph)
            if not coloring:
                coloring = {i: 0 for i in range(n)}
            self.correct_answer = "yes"

            # Verify it's actually valid
            conflicts = []
            for node in graph:
                for neighbor in graph[node]:
                    if coloring[node] == coloring[neighbor]:
                        conflicts.append((node, neighbor))

            if conflicts:
                self.params["reason"] = f"All adjacent nodes have different colors."
            else:
                self.params["reason"] = f"All adjacent nodes have different colors."
        else:
            # Generate invalid coloring
            coloring = {i: random.randint(0, 2) for i in range(n)}
            self.correct_answer = "no"

            # Find a conflict
            conflict_found = False
            for node in graph:
                for neighbor in graph[node]:
                    if neighbor > node and coloring[node] == coloring[neighbor]:
                        self.params["reason"] = (
                            f"There is a conflict: Node {node} and Node {neighbor} are adjacent but both have color {coloring[node]}."
                        )
                        conflict_found = True
                        break
                if conflict_found:
                    break

            if not conflict_found:
                # Force a conflict
                if len(graph[0]) > 0:
                    neighbor = graph[0][0]
                    coloring[neighbor] = coloring[0]
                    self.params["reason"] = (
                        f"There is a conflict: Node 0 and Node {neighbor} are adjacent but both have color {coloring[0]}."
                    )
                else:
                    self.params["reason"] = (
                        "There is a conflict between adjacent nodes."
                    )

        self.params["coloring"] = coloring
        color_names = ["Red", "Green", "Blue", "Yellow", "Orange", "Purple"]
        color_legend = ", ".join(
            [f"{i}={color_names[i]}" for i in range(min(4, max(coloring.values()) + 1))]
        )
        self.question_text = f"For the graph `{graph}`, is the following coloring valid: `{coloring}`? ({color_legend})"
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
        # Use smaller graphs so we can show edge list to user
        n = random.randint(8, 15)
        # Moderate edge density
        max_edges = n * (n - 1) // 2
        m = random.randint(n, min(max_edges, n * 2))
        self.params["n"] = n
        self.params["m"] = m

        # We pre-generate the graph here, so evaluation is just running algorithms
        self.params["graph"] = algorithms.generate_random_graph(n, m)

        # Create edge list for display
        edges = []
        graph = self.params["graph"]
        for u in graph:
            for v in graph[u]:
                if u < v:  # Only add each edge once
                    edges.append((u, v))
        edges.sort()

        edge_str = ", ".join([f"{u}-{v}" for u, v in edges[:20]])
        if len(edges) > 20:
            edge_str += f", ... ({len(edges) - 20} more edges)"

        self.question_text = f"For a graph with {n} nodes and edges: [{edge_str}], which algorithm will find a valid coloring *first*: Simple Greedy or Welsh-Powell (Largest-Degree-First)?"
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
