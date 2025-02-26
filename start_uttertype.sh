#!/bin/bash

# Get directory of the script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Check if tmux is installed
if ! command -v tmux &> /dev/null; then
    echo "tmux is not installed. Please install it first."
    exit 1
fi

# Check if uv is installed and create virtual environment if needed
if command -v uv &> /dev/null; then
    cd "$SCRIPT_DIR"
    # Create virtual environment and install dependencies if needed
    if [ ! -d ".venv" ]; then
        uv sync
    fi
    VENV_PYTHON="$SCRIPT_DIR/.venv/bin/python"
else
    echo "uv is not installed. Using system Python."
    VENV_PYTHON=$(which python)
fi

# Create new tmux session if it doesn't exist
if ! tmux has-session -t uttertype 2>/dev/null; then
    tmux new-session -s uttertype -d
    tmux send-keys -t uttertype "cd '$SCRIPT_DIR' && '$VENV_PYTHON' main.py" C-m
fi