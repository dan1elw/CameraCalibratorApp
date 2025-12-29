#!/usr/bin/env bash
set -euo pipefail

# Setup script to install Python requirements for CameraCalibratorApp
# Usage: ./setup.sh (or run the pip command below directly)

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 not found on PATH; please install Python 3"
  exit 1
fi

python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

echo
echo "Done. If the GUI fails to start because of tkinter, on Debian/Ubuntu run:"
echo "  sudo apt update && sudo apt install python3-tk"
echo
echo "You can also run: python3 -m pip install -r requirements.txt"
