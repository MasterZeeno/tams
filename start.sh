#!/usr/bin/env bash

if ! command -v python3 >/dev/null 2>&1; then
  sudo apt install python -y
fi

[[ -d venv ]] || python3 -m venv venv
. venv/bin/activate

[[ -f requirements.txt ]] && pip3 -qqq install -r requirements.txt --break-system-packages

DIR="USERDATA"

while IFS=" " read -r url user pass; do
  [[ -z "$url" ]] && continue
  url="https://${url}-tams.com.ph"
  mkdir -p "$DIR/$user"
  echo "- Preparing [$user] data..."
  python3 tams.py "$url" "$user" "$pass"
done < USERS

deactivate
