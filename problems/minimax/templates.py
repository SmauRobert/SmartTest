import random
import threading
from typing import Any

try:
    from . import algorithms
except ImportError:
    import problems.minimax.algorithms as algorithms

try:
    from ...utils.string_matching import strings_are_similar
except ImportError:
    from utils.string_matching import strings_are_similar

try:
    from ..n_queens.templates import BaseQuestionTemplate
except ImportError:
    from problems.n_queens.templates import BaseQuestionTemplate
    
class MM_Solution(BaseQuestionTemplate):
    id = "minimax_solution"
    problem_type = "minimax"
    question_type = "computation"

    def generate(self) -> dict[str, str]:
        # Generate a random tree
        tree,depth = algorithms.generate_tree()
        self.params['tree'] = tree
        self.params['depth']=depth
        l = algorithms.tree_to_list(tree)
        self.question_text = f"What will be the root value after applying the Minimax algorithm with Alpha-Beta Pruning to the following tree represented as a nested list of leaf values: {l}?"
        self.answer_prompt = "Please enter a single integer. Keep in mind that the first player is the maximizing player."
        return {
            'question_text': self.question_text,
            'answer_prompt': self.answer_prompt
        }
    
    def evaluate(self, user_answer: str) -> tuple[int, str, str]:
        tree = self.params['tree']
        depth = self.params['depth']
        correct_value,_ = algorithms.alpha_beta_pruning(tree, depth, float('-inf'), float('inf'), True, [])

        try:
            user_value = int(user_answer.strip())
        except ValueError:
            return (0, str(correct_value), "Your answer is not a valid integer.")

        if user_value == correct_value:
            return (100, str(correct_value), f"Correct! The Minimax algorithm with Alpha-Beta Pruning yields the root value of {correct_value}.")
        else:
            return (0, str(correct_value), f"Incorrect. The correct root value is {correct_value}.")
        
class MM_NumberOfVisitedLeaves(BaseQuestionTemplate):
    id = "minimax_number_of_visited_leaves"
    problem_type = "minimax"
    question_type = "computation"

    def generate(self) -> dict[str, str]:
        # Generate a random tree
        tree,depth = algorithms.generate_tree()
        self.params['tree'] = tree
        self.params['depth']=depth
        l = algorithms.tree_to_list(tree)
        self.question_text = f"How many leaves are visited when applying the Minimax algorithm with Alpha-Beta Pruning to the following tree represented as a nested list of leaf values: {l}?"
        self.answer_prompt = "Please enter a single integer. Keep in mind that the first player is the maximizing player."
        return {
            'question_text': self.question_text,
            'answer_prompt': self.answer_prompt
        }
    
    def evaluate(self, user_answer: str) -> tuple[int, str, str]:
        tree = self.params['tree']
        depth = self.params['depth']
        _,visited = algorithms.alpha_beta_pruning(tree, depth, float('-inf'), float('inf'), True, [])
        correct_value = len(visited)
        try:
            user_value = int(user_answer.strip())
        except ValueError:
            return (0, str(correct_value), "Your answer is not a valid integer.")

        if user_value == correct_value:
            return (100, str(correct_value), f"Correct! The number of visited leaves is {correct_value}, those being the leaves with the values: {visited}")
        else:
            return (0, str(correct_value), f"Incorrect. The correct number is {correct_value}, those being the leaves with the values: {visited}")
       
