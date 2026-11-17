#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

source .venv/bin/activate

export SDL_VIDEODRIVER=wayland
export LIBGL_ALWAYS_SOFTWARE=1

python main.py
