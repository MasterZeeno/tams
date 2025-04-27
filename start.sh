#!/bin/sh

check_cmd() {
  command -v "$1" >/dev/null 2>&1
}

check_cmd python || apt install python -y

alias python='python3'
alias pip='pip3'

if [ ! -d venv ]; then
  python -m venv venv
fi

. venv/bin/activate
if [ -f requirements.txt ]; then
  if pip -qqq install -r requirements.txt; then
    [ -f main.py ] && python main.py
  fi
fi

deactivate
