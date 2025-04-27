#!/bin/sh

projdir="${0%/*}"

if [ -d "$projdir/venv" ]; then
  . "$projdir/venv/bin/activate"
  if [ -f "$projdir/requirements.txt" ]; then
    if pip3 -qqq install -r "$projdir/requirements.txt"; then
      if [ -f "$projdir/main.py" ]; then
        python3 "$projdir/main.py"
      fi
    fi
  fi
  deactivate 2>/dev/null
else
  echo "Virtual env not found."
fi
