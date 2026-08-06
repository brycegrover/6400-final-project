#!/usr/bin/env bash
# push the project to github, safe to re-run for later updates
# usage: ./push_to_github.sh "commit message"
set -euo pipefail

cd "$(dirname "$0")"

REPO_URL="https://github.com/brycegrover/6400-final-project.git"
MSG="${1:-Update project}"

# git identity check so the first commit does not fail silently
if ! git config user.email >/dev/null 2>&1; then
    echo "git identity not set. Run these once, then re-run this script:"
    echo '  git config --global user.name "Bryce Grover"'
    echo '  git config --global user.email "bryceg5@outlook.com"'
    exit 1
fi

# initialize on first run
if [ ! -d .git ]; then
    git init
    git branch -M main
fi

# github recommends a readme, create a stub only if none exists
if [ ! -f README.md ]; then
    echo "# 6400-final-project" >> README.md
fi

# wire up the remote on first run
if ! git remote get-url origin >/dev/null 2>&1; then
    git remote add origin "$REPO_URL"
fi

# untrack this script if an earlier push included it, the gitignore keeps it out afterward
git rm --cached --ignore-unmatch -q push_to_github.sh

git add -A
if git diff --cached --quiet; then
    echo "Nothing new to commit"
else
    git commit -m "$MSG"
fi

git branch -M main
git push -u origin main
echo "Pushed to $REPO_URL"
