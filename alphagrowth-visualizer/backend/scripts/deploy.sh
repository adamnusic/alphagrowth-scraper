#!/bin/bash

# Exit on error
set -e

echo "Starting deployment..."

# Try to determine the correct backend directory
if [ -d "alphagrowth-visualizer/backend" ]; then
    # We're in the project root
    cd alphagrowth-visualizer/backend
elif [ -d "backend" ]; then
    # We're in the alphagrowth-visualizer directory
    cd backend
fi

# Verify we're in the correct directory
if [ ! -f "app.py" ]; then
    echo "Error: Could not find app.py. Current directory: $(pwd)"
    echo "Directory contents:"
    ls -la
    exit 1
fi

echo "Current directory: $(pwd)"

# Create data directory if it doesn't exist
mkdir -p data

# Run the setup script
echo "Setting up data directory..."
python scripts/setup_data.py

# Start the server
echo "Starting server..."
python app.py 