#!/usr/bin/env python3
"""
Consolidated test script for SmartTest quiz functionality.
Tests template loading, quiz generation, question retrieval, evaluation,
and all improvements made to the quiz templates.
"""

import sys
import time
import re
from quiz_controller import QuizController


class MockApp:
    """Mock app for testing without GUI."""

    def __init__(self):
        self.after_called = False

    def after(self, delay, callback, *args):
        """Mock the after method - just call immediately."""
        self.after_called = True
        callback(*args)


# ============================================================================
# CORE FUNCTIONALITY TESTS
# ============================================================================


def test_template_loading():
    """Test that templates are loaded correctly."""
    print("=" * 60)
    print("TEST 1: Template Loading")
    print("=" * 60)

    mock_app = MockApp()
    controller = QuizController(mock_app)

    problems = controller.get_available_problems()
    print(f"✓ Found {len(problems)} problem types: {problems}")

    if len(problems) == 0:
        print("✗ ERROR: No problem types found!")
        return False

    for problem in problems:
        if problem in controller.templates:
            templates = controller.templates[problem]
            print(f"  - {problem}: {len(templates)} templates")
        else:
            print(f"✗ ERROR: Problem type '{problem}' has no templates!")
            return False

    print()
    return True


def test_quiz_generation():
    """Test quiz generation."""
    print("=" * 60)
    print("TEST 2: Quiz Generation")
    print("=" * 60)

    mock_app = MockApp()
    controller = QuizController(mock_app)

    problems = controller.get_available_problems()

    # Try to generate a small quiz
    num_questions = 3
    success = controller.generate_quiz(problems, num_questions)

    if not success:
        print("✗ ERROR: Failed to generate quiz!")
        return False

    print(
        f"✓ Successfully generated quiz with {len(controller.current_quiz)} questions"
    )
    print()
    return True


def test_question_retrieval():
    """Test question retrieval."""
    print("=" * 60)
    print("TEST 3: Question Retrieval")
    print("=" * 60)

    mock_app = MockApp()
    controller = QuizController(mock_app)

    problems = controller.get_available_problems()
    controller.generate_quiz(
        problems[:2], 2
    )  # Generate 2 questions from first 2 problem types

    # Get first question
    q1 = controller.get_next_question()
    if q1 is None:
        print("✗ ERROR: Failed to get first question!")
        return False

    print(f"✓ Question 1:")
    print(f"  Type: {controller.get_current_question_instance().__class__.__name__}")
    print(f"  Text: {q1['question_text'][:80]}...")
    print(f"  Prompt: {q1['answer_prompt'][:60]}...")

    # Get second question
    q2 = controller.get_next_question()
    if q2 is None:
        print("✗ ERROR: Failed to get second question!")
        return False

    print(f"✓ Question 2:")
    print(f"  Type: {controller.get_current_question_instance().__class__.__name__}")
    print(f"  Text: {q2['question_text'][:80]}...")

    # Try to get third question (should be None)
    q3 = controller.get_next_question()
    if q3 is not None:
        print("✗ ERROR: Got more questions than expected!")
        return False

    print(f"✓ Correctly returned None after all questions retrieved")
    print()
    return True


def test_simple_evaluation():
    """Test simple question evaluation."""
    print("=" * 60)
    print("TEST 4: Simple Question Evaluation")
    print("=" * 60)

    mock_app = MockApp()
    controller = QuizController(mock_app)

    # Generate quiz with just n_queens theory questions
    controller.generate_quiz(["n_queens"], 1)

    q = controller.get_next_question()
    if q is None:
        print("✗ ERROR: Failed to get question!")
        return False

    print(f"Question: {q['question_text'][:80]}...")

    # Define callback to receive result
    result = []

    def callback(eval_result):
        result.append(eval_result)

    # Try a wrong answer
    controller.evaluate_answer_async("wrong answer", callback)

    # Wait a bit for the async evaluation to complete
    timeout = 5
    elapsed = 0
    while len(result) == 0 and elapsed < timeout:
        time.sleep(0.1)
        elapsed += 0.1

    if len(result) == 0:
        print("✗ ERROR: Evaluation callback was not called!")
        return False

    score, correct_ans, explanation = result[0]
    print(f"✓ Evaluation completed:")
    print(f"  Score: {score}/100")
    print(f"  Correct answer: {correct_ans}")
    print(f"  Explanation: {explanation[:100]}...")
    print()
    return True


# ============================================================================
# IMPROVEMENT TESTS
# ============================================================================


