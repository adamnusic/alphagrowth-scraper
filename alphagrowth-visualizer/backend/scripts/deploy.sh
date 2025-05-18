#!/bin/bash

# Exit on error
set -e

echo "Starting deployment..."

# Navigate to the backend directory
cd "$(dirname "$0")/.."

# Create data directory if it doesn't exist
mkdir -p data

# Run the setup script
echo "Setting up data directory..."
python scripts/setup_data.py

# Start the server
echo "Starting server..."
python app.py 