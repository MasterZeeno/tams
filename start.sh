#!/usr/bin/env bash

cmd_exists() {
  command -v "$1" >/dev/null 2>&1
}

install_pkg() {
  local pkg="$1"
  local bin=$(echo "$pkg" | sed -E 's/-driver//g')
  $IS_TERMUX && pkg=$(echo "$bin" | sed -E 's/"3"//g')

  ! cmd_exists "$bin" && \
    ${PKG_MNGR[@]} install "$pkg" -y >/dev/null 2>&1
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
    # ${PKG_MNGR[@]} update >/dev/null 2>&1

    pkgs=(python3 python3-pip python3-venv chromium-driver)
    
    for pkg in "${pkgs[@]}"; do
      install_pkg "$pkg"
    done

    [[ -d "$VDIR" ]] || python3 -m venv "$VDIR"
    . "$VDIR/bin/activate"

    [[ -f "$REQ_TXT" ]] && pip3 -qqq install -r "$REQ_TXT" --break-system-packages

    # while IFS=" " read -r HP UN PW; do
    #   [[ -z "$UN" ]] && continue

    #   HP="https://${HP}-tams.com.ph"
    #   mkdir_var UD "$DATA_DIR/$UN"

    #   for v in $(compgen -v); do
    #     [[ ${#v} -gt 2 ]] && continue
    #     var="${VARS[$v]}"
    #     [[ -n "$var" ]] && echo "$var"
    #   done
      
      # for key in "${!params[@]}"; do
          # value="${params[$key]}"
          # echo "KEY: $key, VALUE: $value"
      # done

      # python tams.py "$homepage" "$username" "$password" "$user_data_dir"
    # done < USERS
  fi
fi

while IFS=" " read -r H U P; do
  [[ -z "$U" ]] && continue
  H="https://${H}-tams.com.ph"
  mkdir_recursive "USERDATA/$U"
  python3 tams.py "homepage=$H username=$U password=$P"
done < USERS

exec_cmd deactivate
