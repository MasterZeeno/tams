#!/data/data/com.termux/files/usr/bin/zsh

typeset -gix USE_COLOR=1
typeset -gx RESET=$'\e[0m'
typeset -gx BOLD=$'\e[1m'
typeset -gx DIM=$'\e[2m'
typeset -gx ITALIC=$'\e[3m'
typeset -gx UNDERLINE=$'\e[3m'
typeset -gx BLACK=$'\e[30m'
typeset -gx RED=$'\e[31m'
typeset -gx GREEN=$'\e[32m'
typeset -gx YELLOW=$'\e[33m'
typeset -gx BLUE=$'\e[34m'
typeset -gx MAGENTA=$'\e[35m'
typeset -gx CYAN=$'\e[36m'
typeset -gx WHITE=$'\e[37m'

typeset -gx PRIMARY="${CYAN}" # PRIMARY
typeset -gx SECONDARY="${YELLOW}"  # SECONDARY

typeset -gx RP="${RESET}${PRIMARY}" # RESET PRIMARY
typeset -gx RPB="${RP}${BOLD}" # RESET PRIMARY BOLD
typeset -gx RPD="${RP}${DIM}"  # RESET PRIMARY DIM
typeset -gx RPI="${RP}${ITALIC}"  # RESET PRIMARY ITALIC
typeset -gx RPBD="${RPB}${DIM}" # RESET PRIMARY BOLD DIM
typeset -gx RPBI="${RPB}${ITALIC}" # RESET PRIMARY BOLD ITALIC
typeset -gx RPDI="${RPD}${ITALIC}"  # RESET PRIMARY DIM ITALIC

typeset -gx RS="${RESET}${SECONDARY}" # RESET SECONDARY
typeset -gx RSB="${RS}${BOLD}" # RESET SECONDARY BOLD
typeset -gx RSD="${RS}${DIM}"  # RESET SECONDARY DIM
typeset -gx RSI="${RS}${ITALIC}"  # RESET SECONDARY ITALIC
typeset -gx RSBD="${RSB}${DIM}" # RESET SECONDARY BOLD DIM
typeset -gx RSBI="${RSB}${ITALIC}" # RESET SECONDARY BOLD ITALIC
typeset -gx RSDI="${RSD}${ITALIC}"  # RESET SECONDARY DIM ITALIC

fdir() {
  local startpath="$PWD"
  local dirs_excluded='.*'
  local -i ret_count=1
  local -i include_hidden=0
  local -i show_fullpath=0
  local -a dirs=()
  local -i counter=0
  local color_output=auto
  
  unset_color_vars() {
    local -A color_vars=(
      RP RPB RPD RPI RPBD RPBI RPDI
      RS RSB RSD RSI RSBD RSBI RSDI
    )
  }
  
  boring_print() {
    # Use POSIX-compliant sed if needed: 's/\x1b\[[0-9;]*[a-zA-Z]//g'
    printf '%s\n' "$@" | sed -E 's/\x1B\[[0-9;]*[a-zA-Z]//g'
  }
  
  fancy_print() {
    if [[ "$color_output" == "none" ]] || \
      [[ ! -o interactive ]] || [[ ! -t 1 ]]; then
        boring_print "$@"
    else
      printf '%b\n' "$@"
    fi
  }

  
  abort() {
    printf '%b\n' "${RED}${BOLD}${1:-Aborted!}${RESET}" >&2
    return 1
  }
  
  show_help() {
    clear
    printf '%b\n' "
${RPB}Usage: ${RSB}fdir${RP} [${RSBI}options${RP}] [<${RSBI}path${RP}>|<${RSBI}PWD${RP}>]${RESET}

${RPB}Options:${RESET}
 ${RPB}-A${RP}, ${RPB}--All${RP}          ${RPI}Include hidden folders${RESET}
 ${RPB}-a${RP}, ${RPB}--all${RP}          ${RPBI}Exclude hidden folders${RP}${RSI}*${RESET}
 ${RPB}-f${RP}, ${RPB}--full${RP}         ${RPI}Show full path${RESET}
 ${RPB}-b${RP}, ${RPB}--base${RP}         ${RPBI}Show basename only${RP}${RSI}*${RESET}
 ${RPB}-n${RP}, ${RPB}--count${RP}=<${RSBI}num${RP}>  ${RPI}Number of folders to return${RESET}
 ${RPB}-p${RP}, ${RPB}--path${RP}=<${RSBI}path${RP}>  ${RPI}Set starting path${RESET}
 ${RPB}-h${RP}, ${RPB}--help${RP}         ${RPI}Show this help message${RESET}"
  }

  # Parse long options manually
  while [[ "$1" == --* ]]; do
    case "$1" in
      --)          [[ -d "$1" ]] && \
                    { startpath="$1"
                      shift; break; } ;;
      --all)        include_hidden=0 ;;
      --almost-all) include_hidden=1 ;;
      --full)        show_fullpath=1 ;;
      --base)      show_fullpath=0 ;;
      --count=*)   ret_count="${1#*=}" ;;
      --path=*)    startpath="${1#*=}" ;;
      --color=*)   color_output="${1#*=}" ;;
      --help)      show_help; return 1 ;;
      *) abort "Unknown option: $1" ;;
    esac
    shift
  done

  # Handle short options
  while getopts 'Aafbn:p:h' opt; do
    case "$opt" in
      A) include_hidden=1 ;;
      a) include_hidden=0 ;;
      f) show_fullpath=1 ;;
      b) show_fullpath=0 ;;
      n) [[ "$OPTARG" =~ ^[0-9]+$ ]] && \
          ((OPTARG)) && ret_count="$OPTARG" ;;
      p) [[ -d "$OPTARG" ]] && \
        startpath="$OPTARG" ;;
      h) show_help; return 1 ;;
      *) return 1 ;;
    esac
  done
  shift $((OPTIND - 1))

  # Adjust excluded dirs logic
  ((include_hidden)) && dirs_excluded='____'
  
  while (($#)); do
    [[ -d "$1" ]] && \
      { startpath="$1"; break; }
    shift
  done

  # Scan for non-empty dirs
  find "$startpath" -mindepth 1 -maxdepth 1 -type d \
    ! -name "$dirs_excluded" 2>/dev/null | \
  while IFS= read -r dir; do
    if find "$dir" -mindepth 1 -print -quit | grep -q .; then
      ((counter++))
      ((show_fullpath)) && dirs+=("$(realpath "$dir")") || dirs+=("${dir##*/}")
      ((counter >= ret_count)) && break
    fi
  done

  # Output result
  if (( ${#dirs[@]} )); then
    printf '%s\n' ${dirs[@]}
    print -z "cd ${dirs[1]}"
  else
    return 1
  fi
}

# Execute if not sourced
if [[ "${(%):-%N}" == "$0" ]]; then
  fdir "$@"
fi