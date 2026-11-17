#!/usr/bin/env bash
set -euo pipefail

# Always run from the project root (where this script is located).
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

VENV_DIR=".venv"

if ! command -v python3 >/dev/null 2>&1; then
    echo "Error: python3 was not found in PATH."
    return 1 2>/dev/null || exit 1
fi

if [[ ! -d "$VENV_DIR" ]]; then
    echo "Creating virtual environment in $VENV_DIR..."
    python3 -m venv "$VENV_DIR"
else
    echo "Using existing virtual environment in $VENV_DIR..."
fi

"$VENV_DIR/bin/python" -m pip install --upgrade pip
"$VENV_DIR/bin/python" -m pip install -r requirements.txt

# If sourced, also activate in the current shell session.
if [[ "${BASH_SOURCE[0]}" != "$0" ]]; then
    # shellcheck disable=SC1091
    source "$VENV_DIR/bin/activate"
    echo "Done. Virtual environment is active in this shell."
else
    echo "Done. Activate it with: source .venv/bin/activate"
fi
