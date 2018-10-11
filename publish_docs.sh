#!/bin/bash

set -ex

main_branch="dev"

git checkout gh-pages
git rm -rf .

git checkout $main_branch docs/
git checkout $main_branch memedata/
(cd docs && make html)

mv docs/build/html/* .
rm -rf docs memedata publish_docs.sh
touch .nojekyll

git add -A
git commit -m \
    "gen docs from `git log $main_branch -1 --pretty=short --abbrev-commit`"
git push origin gh-pages

git checkout dev
