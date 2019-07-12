#!/bin/bash
git branch -D etlmaster
git subtree split --prefix etl -b etlmaster
git push -f trader-etl etlmaster:master
git branch -D etlmaster