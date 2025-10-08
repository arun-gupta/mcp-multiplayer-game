#!/bin/bash

# Check if a script path is provided
if [ $# -eq 0 ]; then
    echo "Error: No script specified to run"
    exit 1
fi

# The first argument is the script path
SCRIPT_PATH="$1"
shift  # Remove the first argument

# Check if the script exists in the mounted volume
if [ ! -f "$SCRIPT_PATH" ]; then
    echo "Error: Script $SCRIPT_PATH not found"
    exit 1
fi

# Make the script executable
chmod +x "$SCRIPT_PATH"

# Run the script with remaining arguments
exec "$SCRIPT_PATH" "$@"
