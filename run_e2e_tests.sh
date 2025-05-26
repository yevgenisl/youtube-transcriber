#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Define the path to the Flask app (optional, if not running from root)
# export FLASK_APP=front-end/app.py

echo "Starting E2E tests..."

# Ensure dependencies are installed (optional, good practice)
# echo "Installing/updating dependencies..."
# pip install -r requirements.txt

# Run Robot Framework tests
# Pass any Robot options if needed, e.g., --outputdir reports/e2e
robot tests/e2e/api_tests.robot

echo "E2E tests finished."

# No explicit stop needed here if Robot's Suite Teardown handles it.
