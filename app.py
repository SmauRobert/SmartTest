import tkinter as tk
from tkinter import ttk, messagebox, font
from tkinter.scrolledtext import ScrolledText
from typing import Dict, List, Optional, Final, TypeVar
from dataclasses import dataclass
import random

from questions_bank import (
    Question,
    QuestionType,
    generate_question,
    QUESTION_TEMPLATES,
)
from evaluators import evaluate_answer


@dataclass
class TestState:
    """Represents the current state of the test"""

    questions: List[Question]
    current_idx: int = 0
    answers: Dict[int, str] = None

    def __post_init__(self):
        if self.answers is None:
            self.answers = {}

    @property
    def current_question(self) -> Optional[Question]:
        """Get the current question or None if test is finished"""
        if 0 <= self.current_idx < len(self.questions):
            return self.questions[self.current_idx]
        return None

    @property
    def is_last_question(self) -> bool:
        """Check if current question is the last one"""
        return self.current_idx == len(self.questions) - 1

    def save_answer(self, answer: str) -> None:
        """Save answer for current question"""
        self.answers[self.current_idx] = answer


class SmartTestApp(tk.Tk):
    """Main application window"""

    def __init__(self):
        super().__init__()

        self.title("N-Queens Test Generator")
        self.geometry("1000x800")
        self.configure(bg="#f0f0f0")

        # Initialize test state
        self.test_state: Optional[TestState] = None

        # Configure main container
        container = ttk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # Create frames dictionary
        self.frames: Dict[str, tk.Frame] = {}

        # Initialize all frames
        for F in (StartFrame, TestFrame, ResultsFrame):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # Show start frame
        self.show_frame("StartFrame")

    def show_frame(self, page_name: str) -> None:
        """Show the specified frame"""
        frame = self.frames[page_name]
        if page_name == "TestFrame" and self.test_state:
            frame.load_current_question()
        elif page_name == "ResultsFrame" and self.test_state:
            frame.show_results()
        frame.tkraise()

    def start_test(self, num_questions: int) -> None:
        """Initialize a new test with the specified number of questions"""
        # Generate random questions
        questions = []
        question_types = list(QUESTION_TEMPLATES.keys())

        for _ in range(num_questions):
            q_type = random.choice(question_types)
            questions.append(generate_question(q_type))

        # Initialize test state
        self.test_state = TestState(questions=questions)
        self.show_frame("TestFrame")

    def next_question(self, current_answer: str) -> None:
        """Process current answer and move to next question"""
        if not self.test_state:
            raise RuntimeError("Test state not initialized")

        # Save current answer
        self.test_state.save_answer(current_answer)

        # Move to next question or results
        self.test_state.current_idx += 1
        if self.test_state.current_question:
            self.show_frame("TestFrame")
        else:
            self.show_frame("ResultsFrame")


class StartFrame(ttk.Frame):
    """Initial frame for test configuration"""

    def __init__(self, parent: tk.Widget, controller: SmartTestApp):
        super().__init__(parent)
        self.controller = controller

        # Title
        title_font = font.Font(family="Helvetica", size=24, weight="bold")
        ttk.Label(
            self,
            text="N-Queens Test Generator",
            font=title_font,
        ).pack(pady=40, padx=20)

        # Instructions
        ttk.Label(
            self,
            text="Select number of questions to generate:",
            font=("Helvetica", 14),
        ).pack(pady=10, padx=20)

        # Question count selector
        self.num_questions = tk.StringVar(value="3")
        max_questions = len(QUESTION_TEMPLATES)
        values = [str(i) for i in range(1, max_questions + 1)]

        self.question_count = ttk.Combobox(
            self,
            textvariable=self.num_questions,
            values=values,
            font=("Helvetica", 12),
            width=10,
            state="readonly",
        )
        self.question_count.pack(pady=10)

        # Description
        desc_text = "\n".join(
            [
                "Questions will be randomly selected from:",
                "- N-Queens solution finding",
                "- Position validity checking",
                "- Next move analysis",
                "\nEach question will use randomly generated parameters",
                "for different board sizes (N=4 to N=8)",
            ]
        )

        ttk.Label(
            self,
            text=desc_text,
            font=("Helvetica", 12),
            justify="left",
        ).pack(pady=20)

        # Start button
        ttk.Button(
            self,
            text="Generate Test",
            command=self.start_test,
            style="Start.TButton",
        ).pack(pady=20)

        # Configure button style
        style = ttk.Style()
        style.configure("Start.TButton", font=("Helvetica", 12, "bold"), padding=10)

    def start_test(self) -> None:
        """Start the test with selected number of questions"""
        try:
            num_questions = int(self.num_questions.get())
            self.controller.start_test(num_questions)
        except ValueError:
            messagebox.showerror("Error", "Invalid number of questions selected")


