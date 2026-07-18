#!/usr/bin/env bash
# Initialize git and push to GitHub repository cachy-new-config

cd "$(dirname "$0")" || exit 1

if [ ! -d ".git" ]; then
    echo "Initializing git repository..."
    git init
    git branch -M main
fi

git remote remove origin 2>/dev/null
git remote add origin https://github.com/omarahmed321/cachy-new-config.git

# Configure local git user if not set globally
if [ -z "$(git config --get user.name)" ]; then
    git config --local user.name "omarahmed321"
fi
if [ -z "$(git config --get user.email)" ]; then
    git config --local user.email "omarahmed321@users.noreply.github.com"
fi

git add .
git commit -m "Initialize cachy-new-config setup repository"

echo "Pushing to GitHub..."
echo "If prompted, please enter your GitHub username and Personal Access Token (PAT)."
git push -u origin main
