#!/usr/bin/env bash
# Republish site/ to the gh-pages branch (GitHub Pages root). Commits as Bo. Run after site/ changes and a walk pass.
set -euo pipefail
cd "$(dirname "$0")/.."
TMP=$(mktemp -d)
git worktree add -q --detach "$TMP"
( cd "$TMP" && git checkout -q gh-pages 2>/dev/null || git checkout -q --orphan gh-pages
  git rm -rq --cached . 2>/dev/null || true
  find . -mindepth 1 -maxdepth 1 ! -name .git -exec rm -rf {} +
  cp -r "$OLDPWD/site/." . && touch .nojekyll && git add -A
  git -c user.name="Bolgaç Gülen" -c user.email="bolgacg1@gmail.com" commit -q -m "Results page $(date +%Y-%m-%d\ %H:%M)" || true
  git push -q origin gh-pages )
git worktree remove --force "$TMP"
echo "gh-pages pushed"
