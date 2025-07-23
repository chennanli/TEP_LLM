#!/bin/bash
# Script to push to GitHub after cleaning

echo "=== Pushing to GitHub ==="

# Pull with rebase
echo "Pulling from GitHub with rebase..."
git pull --rebase origin main

# Push to GitHub
echo "Pushing to GitHub..."
git push origin main

echo "=== Push complete ==="
echo "Check your GitHub repository at: https://github.com/chennanli/TEP_LLM"