class TestFrame(ttk.Frame):
    """Frame for displaying and answering questions"""

    def __init__(self, parent: tk.Widget, controller: SmartTestApp):
        super().__init__(parent)
        self.controller = controller

        # Question counter
        self.counter_label = ttk.Label(
            self, text="Question 0/0", font=("Helvetica", 14)
        )
        self.counter_label.pack(pady=10, padx=40)

        # Question text
        self.question_label = ttk.Label(
            self,
            text="Loading question...",
            font=("Helvetica", 12),
            wraplength=900,
            justify="left",
        )
        self.question_label.pack(pady=10, padx=40)

        # Format hint
        self.format_label = ttk.Label(
            self,
            text="",
            font=("Helvetica", 11, "italic"),
            wraplength=900,
            justify="left",
        )
        self.format_label.pack(pady=5, padx=40)

        # Answer text area
        self.answer_text = ScrolledText(
            self,
            height=15,
            font=("Helvetica", 11),
            wrap=tk.WORD,
        )
        self.answer_text.pack(pady=10, padx=40, fill=tk.BOTH, expand=True)

        # Submit button
        self.submit_button = ttk.Button(
            self,
            text="Submit Answer",
            command=self.submit_answer,
        )
        self.submit_button.pack(pady=20)

    def load_current_question(self) -> None:
        """Load and display the current question"""
        if not self.controller.test_state:
            return

        state = self.controller.test_state
        question = state.current_question

        if not question:
            return

        # Update question counter
        total = len(state.questions)
        self.counter_label.config(text=f"Question {state.current_idx + 1}/{total}")

        # Update question text
        self.question_label.config(text=question.prompt)
        self.format_label.config(text=f"Answer format: {question.answer_format}")

        # Clear answer box
        self.answer_text.delete("1.0", tk.END)

        # Update submit button
        self.submit_button.config(
            text="Finish Test" if state.is_last_question else "Next Question"
        )

    def submit_answer(self) -> None:
        """Submit current answer and move to next question"""
        answer = self.answer_text.get("1.0", tk.END).strip()
        if not answer:
            messagebox.showwarning(
                "Warning", "Please provide an answer before continuing"
            )
            return

        self.controller.next_question(answer)


class ResultsFrame(ttk.Frame):
    """Frame for displaying test results"""

    def __init__(self, parent: tk.Widget, controller: SmartTestApp):
        super().__init__(parent)
        self.controller = controller

        # Title
        ttk.Label(self, text="Test Results", font=("Helvetica", 20, "bold")).pack(
            pady=20
        )

        # Create scrollable results area
        self.canvas = tk.Canvas(self, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)

        self.scrollable_frame = ttk.Frame(self.canvas)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )

        self.canvas.create_window(
            (0, 0),
            window=self.scrollable_frame,
            anchor="nw",
            width=980,  # Leave space for scrollbar
        )
        self.canvas.configure(yscrollcommand=scrollbar.set)

        # Pack scrollable area
        self.canvas.pack(side="left", fill="both", expand=True, padx=10)
        scrollbar.pack(side="right", fill="y")

        # Restart button
        ttk.Button(
            self,
            text="Start New Test",
            command=lambda: controller.show_frame("StartFrame"),
        ).pack(pady=20)

        # Configure mouse wheel scrolling
        self.bind_mouse_wheel()

    def bind_mouse_wheel(self) -> None:
        """Bind mouse wheel to scroll results"""

        def _on_mouse_wheel(event):
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        self.canvas.bind_all("<MouseWheel>", _on_mouse_wheel)

    def show_results(self) -> None:
        """Display test results"""
        # Clear previous results
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        if not self.controller.test_state:
            return

        state = self.controller.test_state
        total_score = 0

        # Show results for each question
        for idx, question in enumerate(state.questions):
            answer = state.answers.get(idx, "No answer provided")

            # Create frame for this question
            question_frame = ttk.Frame(self.scrollable_frame)
            question_frame.pack(fill="x", pady=10, padx=10)

            # Question header
            ttk.Label(
                question_frame,
                text=f"Question {idx + 1}: {question.name}",
                font=("Helvetica", 12, "bold"),
            ).pack(fill="x")

            # Evaluate answer
            try:
                score, feedback = evaluate_answer(question, answer)
                total_score += score

                # Show score
                ttk.Label(
                    question_frame, text=f"Score: {score}%", font=("Helvetica", 11)
                ).pack(fill="x")

                # Show feedback
                feedback_text = ScrolledText(
                    question_frame, height=6, font=("Helvetica", 10), wrap=tk.WORD
                )
                feedback_text.insert("1.0", feedback)
                feedback_text.config(state="disabled")
                feedback_text.pack(fill="x")

            except Exception as e:
                ttk.Label(
                    question_frame,
                    text=f"Error evaluating answer: {str(e)}",
                    font=("Helvetica", 10),
                    foreground="red",
                ).pack(fill="x")

        # Show final score
        if state.questions:
            avg_score = total_score / len(state.questions)
            ttk.Label(
                self.scrollable_frame,
                text=f"\nFinal Score: {avg_score:.1f}%",
                font=("Helvetica", 14, "bold"),
            ).pack(pady=20)


if __name__ == "__main__":
    app = SmartTestApp()
    app.mainloop()
