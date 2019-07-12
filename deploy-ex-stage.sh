#!/bin/bash
git branch -D rgmaster
git subtree split --prefix rg -b rgmaster
git push -f rg rgmaster:master
git branch -D rgmaster