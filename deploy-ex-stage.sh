#!/bin/bash
git branch -D ahmaster
git subtree split --prefix ah -b ahmaster
git push -f ah ahmaster:master
git branch -D ahmaster