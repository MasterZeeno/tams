#!/bin/sh

if ! command -v "$1" >/dev/null 2>&1; then
  apt install python -y
fi

if [ ! -d venv ]; then
  python3 -m venv venv
fi

. venv/bin/activate
if [ -f requirements.txt ]; then
  if pip3 -qqq install -r requirements.txt; then
    [ -f main.py ] && python3 main.py
  fi
fi

deactivate >/dev/null 2>&1
