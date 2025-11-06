from app_ui import AppUI
from quiz_controller import QuizController


def main():
    # 1. Create the root app window
    # We must do this first so the controller can have a
    # reference to it for `app.after()`
    app = AppUI(controller=None)  # Pass a temporary None

    # 2. Create the controller, passing it the app reference
    controller = QuizController(app_reference=app)

    # 3. Give the app the real controller
    app.controller = controller

    # 4. Manually re-run the parts of __init__ that needed
    #    the controller. This is a bit of a hack to solve
    #    the circular dependency, but it's clean.
    app.show_setup_frame()

    # 5. Start the app
    app.mainloop()


if __name__ == "__main__":
    main()
