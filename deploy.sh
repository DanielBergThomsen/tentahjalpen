#!/bin/bash

# $1 = directory
# $2 = remote to push to

git stash --all
git checkout master
git subtree push --prefix $1 $2 master
