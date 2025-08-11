#!/bin/bash

# Fix Contributors Script
# Ensures all commits are properly attributed to chennanli

set -e

echo "🔧 Fixing Git Contributors"
echo "========================="

# Set correct git configuration
echo "📝 Setting correct git configuration..."
git config user.name "chennanli"
git config user.email "chennanli@gmail.com"

# Check current configuration
echo "✅ Current git configuration:"
echo "Name: $(git config user.name)"
echo "Email: $(git config user.email)"

# Check for any commits with incorrect authors
echo "🔍 Checking for commits with incorrect authors..."
INCORRECT_COMMITS=$(git log --all --pretty=format:"%h %an <%ae>" | grep -v "chennanli <chennanli@gmail.com>" | wc -l)

if [ "$INCORRECT_COMMITS" -gt 0 ]; then
    echo "⚠️  Found $INCORRECT_COMMITS commits with incorrect authors:"
    git log --all --pretty=format:"%h %an <%ae> %s" | grep -v "chennanli <chennanli@gmail.com>"
    
    echo ""
    echo "🔧 To fix this, we would need to rewrite git history."
    echo "This is a destructive operation. Do you want to proceed? (y/N)"
    read -r response
    
    if [[ "$response" =~ ^[Yy]$ ]]; then
        echo "🔄 Rewriting git history to fix author information..."
        
        # Use git filter-branch to fix author information
        git filter-branch --env-filter '
        OLD_EMAIL="claude@anthropic.com"
        CORRECT_NAME="chennanli"
        CORRECT_EMAIL="chennanli@gmail.com"
        
        if [ "$GIT_COMMITTER_EMAIL" = "$OLD_EMAIL" ]
        then
            export GIT_COMMITTER_NAME="$CORRECT_NAME"
            export GIT_COMMITTER_EMAIL="$CORRECT_EMAIL"
        fi
        if [ "$GIT_AUTHOR_EMAIL" = "$OLD_EMAIL" ]
        then
            export GIT_AUTHOR_NAME="$CORRECT_NAME"
            export GIT_AUTHOR_EMAIL="$CORRECT_EMAIL"
        fi
        ' --tag-name-filter cat -- --branches --tags
        
        echo "✅ Git history rewritten successfully!"
        echo "🚀 Force pushing to GitHub..."
        git push origin main --force
        
    else
        echo "❌ Operation cancelled."
    fi
else
    echo "✅ All commits are correctly attributed to chennanli!"
fi

# Create a .mailmap file to ensure correct attribution
echo "📧 Creating .mailmap file for consistent attribution..."
cat > .mailmap << 'EOF'
# .mailmap file to ensure consistent git attribution
chennanli <chennanli@gmail.com>
chennanli <chennanli@gmail.com> claude <claude@anthropic.com>
chennanli <chennanli@gmail.com> Claude <claude@anthropic.com>
chennanli <chennanli@gmail.com> claude Claude
EOF

echo "✅ Created .mailmap file to ensure consistent attribution"

# Check if .mailmap should be committed
if [ ! -f .mailmap ] || ! git ls-files --error-unmatch .mailmap > /dev/null 2>&1; then
    echo "📝 Adding .mailmap to repository..."
    git add .mailmap
    git commit -m "fix: add .mailmap for consistent git attribution

- Ensure all commits are attributed to chennanli
- Map any potential claude commits to chennanli
- Improve contributor accuracy on GitHub"
    
    echo "🚀 Pushing .mailmap to GitHub..."
    git push origin main
fi

echo ""
echo "✅ Contributor fix complete!"
echo ""
echo "🎯 Next steps:"
echo "1. Check GitHub repository - contributors should now be correct"
echo "2. If 'claude' still appears, it may take time for GitHub to update"
echo "3. GitHub caches contributor information, so changes may take 24-48 hours"
echo ""
echo "📚 What was done:"
echo "- Set correct git configuration (chennanli)"
echo "- Created .mailmap file to map any claude commits to chennanli"
echo "- Ensured all future commits will be correctly attributed"