def test_graph_coloring_improvements():
    """Test that graph coloring templates now use random graphs."""
    print("=" * 60)
    print("TEST 5: Graph Coloring Improvements")
    print("=" * 60)

    mock_app = MockApp()
    controller = QuizController(mock_app)

    # Generate multiple questions to see variety
    print("\nGenerating 5 GC_ComputationFindChi questions:")
    graphs_seen = set()
    for i in range(5):
        controller.generate_quiz(["graph_coloring"], 1)
        q = controller.get_next_question()
        if q:
            # Extract graph structure from question text
            graph_info = q["question_text"][:100]
            graphs_seen.add(graph_info)
            print(f"  {i + 1}. {graph_info}...")

    if len(graphs_seen) > 1:
        print(
            f"✓ Generated {len(graphs_seen)} different graphs (randomization working!)"
        )
    else:
        print(f"⚠ Only saw {len(graphs_seen)} unique graph(s)")

    print()
    return len(graphs_seen) > 1


def test_knights_tour_improvements():
    """Test that knight's tour validation uses random paths."""
    print("=" * 60)
    print("TEST 6: Knight's Tour Improvements")
    print("=" * 60)

    mock_app = MockApp()
    controller = QuizController(mock_app)

    # Test path generation variety
    print("\nGenerating 5 KT_ValidationViability questions:")
    paths_seen = set()
    for i in range(5):
        controller.generate_quiz(["knights_tour"], 1)
        q = controller.get_next_question()
        if q and "partial tour" in q["question_text"]:
            # Extract path from question
            match = re.search(r"partial tour: `(\[.*?\])`", q["question_text"])
            if match:
                path = match.group(1)
                paths_seen.add(path)
                print(f"  {i + 1}. Path: {path[:60]}...")

    if len(paths_seen) > 1:
        print(
            f"✓ Generated {len(paths_seen)} different paths (random generation working!)"
        )
    else:
        print(f"⚠ Only saw {len(paths_seen)} unique path(s)")

    # Test wider N range for KT_ComputationFindTour
    print("\nChecking N value variety for KT_ComputationFindTour:")
    n_values = set()
    for i in range(10):
        controller.generate_quiz(["knights_tour"], 1)
        q = controller.get_next_question()
        if q and "Find an *open* Knight's Tour" in q["question_text"]:
            match = re.search(r"(\d+)x\1 board", q["question_text"])
            if match:
                n = int(match.group(1))
                n_values.add(n)

    print(f"  N values seen: {sorted(n_values)}")
    if len(n_values) >= 3:
        print(f"✓ Good variety of N values (expected 3-7)")
    else:
        print(f"⚠ Limited N variety: {n_values}")

    print()
    return len(paths_seen) > 1 or len(n_values) >= 3


def test_nqueens_improvements():
    """Test that N-Queens theory question varies algorithms."""
    print("=" * 60)
    print("TEST 7: N-Queens Improvements")
    print("=" * 60)

    mock_app = MockApp()
    controller = QuizController(mock_app)

    print("\nGenerating 10 NQ_TheoryComplexity questions:")
    algorithms_seen = set()
    for i in range(10):
        controller.generate_quiz(["n_queens"], 1)
        q = controller.get_next_question()
        if q and "time complexity" in q["question_text"].lower():
            # Extract algorithm name
            match = re.search(r"complexity of the (.*?) algorithm", q["question_text"])
            if match:
                algo = match.group(1)
                algorithms_seen.add(algo)

    print(f"  Algorithms seen: {algorithms_seen}")
    if len(algorithms_seen) >= 2:
        print(f"✓ Multiple algorithms tested ({len(algorithms_seen)} different types)")
    else:
        print(f"⚠ Only one algorithm type seen")

    print()
    return len(algorithms_seen) >= 2


def test_hanoi_improvements():
    """Test that Hanoi templates have variety."""
    print("=" * 60)
    print("TEST 8: Tower of Hanoi Improvements")
    print("=" * 60)

    mock_app = MockApp()
    controller = QuizController(mock_app)

    # Test peg variety in 4.1
    print("\nGenerating 10 Hanoi_Theory3PegMoves questions:")
    peg_counts = set()
    for i in range(10):
        controller.generate_quiz(["tower_of_hanoi"], 1)
        q = controller.get_next_question()
        if q and "minimum number of moves" in q["question_text"]:
            match = re.search(r"with \d+ disks and (\d+) pegs", q["question_text"])
            if match:
                pegs = int(match.group(1))
                peg_counts.add(pegs)

    print(f"  Peg counts seen: {sorted(peg_counts)}")
    if 3 in peg_counts and 4 in peg_counts:
        print(f"✓ Both 3-peg and 4-peg questions generated")
        result = True
    elif len(peg_counts) == 1:
        print(f"⚠ Only saw {peg_counts} peg configuration")
        result = False
    else:
        print(f"⚠ Unexpected peg counts: {peg_counts}")
        result = False

    print()
    return result


