#!/bin/bash
# Script to clean up Git repository by removing large files from tracking

echo "=== Cleaning up Git repository ==="
echo "Removing large files from Git tracking (files will remain on your filesystem)"

# Create .gitkeep files to preserve directory structure
mkdir -p data/plots
mkdir -p data/simulation_results
touch data/plots/.gitkeep
touch data/simulation_results/.gitkeep

# Remove specific external_repos from Git tracking (but keep tep2py-master)
echo "Removing unnecessary external repositories from Git tracking..."
git rm -r --cached external_repos/FaultExplainer-* 2>/dev/null || true
git rm -r --cached external_repos/OptiChat-main/ 2>/dev/null || true
git rm -r --cached external_repos/sensorscan-main/ 2>/dev/null || true
git rm -r --cached external_repos/temexd_mod/ 2>/dev/null || true
git rm -r --cached external_repos/tennessee-eastman-profBraatz-master/ 2>/dev/null || true
echo "Keeping external_repos/tep2py-master/ as it's essential"

# Remove data files from Git tracking
echo "Removing data files from Git tracking..."
git rm --cached data/plots/*.png data/plots/*.jpg data/plots/*.jpeg data/plots/*.gif 2>/dev/null || true
git rm --cached data/simulation_results/*.csv data/simulation_results/*.dat 2>/dev/null || true

# Remove tep_env from Git tracking
echo "Removing tep_env from Git tracking..."
git rm -r --cached tep_env/ 2>/dev/null || true

# Remove .DS_Store files from Git tracking
echo "Removing .DS_Store files from Git tracking..."
find . -name ".DS_Store" -exec git rm --cached {} \; 2>/dev/null || true

# Commit changes
echo "Committing changes..."
git add .gitignore data/plots/.gitkeep data/simulation_results/.gitkeep
git add external_repos/tep2py-master/
git commit -m "Clean up repository: Remove large files from tracking, keep tep2py-master and folder structure"

echo "=== Clean up complete ==="
echo "Now try pushing to GitHub again with:"
echo "git pull --rebase origin main"
echo "git push origin main"
