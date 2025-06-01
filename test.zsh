

[[ ! -v __FANCY_SOURCED__ ]] && {
  local __FANCY_PREFIX__="typeset -gr FANCY_"
  
cat << EOF > "${__CACHE_FILE__}"

${__FANCY_PREFIX__}RESET=$'\e[0m'
${__FANCY_PREFIX__}BOLD=$'\e[1m'
${__FANCY_PREFIX__}DIM=$'\e[2m'
${__FANCY_PREFIX__}ITALIC=$'\e[3m'
${__FANCY_PREFIX__}UNDERLINE=$'\e[4m'
${__FANCY_PREFIX__}BLACK=$'\e[30m'
${__FANCY_PREFIX__}RED=$'\e[31m'
${__FANCY_PREFIX__}GREEN=$'\e[32m'
${__FANCY_PREFIX__}YELLOW=$'\e[33m'
${__FANCY_PREFIX__}BLUE=$'\e[34m'
${__FANCY_PREFIX__}MAGENTA=$'\e[35m'
${__FANCY_PREFIX__}CYAN=$'\e[36m'
${__FANCY_PREFIX__}WHITE=$'\e[37m'
${__FANCY_PREFIX__}LIGHTER_BLACK=$'\e[90m'
${__FANCY_PREFIX__}LIGHTER_RED=$'\e[91m'
${__FANCY_PREFIX__}LIGHTER_GREEN=$'\e[92m'
${__FANCY_PREFIX__}LIGHTER_YELLOW=$'\e[93m'
${__FANCY_PREFIX__}LIGHTER_BLUE=$'\e[94m'
${__FANCY_PREFIX__}LIGHTER_MAGENTA=$'\e[95m'
${__FANCY_PREFIX__}LIGHTER_CYAN=$'\e[96m'
${__FANCY_PREFIX__}LIGHTER_WHITE=$'\e[97m'
${__FANCY_PREFIX__//-gr/-g}PRIMARY_COLOR=$'\e[96m'
${__FANCY_PREFIX__//-gr/-g}SECONDARY_COLOR=$'\e[93m'
EOF

  source "${__CACHE_FILE__}"
  chmod -rwx "${__CACHE_FILE__}"
}

