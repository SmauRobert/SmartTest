import customtkinter as ctk
from typing import Any, TYPE_CHECKING


class AppUI(ctk.CTk):
    def __init__(self, controller: Any):
        super().__init__()

        self.controller: Any = controller

        # --- App Setup ---
        self.title("AI Problem Solver Quiz")
        self.geometry("800x600")
        ctk.set_appearance_mode("System")  # Dark/Light
        ctk.set_default_color_theme("blue")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # --- Frames ---
        self.setup_frame: Any = None
        self.quiz_frame: Any = None

        # --- Quiz State ---
        self.problem_checkboxes: dict[str, Any] = {}  # str -> ctk.Variable
        self.total_questions: Any = ctk.StringVar(value="5")
        self.current_score: int = 0
        self.questions_answered: int = 0

        # Don't call show_setup_frame here - it will be called from main()

    def clear_frame(self):
        """Destroys all widgets in the main frame."""
        for widget in self.winfo_children():
            widget.destroy()

    # ==================================================================
    # FRAME 1: SETUP SCREEN
    # ==================================================================

    def show_setup_frame(self):
        self.clear_frame()
        self.setup_frame = ctk.CTkFrame(self)
        self.setup_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)

        # Center the content
        self.setup_frame.grid_columnconfigure(0, weight=1)
        self.setup_frame.grid_columnconfigure(2, weight=1)

        title = ctk.CTkLabel(
            self.setup_frame,
            text="AI Problem Solver Quiz",
            font=ctk.CTkFont(size=24, weight="bold"),
        )
        title.grid(row=0, column=1, pady=(10, 20))

        # --- Problem Type Checkboxes ---
        problem_frame = ctk.CTkFrame(self.setup_frame, fg_color="transparent")
        problem_frame.grid(row=1, column=1, pady=10)

        problem_label = ctk.CTkLabel(problem_frame, text="Select Problem Types:")
        problem_label.pack(anchor="w")

        self.problem_checkboxes = {}
        available_problems = (
            self.controller.get_available_problems() if self.controller else []
        )

        for problem_name in available_problems:
            var = ctk.StringVar(value=problem_name)  # Pre-select all
            cb = ctk.CTkCheckBox(
                problem_frame,
                text=problem_name.replace("_", " ").title(),
                variable=var,
                onvalue=problem_name,
                offvalue="",
            )
            cb.pack(anchor="w", padx=10, pady=2)
            self.problem_checkboxes[problem_name] = var

        # --- Number of Questions ---
        num_q_frame = ctk.CTkFrame(self.setup_frame, fg_color="transparent")
        num_q_frame.grid(row=2, column=1, pady=10)

        num_q_label = ctk.CTkLabel(num_q_frame, text="Number of Questions:")
        num_q_label.pack(side="left", padx=5)

        num_q_entry = ctk.CTkEntry(
            num_q_frame, textvariable=self.total_questions, width=50
        )
        num_q_entry.pack(side="left")

        # --- Start Button ---
        start_button = ctk.CTkButton(
            self.setup_frame,
            text="Start Quiz",
            command=self.start_quiz,
            font=ctk.CTkFont(size=16),
        )
        start_button.grid(row=3, column=1, pady=20, ipady=10)

    def start_quiz(self):
        # 1. Get selected problem types
        selected_types = [
            var.get() for var in self.problem_checkboxes.values() if var.get()
        ]

        # 2. Get number of questions
        try:
            num_q = int(self.total_questions.get())
            if num_q <= 0:
                raise ValueError
        except ValueError:
            # Show an error (ideally a modal, but a label is fine)
            print("Invalid number of questions")
            return

        # 3. Tell controller to generate quiz
        if not self.controller or not self.controller.generate_quiz(
            selected_types, num_q
        ):
            # Handle error (e.g., no templates found)
            print("Error: Could not generate quiz.")
            return

        # 4. Reset score and go to quiz frame
        self.current_score = 0
        self.questions_answered = 0
        self.show_quiz_frame()
        self.load_next_question()

    # ==================================================================
    # FRAME 2: QUIZ SCREEN
    # ==================================================================

    def show_quiz_frame(self):
        self.clear_frame()
        self.quiz_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.quiz_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)

        self.quiz_frame.grid_rowconfigure(2, weight=1)  # Question text
        self.quiz_frame.grid_rowconfigure(5, weight=2)  # Result
        self.quiz_frame.grid_columnconfigure(0, weight=1)

        # --- Score / Progress ---
        self.progress_label = ctk.CTkLabel(
            self.quiz_frame, text="Question 1 / 10", font=ctk.CTkFont(size=16)
        )
        self.progress_label.grid(row=0, column=0, pady=5, sticky="w")

        self.score_label = ctk.CTkLabel(
            self.quiz_frame, text="Score: 0%", font=ctk.CTkFont(size=16)
        )
        self.score_label.grid(row=0, column=0, pady=5, sticky="e")

        # --- Question Text ---
        self.question_text_label = ctk.CTkLabel(
            self.quiz_frame,
            text="Loading question...",
            font=ctk.CTkFont(size=18, weight="bold"),
            wraplength=750,
            justify="left",
        )
        self.question_text_label.grid(row=1, column=0, pady=(10, 5), sticky="w")

        self.question_prompt_label = ctk.CTkLabel(
            self.quiz_frame,
            text="...",
            font=ctk.CTkFont(size=14, slant="italic"),
            wraplength=750,
            justify="left",
        )
        self.question_prompt_label.grid(row=2, column=0, pady=(0, 10), sticky="nw")

        # --- Answer Entry ---
        self.answer_entry = ctk.CTkEntry(
            self.quiz_frame, font=ctk.CTkFont(size=14), height=40
        )
        self.answer_entry.grid(row=3, column=0, pady=10, sticky="ew")
        self.answer_entry.bind("<Return>", self.submit_answer)

        # --- Button Frame ---
        self.button_frame = ctk.CTkFrame(self.quiz_frame, fg_color="transparent")
        self.button_frame.grid(row=4, column=0, sticky="ew")

        self.submit_button = ctk.CTkButton(
            self.button_frame,
            text="Submit Answer",
            command=self.submit_answer,
            font=ctk.CTkFont(size=14),
        )
        self.submit_button.pack(side="left", padx=5)

        self.next_button = ctk.CTkButton(
            self.button_frame,
            text="Next Question",
            command=self.load_next_question,
            state="disabled",
            font=ctk.CTkFont(size=14),
        )
        self.next_button.pack(side="left", padx=5)

        # --- Result Frame ---
        self.result_frame = ctk.CTkFrame(self.quiz_frame, fg_color="transparent")
        self.result_frame.grid(row=5, column=0, pady=10, sticky="nsew")
        self.result_frame.grid_rowconfigure(1, weight=1)
        self.result_frame.grid_columnconfigure(0, weight=1)

        self.result_title_label = ctk.CTkLabel(
            self.result_frame, text="", font=ctk.CTkFont(size=16, weight="bold")
        )
        self.result_title_label.grid(row=0, column=0, pady=5, sticky="w")

        self.result_explanation_text = ctk.CTkTextbox(
            self.result_frame,
            wrap="word",
            font=ctk.CTkFont(size=14),
            state="disabled",
            fg_color="transparent",
        )
        self.result_explanation_text.grid(row=1, column=0, sticky="nsew")

    def load_next_question(self):
        if not self.controller:
            return
        question_data = self.controller.get_next_question()

        if question_data is None:
            # Quiz is over
            self.show_final_score()
            return

        # 1. Reset UI state
        self.question_text_label.configure(text=question_data["question_text"])
        self.question_prompt_label.configure(text=question_data["answer_prompt"])
        self.progress_label.configure(
            text=f"Question {question_data['question_number']} / {question_data['total_questions']}"
        )

        self.answer_entry.delete(0, "end")
        self.answer_entry.configure(state="normal")
        self.answer_entry.focus()

        self.submit_button.configure(state="normal", text="Submit Answer")
        self.next_button.configure(state="disabled")

        self.result_title_label.configure(text="")
        self.result_explanation_text.configure(state="normal")
        self.result_explanation_text.delete("1.0", "end")
        self.result_explanation_text.configure(state="disabled")

    def submit_answer(self, event: Any = None):
        if not self.controller:
            return
        user_answer = self.answer_entry.get()
        if not user_answer or self.submit_button.cget("state") == "disabled":
            return

        # 1. Disable UI
        self.submit_button.configure(state="disabled", text="Evaluating...")
        self.answer_entry.configure(state="disabled")

        # 2. Call controller async
        self.controller.evaluate_answer_async(user_answer, self.on_evaluation_complete)

    def on_evaluation_complete(self, result: tuple[int, str, str]):
        """
        This is the callback function that runs on the main thread
        when the controller is finished.
        """
        score, correct_answer_str, explanation = result

        # 1. Update score
        self.questions_answered += 1
        if score == 100:
            self.current_score += 1

        avg_score = (self.current_score / self.questions_answered) * 100
        self.score_label.configure(text=f"Score: {avg_score:.0f}%")

        # 2. Display result
        if score == 100:
            self.result_title_label.configure(
                text="Correct!", text_color="#00A000"
            )  # Green
        else:
            self.result_title_label.configure(
                text=f"Incorrect. The correct answer was: {correct_answer_str}",
                text_color="#C00000",
            )  # Red

        self.result_explanation_text.configure(state="normal")
        self.result_explanation_text.delete("1.0", "end")
        self.result_explanation_text.insert("1.0", explanation)
        self.result_explanation_text.configure(state="disabled")

        # 3. Re-enable UI
        self.submit_button.configure(state="disabled", text="Submitted")
        self.next_button.configure(state="normal")
        self.next_button.focus()

    def show_final_score(self):
        self.clear_frame()
        final_frame = ctk.CTkFrame(self)
        final_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)

        final_frame.grid_rowconfigure(0, weight=1)
        final_frame.grid_rowconfigure(3, weight=1)
        final_frame.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            final_frame, text="Quiz Complete!", font=ctk.CTkFont(size=24, weight="bold")
        )
        title.grid(row=1, column=0, pady=10)

        total_q = len(self.controller.current_quiz) if self.controller else 1
        final_score_pct = (self.current_score / total_q) * 100

        score_text = (
            f"You scored {self.current_score} out of {total_q} ({final_score_pct:.0f}%)"
        )
        score_label = ctk.CTkLabel(
            final_frame, text=score_text, font=ctk.CTkFont(size=18)
        )
        score_label.grid(row=2, column=0, pady=10)

        back_button = ctk.CTkButton(
            final_frame,
            text="Back to Main Menu",
            command=self.show_setup_frame,
            font=ctk.CTkFont(size=16),
        )
        back_button.grid(row=4, column=0, pady=20, ipady=10)
