#!/usr/bin/env bash

cmd_exists() {
  command -v "$1" >/dev/null 2>&1
}

install_pkg() {
  local pkg="$1"
  local bin=$(echo "$pkg" | sed -E 's/(^| )((chromium|python3)-)/\1/Ig;s/^(pip)$/\1'"3"'/')
  $IS_TERMUX && pkg=$(echo "$bin" | sed -E 's/"3"//g')

  if ! cmd_exists "$bin"; then
    echo "Installing [$pkg]..."
    ${PKG_MNGR[@]} install "$pkg" -y >/dev/null 2>&1
  fi
}

resolve_pkg() {
  cmd_exists "$1" && echo "$1"
}

exec_cmd() {
  cmd_exists "$1" && "$@"
}

mkdir_recursive() {
  local dir=$(realpath -m "${1:?Missing directory path}")
  local base_dir=$(realpath -m "${2:-$(pwd)}")
  dir="${dir#$base_dir/}"

  IFS='/' read -ra folders <<< "$dir"
  for folder in "${folders[@]}"; do
    base_dir+="/$folder"
    mkdir -p "$base_dir" || return 1
  done
}

mkdir_var() {
  local var=${1:?Missing variable name}
  local dir=${2:?Missing directory path}

  if mkdir_recursive "$dir" && [[ -d "$dir" ]]; then
    printf -v "$var" '%s' $(realpath "$dir")
  else
    echo "Error: Not a valid directory: [$dir]" >&2
    return 1
  fi
}

TEST=false
[[ "$1" == "1" ]] && TEST=true

if ! $TEST; then
  VDIR="zenv"
  REQ_TXT="requirements.txt"
  PKG_MNGR=("apt")
  IS_TERMUX=$(echo "$HOME" | grep -q "termux" && echo true || echo false)

  if $IS_TERMUX; then
    PKG_MNGR=("$(resolve_pkg "pkg")")
  else
    if [[ "$(whoami)" != "root" ]]; then
      PKG_MNGR=("$(resolve_pkg "sudo")" "$(resolve_pkg "$PKG_MNGR")")
    fi
  fi

  if (( ${#PKG_MNGR[@]} )); then
    ${PKG_MNGR[@]} update >/dev/null 2>&1

    pkgs=(python3 python3-pip python3-selenium python3-requests chromium-chromedriver)
    
    for pkg in "${pkgs[@]}"; do
      install_pkg "$pkg"
    done

    # [[ -f "$VDIR/bin/activate" ]] || python3 -m venv "$VDIR"
    # source "$VDIR/bin/activate"

    # [[ -f "$REQ_TXT" ]] && pip3 -qqq install -r "$REQ_TXT" --break-system-packages
  fi
fi

while IFS=" " read -r H U P; do
  [[ -z "$U" ]] && continue
  H="https://${H}-tams.com.ph"
  mkdir_recursive "USERDATA/$U"
  python3 tams.py "homepage=$H username=$U password=$P"
done < USERS

exec_cmd deactivate

git add . >/dev/null 2>&1 && \
git commit -m "Update" >/dev/null 2>&1
git push >/dev/null 2>&1

# selenium==4.9.1