#!/bin/bash

# Get directory of the script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Check if tmux is installed
if ! command -v tmux &> /dev/null; then
    echo "tmux is not installed. Please install it first."
    exit 1
fi

# Check if pipenv is installed and create virtual environment if needed
if command -v pipenv &> /dev/null; then
    cd "$SCRIPT_DIR"
    # Create/update virtual environment if needed
    pipenv install --quiet
    # Get the path to the virtual environment's Python
    VENV_PYTHON=$(pipenv --py)
else
    echo "pipenv is not installed. Using system Python."
    VENV_PYTHON=$(which python)
fi

# Create new tmux session if it doesn't exist
if ! tmux has-session -t uttertype 2>/dev/null; then
    tmux new-session -s uttertype -d
    tmux send-keys -t uttertype "cd '$SCRIPT_DIR' && '$VENV_PYTHON' main.py" C-m
fi