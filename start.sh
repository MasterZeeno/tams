#!/bin/bash

cmd_exists() {
  command -v "$1" >/dev/null 2>&1
}

install_pkg() {
  local pkg="$1"
  local bin=$(echo "$pkg" | sed -E 's/-driver//g')
  $is_termux && pkg=$(echo "$bin" | sed -E 's/"3"//g')

  ! cmd_exists "$bin" && \
    ${pkg_mngr[@]} install "$pkg" -y
}

cmd_exec() {
  cmd_exists "$1" && "$@"
}

resolve_pkg() {
  cmd_exists "$1" && echo "$1"
}

pkg_mngr=("apt")
is_termux=$(echo "$HOME" | grep -q "termux" && echo true || echo false)

if $is_termux; then
  pkg_mngr=("$(resolve_pkg "pkg")")
else
  if [[ "$(whoami)" != "root" ]]; then
    pkg_mngr=("$(resolve_pkg "sudo")" "$(resolve_pkg "$pkg_mngr")")
  fi
fi

if (( ${#pkg_mngr[@]} )); then
  pkgs=(python3 python3-pip chromium-driver)
  
  for pkg in "${pkgs[@]}"; do
    install_pkg "$pkg"
  done

  if ! $is_termux; then
    alias python=${pkgs[0]}
    alias pip=${pkgs[1]#${pkgs[0]}-}
  fi

  [[ -d venv ]] || python -m venv venv
  . venv/bin/activate

  [[ -f requirements.txt ]] && pip -qqq install -r requirements.txt --break-system-packages

  base_dir="$(pwd)/USERDATA"
  mkdir -p "$base_dir"
  params=()

  while IFS=" " read -r homepage username password; do
    [[ -z "${homepage}${username}${password}" ]] && continue

    homepage="https://${homepage}-tams.com.ph"
    user_data_dir="$base_dir/$username"
    mkdir -p "$user_data_dir"

    for var in homepage username password user_data_dir; do
      eval "val=\$var"
      params[$var]="$val"
    done

    # python tams.py "$homepage" "$username" "$password" "$user_data_dir"
  done < USERS

  deactivate
fi
