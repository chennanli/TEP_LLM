#!/bin/bash
# This script sets up a Git repository and prepares it for GitHub

# Navigate to project directory
cd "$(dirname "$0")"

# Initialize Git repository
echo "Initializing Git repository..."
git init

# Add files to Git
echo "Adding files to Git..."
git add .

# Commit changes
echo "Committing changes..."
git commit -m "Initial commit of Tennessee Eastman Process LLM project"

echo "============================"
echo "Repository setup complete!"
echo "============================"
echo ""
echo "To connect to GitHub, create a repository on GitHub, then run:"
echo "git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git"
echo "git branch -M main"
echo "git push -u origin main"
echo ""
echo "Replace YOUR_USERNAME and YOUR_REPOSITORY_NAME with your GitHub username and repository name."
