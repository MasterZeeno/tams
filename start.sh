#!/bin/sh

if ! command -v python3 >/dev/null 2>&1; then
  sudo apt install python -y
fi

if [ ! -d venv ]; then
  python3 -m venv venv
fi

. venv/bin/activate
if [ -f requirements.txt ]; then
  if pip3 -qqq install -r requirements.txt --break-system-packages; then
    [ -f main.py ] && python3 tams.py
  fi
fi

deactivate >/dev/null 2>&1
