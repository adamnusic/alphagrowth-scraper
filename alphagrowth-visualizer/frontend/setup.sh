#!/bin/bash

# Install dependencies
npm install

# Create necessary directories if they don't exist
mkdir -p src/components

# Create a .gitignore file
echo "node_modules/
dist/
.env
*.log" > .gitignore

echo "Setup complete! You can now run 'npm run dev' to start the development server." 