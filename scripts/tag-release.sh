#!/usr/bin/env bash
set -euo pipefail

if [ $# -ne 1 ]; then
  echo "Usage: ./scripts/tag-release.sh <version> (example: 0.4.0)"; exit 1; fi
VERSION=$1
TAG="v${VERSION}"

if [[ ! $VERSION =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  echo "Version must match MAJOR.MINOR.PATCH"; exit 1; fi

# Ensure working tree clean
if [ -n "$(git status --porcelain)" ]; then
  echo "Working tree dirty. Commit or stash changes first."; exit 1; fi

git fetch --tags
if git rev-parse "$TAG" >/dev/null 2>&1; then
  echo "Tag $TAG already exists"; exit 1; fi

echo "Creating tag $TAG"
git tag -a "$TAG" -m "Release $TAG"
git push origin "$TAG"

echo "Tag pushed. CI will validate and create a draft release."
