#!/bin/bash
GITHUB_USER="${1:-0xmoda}"
REPO_NAME="${2:-crypto-pe-tracker}"

echo "🚀 Setting up GitHub remote..."
git remote remove origin 2>/dev/null
git remote add origin https://github.com/${GITHUB_USER}/${REPO_NAME}.git

echo "📤 Attempting to push..."
git branch -M main
if git push -u origin main 2>&1; then
    echo "✅ Successfully pushed to GitHub!"
    echo ""
    echo "Next steps:"
    echo "1. Enable GitHub Pages: https://github.com/${GITHUB_USER}/${REPO_NAME}/settings/pages"
    echo "2. Enable GitHub Actions: https://github.com/${GITHUB_USER}/${REPO_NAME}/actions"
    echo "3. Your site will be at: https://${GITHUB_USER}.github.io/${REPO_NAME}/"
else
    echo ""
    echo "❌ Push failed. This usually means:"
    echo "   1. The repository doesn't exist yet on GitHub"
    echo "   2. You need to create it first at: https://github.com/new"
    echo ""
    echo "After creating the repo, run this again:"
    echo "   ./push_to_github.sh ${GITHUB_USER} ${REPO_NAME}"
fi
