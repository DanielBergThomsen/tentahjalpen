#!/bin/bash

git stash --all
git checkout master
git subtree push --prefix backend dokku-backend master
git subtree push --prefix frontend dokku-frontend master
