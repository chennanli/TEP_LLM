#!/bin/bash
# Script to reset and recommit the repository properly

echo "=== Resetting and recommitting repository ==="

# Reset to initial state (no commits)
echo "Resetting repository to initial state..."
git reset --soft $(git rev-list --max-parents=0 HEAD)

# Unstage everything
echo "Unstaging all files..."
git reset HEAD -- .

# Add only files we want to include (respecting .gitignore)
echo "Adding files respecting .gitignore..."
git add .

# Show what will be committed
echo "Files that will be committed:"
git status

# Ask for confirmation
read -p "Do you want to proceed with the commit? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    echo "Operation canceled."
    exit 1
fi

# Commit
echo "Committing files..."
git commit -m "Initial commit of Tennessee Eastman Process LLM project"

# Force push
echo "Force pushing to GitHub..."
git push -f origin main

echo "=== Operation complete ==="
echo "Check your GitHub repository at: https://github.com/chennanli/TEP_LLM"