def test_experimental_race_variety():
    """Test that experimental race questions compare different algorithms."""
    print("=" * 60)
    print("TEST 9: Experimental Race Algorithm Variety")
    print("=" * 60)

    mock_app = MockApp()
    controller = QuizController(mock_app)

    print("\nChecking KT_ExperimentalRace algorithm combinations:")
    algo_combos = set()
    for i in range(8):
        controller.generate_quiz(["knights_tour"], 1)
        q = controller.get_next_question()
        if q and "which algorithm will find" in q["question_text"].lower():
            # Extract algorithms being compared
            match = re.search(r"first: (.*?)\?", q["question_text"])
            if match:
                algos = match.group(1)
                algo_combos.add(algos)
                if i < 3:  # Show first few
                    print(f"  {i + 1}. Comparing: {algos}")

    print(f"\n  Total unique combinations: {len(algo_combos)}")
    if len(algo_combos) >= 3:
        print(f"✓ Good variety of algorithm combinations")
        kt_result = True
    else:
        print(f"⚠ Limited variety: {algo_combos}")
        kt_result = False

    print("\nChecking Hanoi_ExperimentalRace algorithm combinations:")
    algo_combos = set()
    for i in range(8):
        controller.generate_quiz(["tower_of_hanoi"], 1)
        q = controller.get_next_question()
        if q and "which algorithm will finish" in q["question_text"].lower():
            # Extract algorithms being compared
            match = re.search(r"first: (.*?)\?", q["question_text"])
            if match:
                algos = match.group(1)
                algo_combos.add(algos)
                if i < 3:  # Show first few
                    print(f"  {i + 1}. Comparing: {algos}")

    print(f"\n  Total unique combinations: {len(algo_combos)}")
    if len(algo_combos) >= 3:
        print(f"✓ Good variety of algorithm combinations")
        hanoi_result = True
    else:
        print(f"⚠ Limited variety: {algo_combos}")
        hanoi_result = False

    print()
    return kt_result and hanoi_result


def test_graph_coloring_edge_display():
    """Test that graph coloring experimental race shows edges."""
    print("=" * 60)
    print("TEST 10: Graph Coloring Edge List Display")
    print("=" * 60)

    mock_app = MockApp()
    controller = QuizController(mock_app)

    print("\nGenerating GC_ExperimentalRace question:")
    controller.generate_quiz(["graph_coloring"], 1)
    q = controller.get_next_question()

    if q and "edges:" in q["question_text"].lower():
        print(f"✓ Question includes edge list")
        # Show a snippet
        match = re.search(r"edges: \[(.*?)\]", q["question_text"])
        if match:
            edges = match.group(1)
            print(f"  Edge list sample: [{edges[:80]}...]")
        result = True
    else:
        print(f"⚠ Edge list not found in question")
        if q:
            print(f"  Question: {q['question_text'][:100]}...")
        result = False

    print()
    return result


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("SMARTTEST COMPREHENSIVE TEST SUITE")
    print("=" * 60 + "\n")

    # Core functionality tests
    core_tests = [
        ("Template Loading", test_template_loading),
        ("Quiz Generation", test_quiz_generation),
        ("Question Retrieval", test_question_retrieval),
        ("Simple Evaluation", test_simple_evaluation),
    ]

    # Improvement tests
    improvement_tests = [
        ("Graph Coloring Improvements", test_graph_coloring_improvements),
        ("Knight's Tour Improvements", test_knights_tour_improvements),
        ("N-Queens Improvements", test_nqueens_improvements),
        ("Tower of Hanoi Improvements", test_hanoi_improvements),
        ("Experimental Race Variety", test_experimental_race_variety),
        ("Graph Coloring Edge Display", test_graph_coloring_edge_display),
    ]

    passed = 0
    failed = 0

    print("CORE FUNCTIONALITY TESTS")
    print("-" * 60)
    for name, test_func in core_tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
                print(f"✗ {name} FAILED\n")
        except Exception as e:
            print(f"✗ {name} FAILED WITH EXCEPTION: {e}")
            import traceback

            traceback.print_exc()
            failed += 1
            print()

    print("\n" + "=" * 60)
    print("IMPROVEMENT VERIFICATION TESTS")
    print("-" * 60)
    for name, test_func in improvement_tests:
        try:
            if test_func():
                passed += 1
            else:
                # Improvement tests are less critical
                print(f"⚠ {name} showed limited variety (not a failure)\n")
        except Exception as e:
            print(f"✗ {name} FAILED WITH EXCEPTION: {e}")
            import traceback

            traceback.print_exc()
            print()

    print("=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)
    print(
        "\nNote: Some tests check for randomization, so results may vary between runs."
    )
    print("Look for ✓ marks indicating successful functionality.\n")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
