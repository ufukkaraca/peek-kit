#!/usr/bin/env bash

# peek-kit update script
echo "Checking for updates..."

# Fetch the latest remote info without merging
git remote update > /dev/null 2>&1

LOCAL=$(git rev-parse @)
REMOTE=$(git rev-parse @{u} 2>/dev/null)

if [ -z "$REMOTE" ]; then
    echo "No remote tracking branch found. Please pull manually."
    exit 1
fi

if [ "$LOCAL" = "$REMOTE" ]; then
    echo "peek-kit is already up to date!"
    exit 0
fi

echo "An update is available for peek-kit!"
read -p "Do you want to pull the latest changes and update? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    # 1. Pull latest code
    git pull origin main

    # 2. Re-install Python dependencies
    pip install -e .

    echo ""
    echo "Update complete! You may need to restart your MCP client (like Claude Code) for changes to take effect."
else
    echo "Update cancelled."
fi
