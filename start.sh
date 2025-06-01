#!/usr/bin/env bash

[[ "$1" == "1" ]] && TEST=true || TEST=false

MAX_RETRY=3
VDIR="zenv"
PKG_MNGR=("apt")
IS_TERMUX=$(echo "$HOME" | grep -q "termux" && echo true || echo false)
  
  
if [[ -f utils.sh ]]; then
  source utils.sh
else
  ui_print() { shift; echo "$@"; }
fi

cmd_exists() {
  command -v "$1" >/dev/null 2>&1
}

install_pkg() {
  local pkg="$1"
  local pkg_stripped=${pkg%%=*}
  shift
  local -a install_cmds=("$@")
  local bin=$(echo "$pkg" | cut -d'-' -f2)
  $IS_TERMUX && pkg="$bin"
  
  condition() {
    if [[ "${install_cmds[*]}" =~ pip ]]; then
      count=$(find -L "$VDIR" -type d -path "*/lib*/python*/site-packages/${pkg_stripped}*" | wc -l)
      (($count)) || return 0
    else
      ! cmd_exists "$bin" && return 0
    fi
    
    return 1
  }
  
  retry=0
  while condition; do
    (( retry++ ))
    ui_print info "Installing [$pkg_stripped] tries: ($retry/$MAX_RETRY)..."
    ${install_cmds[@]} "$pkg" >/dev/null 2>&1
    if (( retry >= MAX_RETRY )); then
      ui_print error "Error: Failed to install: [$pkg_stripped]"
      exit 1
    fi
  done
  
  if condition; then
    ui_print success "Installed: [$pkg_stripped]"
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
    ui_print error "Error: Not a valid directory: [$dir]"
    return 1
  fi
}

if ! $TEST; then
  if $IS_TERMUX; then
    PKG_MNGR=("$(resolve_pkg "pkg")")
  else
    if [[ "$(whoami)" != "root" ]]; then
      PKG_MNGR=("$(resolve_pkg "sudo")" "$(resolve_pkg "$PKG_MNGR")")
    fi
  fi

  if (( ${#PKG_MNGR[@]} )); then
    pkgs=(
      python3
      python3-pip
      chromium-chromedriver
    )
    
    for pkg in "${pkgs[@]}"; do install_pkg "$pkg" ${PKG_MNGR[@]} install -y; done
    
    if ! $IS_TERMUX; then
      alias python="python3"
      alias pip="pip3"
    else
      termux-wake-lock
    fi

    if ! grep -q "$PPREFIX" "$VDIR/pyvenv.cfg" 2>/dev/null; then
        ui_print info "Creating Python Virtual Environment..."
        python -m venv "$VDIR"
    fi
    
    if [[ -f "$VDIR/bin/activate" ]]; then
        source "$VDIR/bin/activate" && \
            ui_print success "Python Virtual Environment Activated!" || \
            ui_print error "Python Virtual Environment Failed to activate!"
    fi
    
    if [[ -n "$VIRTUAL_ENV" ]]; then
      for pkg in requests selenium beautifulsoup4 html5lib; do
        $IS_TERMUX && [[ "$pkg" == "selenium" ]] && pkg+="==4.9.1"
        install_pkg "$pkg" pip install --upgrade --no-deps
      done
    fi
  fi
fi

mkdir -p USERDATA

while IFS=" " read -r H U P; do
  [[ -z "$U" ]] && continue
  H="https://${H}-tams.com.ph"
  # mkdir_recursive "USERDATA/$U"
  python3 tams.py "homepage=$H username=$U password=$P"
done < USERS

exec_cmd deactivate

git pull -f >/dev/null 2>&1
git add -f . >/dev/null 2>&1 && \
git commit -m "Update" >/dev/null 2>&1
git push -f >/dev/null 2>&1

IS_TERMUX && termux-wake-unlock