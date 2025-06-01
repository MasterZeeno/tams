#!/usr/bin/env bash

ui_print() {
  (($#)) || return
  
  local -A ss=([normal]=30 [light]=90 [bold]=1 [dim]=2 [italic]=3)
  local l c1 c2="${ss[light]}" c3=7 e='\033[' t=' ' tm=false
  
  m() {
    local i="${1//[- ]/}"
    [[ -z "$i" ]] && return
    for k in "${!ss[@]}"; do
      if [[ "$k" == "${i,,}"* ]]; then
        echo "${ss[$k]}${2:-}"
        return
      fi
    done
  }
  
  while (($#)); do
    case "${1,,}" in
      success|error|warn|info)
        tm=true
        c1="1;"
        case "$1" in
          success)
            l='✔'
            c3=2
            ;;
          error)
            l='✖'
            c3=1
            ;;
          warn)
            l='⚠️'
            c3=3
            ;;
          info)
            l='𝒊'
            c3=6
            ;;
        esac
        ;;
        
      ✔|✖|⚠️)
        $tm || l="$1"
        ;;
        
      [0-7])
        $tm || c3="$1"
        ;;
        
      -t|--tab)
        shift
        [[ -n "$1" && "$1" != "--" ]] && t="$1"
        ;;
        
      -s|--style)
        shift
        if [[ -n "$1" && "$1" != "--" ]]; then
          for a in $(echo -n "${1//[- ]/}" | fold -w1); do
            [[ -z "$a" ]] && continue
            if [[ "$a" =~ ^[nl]$ ]]; then
              c2=$(m "$a")
            else
              $tm || c1+=$(m "$a" ";")
            fi
          done
        fi
        ;;
        
      -[bdi])
        $tm || c1+=$(m "$1" ";")
        ;;
        
      *)
        break
        ;;
    esac
    shift
  done
  
  printf "${e}${c1}$((c2+c3))m${t}${l} %s${e}0m\n" "$*"
}