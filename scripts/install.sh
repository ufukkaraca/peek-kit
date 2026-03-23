#!/usr/bin/env bash

set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ROOT_DIR="$(dirname "$DIR")"

echo "Installing peek-kit in virtual environment..."
python3 -m venv "$ROOT_DIR/.venv"
source "$ROOT_DIR/.venv/bin/activate"
pip install -e "$ROOT_DIR"

echo "Checking accessibility permissions..."
python "$ROOT_DIR/scripts/check_permissions.py" || true

echo "Adding peek-kit to Claude's global MCP configuration (user scope)..."
claude mcp add -s user peek-kit -- "$ROOT_DIR/.venv/bin/peek-kit"

echo "Installation complete!"
echo "IMPORTANT: Please restart your Claude Code session (type /exit and open it again) for the tools to connect!"
