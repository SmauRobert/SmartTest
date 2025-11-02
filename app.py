from __future__ import annotations
import tkinter as tk
from tkinter import ttk, messagebox, font
from tkinter.scrolledtext import ScrolledText
from typing import Dict, List, Set, Optional
import ttkthemes
import random

from questions_bank import (
    Topic,
    QuestionType,
    Question,
    QUESTION_TEMPLATES,
    generate_question,
)
from evaluators import evaluate_answer


class SmartTestApp(ttkthemes.ThemedTk):
    """Main application window with custom theme"""

    style: ttk.Style
    selected_topics: set[Topic]
    current_test: TestState | None
    frames: dict[str, ttk.Frame]

    def __init__(self):
        super().__init__(theme="arc")  # Modern, clean theme

        self.title("Algorithm Problem Solver")
        self.geometry("1200x800")
        # Initialize style before configuring
        self.style = ttk.Style(self)
        self.configure(bg=self.get_bg_color())

        # Initialize test state
        self.selected_topics = set()
        self.current_test = None

        # Configure custom styles
        self.configure_styles()

        # Create main container
        container = ttk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # Initialize frames
        self.frames = {}
        for Frame in (StartFrame, TopicSelectFrame, TestFrame, ResultsFrame):
            page_name = Frame.__name__
            frame = Frame(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("StartFrame")

    def configure_styles(self):
        """Configure custom styles for widgets"""
        # Main button style
        self.style.configure(
            "Action.TButton",
            font=("Helvetica", 12, "bold"),
            padding=10,
        )

        # Navigation button style
        self.style.configure(
            "Nav.TButton",
            font=("Helvetica", 10),
            padding=5,
        )

        # Header style
        self.style.configure(
            "Header.TLabel",
            font=("Helvetica", 24, "bold"),
            padding=20,
        )

        # Subheader style
        self.style.configure(
            "Subheader.TLabel",
            font=("Helvetica", 14),
            padding=10,
        )

    def get_bg_color(self) -> str:
        """Get background color based on theme"""
        try:
            return self.style.lookup("TFrame", "background", default="#ffffff")
        except:
            return "#ffffff"

    def show_frame(self, page_name: str) -> None:
        """Show the specified frame"""
        frame = self.frames[page_name]
        frame.on_show() if hasattr(frame, "on_show") else None
        frame.tkraise()

    def start_topic_selection(self) -> None:
        """Show topic selection screen"""
        self.selected_topics.clear()
        self.show_frame("TopicSelectFrame")

    def start_test(self, num_questions: int) -> None:
        """Start a new test with selected topics"""
        if not self.selected_topics:
            messagebox.showerror("Error", "Please select at least one topic")
            return

        questions = []
        questions_per_topic = max(1, num_questions // len(self.selected_topics))
        remaining = num_questions % len(self.selected_topics)

        for topic in self.selected_topics:
            # Generate questions for this topic
            for _ in range(questions_per_topic + (1 if remaining > 0 else 0)):
                questions.append(generate_question(topic))
            if remaining > 0:
                remaining -= 1

        # Shuffle questions
        random.shuffle(questions)

        # Initialize test state
        self.current_test = TestState(questions=questions)
        self.show_frame("TestFrame")


class TestState:
    """Manages the state of the current test"""

    questions: list[Question]
    current_idx: int
    answers: dict[int, dict[str, float | str]]

    def __init__(self, questions: list[Question]):
        self.questions = questions
        self.current_idx = 0
        self.answers = {}

    @property
    def current_question(self) -> Question | None:
        """Get current question or None if test is finished"""
        if 0 <= self.current_idx < len(self.questions):
            return self.questions[self.current_idx]
        return None

    @property
    def is_last_question(self) -> bool:
        """Check if current question is the last one"""
        return self.current_idx == len(self.questions) - 1

    def save_answer(self, answer: str) -> None:
        """Save answer for current question"""
        question = self.current_question
        if question:
            score, feedback = evaluate_answer(question, answer)
            optimal = (
                question.solution
                if hasattr(question, "solution") and question.solution
                else None
            )
            self.answers[self.current_idx] = {
                "answer": answer,
                "score": score,
                "feedback": feedback,
                "correct_answer": optimal,
                "optimal_solution": optimal,
                "question": question,
            }


class StartFrame(ttk.Frame):
    """Welcome screen with start button"""

    def __init__(self, parent: tk.Widget, controller: SmartTestApp):
        super().__init__(parent)
        self.controller = controller
        self.setup_ui()

    def setup_ui(self) -> None:
        """Setup UI elements"""
        # Center content
        content = ttk.Frame(self)
        content.place(relx=0.5, rely=0.5, anchor="center")

        # Title
        ttk.Label(
            content,
            text="Algorithm Problem Solver",
            style="Header.TLabel",
        ).pack(pady=20)

        # Description
        description = (
            "Practice solving algorithmic problems:\n"
            "• N-Queens Problem\n"
            "• Generalized Tower of Hanoi\n"
            "• Graph Coloring\n"
            "• Knight's Tour\n\n"
            "Select topics and test your knowledge!"
        )
        ttk.Label(
            content,
            text=description,
            style="Subheader.TLabel",
            justify="left",
        ).pack(pady=20)

        # Start button
        ttk.Button(
            content,
            text="Start Practice",
            style="Action.TButton",
            command=self.controller.start_topic_selection,
        ).pack(pady=30)


class TopicSelectFrame(ttk.Frame):
    """Topic selection screen"""

    def __init__(self, parent: tk.Widget, controller: SmartTestApp):
        super().__init__(parent)
        self.controller = controller
        self.topic_vars: Dict[Topic, tk.BooleanVar] = {}
        self.setup_ui()

    def setup_ui(self) -> None:
        """Setup UI elements"""
        # Header
        ttk.Label(
            self,
            text="Select Topics to Practice",
            style="Header.TLabel",
        ).pack(pady=20)

        # Topics frame
        topics_frame = ttk.LabelFrame(self, text="Available Topics", padding=20)
        topics_frame.pack(pady=20, padx=40, fill="x")

        # Create checkboxes for each topic
        for topic in Topic:
            var = tk.BooleanVar()
            self.topic_vars[topic] = var
            ttk.Checkbutton(
                topics_frame,
                text=Topic.get_display_name(topic),
                variable=var,
                command=self.update_topic_selection,
            ).pack(pady=5, anchor="w")

        # Number of questions selector
        questions_frame = ttk.LabelFrame(self, text="Number of Questions", padding=20)
        questions_frame.pack(pady=20, padx=40, fill="x")

        self.num_questions = tk.StringVar(value="5")
        values = [str(i) for i in range(1, 21)]  # 1 to 20 questions
        ttk.Combobox(
            questions_frame,
            textvariable=self.num_questions,
            values=values,
            state="readonly",
            width=10,
        ).pack(pady=10)

        # Buttons
        buttons_frame = ttk.Frame(self)
        buttons_frame.pack(pady=20)

        ttk.Button(
            buttons_frame,
            text="← Back",
            style="Nav.TButton",
            command=lambda: self.controller.show_frame("StartFrame"),
        ).pack(side="left", padx=10)

        ttk.Button(
            buttons_frame,
            text="Start Test",
            style="Action.TButton",
            command=self.start_test,
        ).pack(side="left", padx=10)

    def update_topic_selection(self) -> None:
        """Update selected topics based on checkboxes"""
        self.controller.selected_topics = {
            topic for topic, var in self.topic_vars.items() if var.get()
        }

    def start_test(self) -> None:
        """Start test with selected options"""
        try:
            num_questions = int(self.num_questions.get())
            self.controller.start_test(num_questions)
        except ValueError:
            messagebox.showerror("Error", "Invalid number of questions")


class TestFrame(ttk.Frame):
    """Question display and answer frame"""

    controller: SmartTestApp
    counter_label: ttk.Label
    topic_label: ttk.Label
    question_label: ttk.Label
    format_label: ttk.Label
    answer_text: ScrolledText
    submit_button: ttk.Button

    def __init__(self, parent: tk.Widget, controller: SmartTestApp):
        super().__init__(parent)
        self.controller = controller
        self.setup_ui()

    def setup_ui(self) -> None:
        """Setup UI elements"""
        # Question counter
        self.counter_label = ttk.Label(
            self,
            text="Question 0/0",
            style="Subheader.TLabel",
        )
        self.counter_label.pack(pady=10)

        # Topic and type labels
        self.topic_label = ttk.Label(
            self,
            text="Topic: None",
            style="Subheader.TLabel",
        )
        self.topic_label.pack(pady=5)

        # Question text
        question_frame = ttk.LabelFrame(self, text="Question", padding=20)
        question_frame.pack(pady=10, padx=40, fill="x")

        self.question_label = ttk.Label(
            question_frame,
            text="Loading...",
            wraplength=1000,
            justify="left",
        )
        self.question_label.pack(fill="x")

        # Answer format hint
        format_frame = ttk.LabelFrame(self, text="Answer Format", padding=10)
        format_frame.pack(pady=10, padx=40, fill="x")

        self.format_label = ttk.Label(
            format_frame,
            text="",
            wraplength=1000,
            justify="left",
        )
        self.format_label.pack(fill="x")

        # Answer input
        answer_frame = ttk.LabelFrame(self, text="Your Answer", padding=20)
        answer_frame.pack(pady=10, padx=40, fill="both", expand=True)

        self.answer_text = ScrolledText(
            answer_frame,
            height=10,
            width=80,
            font=("Courier", 12),
            wrap=tk.WORD,
        )
        self.answer_text.pack(fill="both", expand=True)

        # Submit button
        self.submit_button = ttk.Button(
            self,
            text="Submit Answer",
            style="Action.TButton",
            command=self.submit_answer,
        )
        self.submit_button.pack(pady=20)

    def on_show(self) -> None:
        """Update display when frame is shown"""
        self.load_current_question()

    def load_current_question(self) -> None:
        """Load and display current question"""
        if not self.controller.current_test:
            return

        state: TestState = self.controller.current_test
        question: Question | None = state.current_question
        if not question:
            return

        # Update question counter
        total = len(state.questions)
        self.counter_label.config(text=f"Question {state.current_idx + 1}/{total}")

        # Update topic and question
        self.topic_label.config(text=f"Topic: {Topic.get_display_name(question.topic)}")
        self.question_label.config(text=question.prompt)
        self.format_label.config(text=question.answer_format)

        # Clear answer box
        self.answer_text.delete("1.0", tk.END)

        # Update submit button
        self.submit_button.config(
            text="Finish Test" if state.is_last_question else "Next Question"
        )

    def submit_answer(self) -> None:
        """Submit current answer and move to next question"""
        answer: str = self.answer_text.get("1.0", tk.END).strip()
        if not answer:
            messagebox.showwarning(
                "Warning", "Please provide an answer before continuing"
            )
            return

        state = self.controller.current_test
        if state:
            state.save_answer(answer)
            state.current_idx += 1

            if state.current_question:
                self.load_current_question()
            else:
                self.controller.show_frame("ResultsFrame")


class ResultsFrame(ttk.Frame):
    """Test results display frame"""

    controller: SmartTestApp
    canvas: tk.Canvas
    results_frame: ttk.Frame

    def __init__(self, parent: tk.Widget, controller: SmartTestApp):
        super().__init__(parent)
        self.controller = controller
        self.setup_ui()

    def setup_ui(self) -> None:
        """Setup UI elements"""
        # Header
        ttk.Label(
            self,
            text="Test Results",
            style="Header.TLabel",
        ).pack(pady=20)

        # Create scrollable results area
        self.canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)

        self.results_frame = ttk.Frame(self.canvas)
        self.results_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )

        self.canvas.create_window(
            (0, 0), window=self.results_frame, anchor="nw", width=1100
        )
        self.canvas.configure(yscrollcommand=scrollbar.set)

        # Pack scrollable area
        self.canvas.pack(side="left", fill="both", expand=True, padx=10)
        scrollbar.pack(side="right", fill="y")

        # New test button
        ttk.Button(
            self,
            text="Start New Test",
            style="Action.TButton",
            command=self.start_new_test,
        ).pack(pady=20)

        # Configure mouse wheel scrolling
        self.bind_mouse_wheel()

    def bind_mouse_wheel(self) -> None:
        """Bind mouse wheel to scroll results"""

        def _on_mouse_wheel(event: tk.Event) -> None:
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        self.canvas.bind_all("<MouseWheel>", _on_mouse_wheel)

    def on_show(self) -> None:
        """Update display when frame is shown"""
        self.show_results()

    def show_results(self) -> None:
        """Display test results"""
        # Clear previous results
        for widget in self.results_frame.winfo_children():
            widget.destroy()

        if not self.controller.current_test:
            return

        state = self.controller.current_test
        total_score = 0

        # Show results for each question
        for idx, question in enumerate(state.questions):
            result = state.answers.get(idx)
            if not result:
                continue

            # Create frame for this question
            question_frame = ttk.LabelFrame(
                self.results_frame,
                text=f"Question {idx + 1}: {question.name}",
                padding=10,
            )
            question_frame.pack(fill="x", pady=10, padx=10)

            # Question info
            ttk.Label(
                question_frame,
                text=f"Topic: {Topic.get_display_name(question.topic)}",
                font=("Helvetica", 10, "bold"),
            ).pack(anchor="w")

            # Question text
            # Question text
            question_label = ttk.Label(
                question_frame,
                text="Question:",
                font=("Helvetica", 10, "bold"),
            )
            question_label.pack(anchor="w", pady=(10, 0))

            question_text = ttk.Label(
                question_frame,
                text=question.prompt,
                wraplength=800,
            )
            question_text.pack(anchor="w", padx=10)

            # Expected format
            format_label = ttk.Label(
                question_frame,
                text="Expected Format:",
                font=("Helvetica", 10, "bold"),
            )
            format_label.pack(anchor="w", pady=(10, 0))

            format_text = ttk.Label(
                question_frame,
                text=question.answer_format,
                wraplength=800,
                foreground="gray",
            )
            format_text.pack(anchor="w", padx=10)

            # Your answer
            your_answer_label = ttk.Label(
                question_frame,
                text="Your Answer:",
                font=("Helvetica", 10, "bold"),
            )
            your_answer_label.pack(anchor="w", pady=(10, 0))

            your_answer_text = ttk.Label(
                question_frame,
                text=result["answer"],
                wraplength=800,
                foreground="navy",
            )
            your_answer_text.pack(anchor="w", padx=10)

            # Optimal solution if available
            if "optimal_solution" in result and result["optimal_solution"]:
                optimal_label = ttk.Label(
                    question_frame,
                    text="Optimal Solution:",
                    font=("Helvetica", 10, "bold"),
                )
                optimal_label.pack(anchor="w", pady=(10, 0))

                optimal_text = ttk.Label(
                    question_frame,
                    text=str(result["optimal_solution"]),
                    wraplength=800,
                    foreground="darkgreen",
                )
                optimal_text.pack(anchor="w", padx=10)

            # Score with color coding
            score = result["score"]
            total_score += score
            ttk.Label(
                question_frame,
                text=f"Score: {score}%",
                font=("Helvetica", 11, "bold"),
                foreground="darkgreen"
                if score >= 80
                else ("orange" if score >= 60 else "red"),
            ).pack(anchor="w", pady=(10, 5))

            # Feedback
            ttk.Label(
                question_frame,
                text="Feedback:",
                font=("Helvetica", 10, "bold"),
            ).pack(anchor="w", pady=(10, 0))
            feedback_text = ScrolledText(
                question_frame,
                height=4,
                font=("Helvetica", 10),
                wrap=tk.WORD,
            )
            feedback_text.insert("1.0", result["feedback"])
            feedback_text.config(state="disabled")
            feedback_text.pack(fill="x", pady=5)

        # Show final score
        if state.answers:
            avg_score = total_score / len(state.answers)
            ttk.Label(
                self.results_frame,
                text=f"\nFinal Score: {avg_score:.1f}%",
                font=("Helvetica", 16, "bold"),
                foreground="darkgreen"
                if avg_score >= 80
                else ("orange" if avg_score >= 60 else "red"),
            ).pack(pady=20)

    def start_new_test(self) -> None:
        """Start a new test"""
        self.controller.start_topic_selection()


if __name__ == "__main__":
    app = SmartTestApp()
    app.mainloop()
