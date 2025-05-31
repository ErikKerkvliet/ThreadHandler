import sys
import os

# Add the 'src' directory to Python's path so it can find the modules
# This is often needed if main.py is one level above src
project_root = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(project_root, "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Now you can import from src.MainUI
# If you have src/__init__.py, this should work smoothly
try:
    from MainUI import start_ui_and_app
except ImportError as e:
    print(f"Error importing MainUI: {e}")
    print("Ensure 'src' directory is in Python's path and contains __init__.py")
    sys.exit(1)


if __name__ == "__main__":
    # The application's entry point is now here.
    # All logic, including CLI argument handling and UI startup,
    # is encapsulated in start_ui_and_app() from MainUI.py
    start_ui_and_app()