#!/usr/bin/env bash

mkdir_recursive() {
  local dir=$(realpath -m "$1")
  dir="${dir#$(pwd)/}"

  local paths=$(pwd)
  IFS='/' read -ra folders <<< "$dir"
  for folder in "${folders[@]}"; do
    paths+="/$folder"
    mkdir -p "$paths"
  done
}


mkdir_recursive "$(pwd)/yawa/piste/kulera"