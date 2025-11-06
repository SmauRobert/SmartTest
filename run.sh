#!/bin/bash
# SmartTest Quiz Application Launcher
# This script activates the virtual environment and runs the application

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to the project directory
cd "$SCRIPT_DIR"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Error: Virtual environment not found!"
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "Installing dependencies..."
    ./venv/bin/pip install -r requirements.txt
fi

# Check if dependencies are installed
if ! ./venv/bin/python -c "import customtkinter" 2>/dev/null; then
    echo "Installing missing dependencies..."
    ./venv/bin/pip install -r requirements.txt
fi

echo "Starting SmartTest Quiz Application..."
echo "Press Ctrl+C to exit"
echo ""

# Run the application
./venv/bin/python main.py

# Exit with the same exit code as the Python script
exit $?
