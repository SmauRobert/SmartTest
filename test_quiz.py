#!/usr/bin/env python3
"""
Simple test script to verify the quiz functionality without GUI.
"""

import sys
from quiz_controller import QuizController


class MockApp:
    """Mock app for testing without GUI."""

    def __init__(self):
        self.after_called = False

    def after(self, delay, callback, *args):
        """Mock the after method - just call immediately."""
        self.after_called = True
        callback(*args)


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
    import time

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


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("SMARTTEST QUIZ FUNCTIONALITY TESTS")
    print("=" * 60 + "\n")

    tests = [
        test_template_loading,
        test_quiz_generation,
        test_question_retrieval,
        test_simple_evaluation,
    ]

    passed = 0
    failed = 0

    for test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ TEST FAILED WITH EXCEPTION: {e}")
            import traceback

            traceback.print_exc()
            failed += 1
            print()

    print("=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
