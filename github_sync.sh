#!/bin/bash
echo "Enter GitHub Token:"
read TOKEN

REPO="resume-optimizer"
USER="areychana"

curl -H "Authorization: token $TOKEN" https://api.github.com/user/repos \
-d "{\"name\":\"$REPO\",\"private\":false}"

git init
git branch -M main
git add .
git commit -m "Initial commit - Resume Optimizer"
git remote add origin https://$TOKEN@github.com/$USER/$REPO.git
git push -u origin main

echo "✅ Repo created and code pushed!"