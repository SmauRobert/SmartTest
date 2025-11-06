import os
import importlib
import pkgutil
import random
import threading
import inspect
from typing import TYPE_CHECKING, Callable
import time

# Import the base class to check against
try:
    from .problems.n_queens.templates import BaseQuestionTemplate
except ImportError:
    from problems.n_queens.templates import BaseQuestionTemplate

if TYPE_CHECKING:
    try:
        from .app_ui import AppUI
    except ImportError:
        from app_ui import AppUI


class QuizController:
    def __init__(self, app_reference: "AppUI"):
        """
        Initializes the controller.

        Args:
            app_reference: A reference to the main UI app instance.
                           This is needed to call `app.after()` for
                           thread-safe UI updates.
        """
        self.app: "AppUI" = app_reference
        self.templates: dict[
            str, list[type[BaseQuestionTemplate]]
        ] = {}  # 'n_queens': [NQ_Template1, NQ_Template2]
        self.problem_names: list[str] = []
        self.current_quiz: list[
            BaseQuestionTemplate
        ] = []  # List of generated question *instances*
        self.current_question_index: int = -1
        random.seed(time.time())

        self.load_templates()

    def load_templates(self):
        """
        Dynamically scans the 'problems' package, imports all 'templates.py'
        files, and discovers all classes that inherit from BaseQuestionTemplate.
        """
        print("Loading question templates...")
        self.templates = {}

        # Path to the 'problems' package
        try:
            from . import problems
        except ImportError:
            import problems

        package_path = os.path.dirname(problems.__file__)

        # Iterate over all sub-packages (n_queens, knights_tour, etc.)
        for _, module_name, is_pkg in pkgutil.iter_modules([package_path]):
            if is_pkg:
                problem_type_name = module_name
                try:
                    # Import the 'templates.py' file from this problem package
                    module_path = f"problems.{problem_type_name}.templates"
                    module = importlib.import_module(module_path)

                    self.templates[problem_type_name] = []

                    # Find all classes in the file that are templates
                    for name, cls in inspect.getmembers(module, inspect.isclass):
                        # Check if it's a *subclass* of BaseQuestionTemplate
                        # and *not* the base class itself
                        if (
                            issubclass(cls, BaseQuestionTemplate)
                            and cls != BaseQuestionTemplate
                        ):
                            self.templates[problem_type_name].append(cls)
                            print(f"  - Found template: {name} in {problem_type_name}")

                except ImportError as e:
                    print(
                        f"Warning: Could not load templates for {problem_type_name}. {e}"
                    )
                except Exception as e:
                    print(f"Error loading {problem_type_name}: {e}")

        self.problem_names = list(self.templates.keys())
        print(f"Loading complete. Found: {self.problem_names}")

    def get_available_problems(self) -> list[str]:
        """Returns the list of problem names that were loaded."""
        return self.problem_names

    def generate_quiz(self, selected_types: list[str], num_questions: int) -> bool:
        """
        Generates a new quiz.

        Args:
            selected_types (list): e.g., ['n_queens', 'graph_coloring']
            num_questions (int): Total questions to generate.

        Returns:
            True if successful, False if no templates were available.
        """
        self.current_quiz = []
        self.current_question_index = -1

        # Gather all possible template *classes* from the selected types
        available_template_classes = []
        for prob_type in selected_types:
            if prob_type in self.templates:
                available_template_classes.extend(self.templates[prob_type])

        if not available_template_classes:
            print("Error: No templates available for selected types.")
            return False

        # Generate the questions
        for _ in range(num_questions):
            # 1. Pick a random template *class*
            TemplateClass = random.choice(available_template_classes)

            # 2. Create an *instance* of it
            question_instance = TemplateClass()

            # 3. Call its generate method
            try:
                question_instance.generate()
                self.current_quiz.append(question_instance)
            except Exception as e:
                print(f"Error generating question {TemplateClass.id}: {e}")

        self.current_question_index = 0
        return len(self.current_quiz) > 0

    def get_next_question(self) -> dict[str, str | int] | None:
        """
        Returns the next question in the quiz.
        """
        if not self.current_quiz or self.current_question_index >= len(
            self.current_quiz
        ):
            return None  # Quiz finished

        question = self.current_quiz[self.current_question_index]
        self.current_question_index += 1

        return {
            "question_number": self.current_question_index,
            "total_questions": len(self.current_quiz),
            "question_text": question.question_text,
            "answer_prompt": question.answer_prompt,
        }

    def get_current_question_instance(self) -> BaseQuestionTemplate | None:
        """Gets the *instance* of the current question for evaluation."""
        if 0 <= (self.current_question_index - 1) < len(self.current_quiz):
            return self.current_quiz[self.current_question_index - 1]
        return None

    def evaluate_answer_async(
        self, user_answer: str, callback: Callable[[tuple[int, str, str]], None]
    ):
        """
        Evaluates the user's answer in a background thread to prevent
        the UI from freezing, especially for "Experimental" questions.

        Args:
            user_answer (str): The user's raw input.
            callback (callable): The UI function to call when evaluation is done.
                                 e.g., self.on_evaluation_complete
        """
        question_to_evaluate = self.get_current_question_instance()

        if not question_to_evaluate:
            # Should not happen if logic is correct
            callback((0, "Error", "Could not find question to evaluate."))
            return

        def evaluation_thread():
            """This function runs in the background."""
            try:
                # This is the (potentially) long-running call
                score, correct_str, explanation = question_to_evaluate.evaluate(
                    user_answer
                )
                result = (score, correct_str, explanation)

            except Exception as e:
                print(f"Error during evaluation: {e}")
                result = (
                    0,
                    "Error",
                    f"An internal error occurred during evaluation: {e}",
                )

            # Now, schedule the `callback` function to be run on the main UI thread
            # This is CRITICAL for thread safety in Tkinter.
            self.app.after(0, callback, result)

        # Start the background thread
        threading.Thread(target=evaluation_thread, daemon=True).start()
