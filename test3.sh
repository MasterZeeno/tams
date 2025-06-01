#!/data/data/com.termux/files/usr/bin/bash

save_theme_variables_to_file() {

  clear
  
  split() {
    printf '%s\n' "${1:?}" | tr "${2:- }" '\n'
  }
  
  rept() {
    printf '%*s' "${1:-1}" | tr ' ' "${2:- }"
  }
  
  block() {
    local len=48 char='#' p bl br w
    while (($#)); do case "$1" in [0-9]*) len=$1;;
        *) [[ "${#1}" -eq 1 ]] && char="$1" || break;;
      esac; shift; done
    local t="${*:-}"
    len=$(((len-(${#t}+2))/2))
    p=$((len/10))
    w="$(rept $((len+${#t})) "$char")"
    bl="$(rept $p "$char")"
    br="$(rept $((len-p)) "$char")"
    echo -e "$w\n$bl${t:+ $t }$br\n$w"
  }
  
  resolve_var() {
    local var="${1:?}"
    echo -e "\nif [[ ! -v $var || -z \"\$$var\" ]]; then\n$s$d $var=("
  }
  
  local shell="${1:-$(command -v bash)}"
  local shebang=$(printf '#!%s\n' $(realpath "$shell"))
  local s=$(rept 2) d="declare"
  [[ $shell =~ bash$ ]] || \
    d="typeset"; d+=" grA"
  local prefix="PRESET_THEME"
  local title="${prefix%%_*} VARIABLES"
  local func_name="ui_print"
  local variables_string2
  local variables_string="
if [[ ! -v ${prefix}_COLORS || -z \"\$${prefix}_COLORS\" ]]; then\n$s$d ${prefix}_COLORS=(
$s$s[black]=0 [red]=1 [green]=2 [yellow]=3 [blue]=4 [magenta]=5 [cyan]=6 [white]=7
$s$s[grey]=8 [maroon]=9 [lime]=10 [olive]=11 [navy]=12 [fuchsia]=13 [aqua]=14 [teal]=14
$s$s[silver]=15 [grey0]=16 [navyblue]=17 [darkblue]=18 [blue3]=20 [blue1]=21 [darkgreen]=22 [deepskyblue4]=25
$s$s[dodgerblue3]=26 [dodgerblue2]=27 [green4]=28 [springgreen4]=29 [turquoise4]=30 [deepskyblue3]=32 [dodgerblue1]=33 [darkcyan]=36
$s$s[lightseagreen]=37 [deepskyblue2]=38 [deepskyblue1]=39 [green3]=40 [springgreen3]=41 [cyan3]=43 [darkturquoise]=44 [turquoise2]=45
$s$s[green1]=46 [springgreen2]=47 [springgreen1]=48 [mediumspringgreen]=49 [cyan2]=50 [cyan1]=51 [purple4]=55 [purple3]=56
$s$s[blueviolet]=57 [grey37]=59 [mediumpurple4]=60 [slateblue3]=62 [royalblue1]=63 [chartreuse4]=64 [paleturquoise4]=66 [steelblue]=67
$s$s[steelblue3]=68 [cornflowerblue]=69 [darkseagreen4]=71 [cadetblue]=73 [skyblue3]=74 [chartreuse3]=76 [seagreen3]=78 [aquamarine3]=79
$s$s[mediumturquoise]=80 [steelblue1]=81 [seagreen2]=83 [seagreen1]=85 [darkslategray2]=87 [darkred]=88 [darkmagenta]=91 [orange4]=94
$s$s[lightpink4]=95 [plum4]=96 [mediumpurple3]=98 [slateblue1]=99 [wheat4]=101 [grey53]=102 [lightslategrey]=103 [mediumpurple]=104
$s$s[lightslateblue]=105 [yellow4]=106 [darkseagreen]=108 [lightskyblue3]=110 [skyblue2]=111 [chartreuse2]=112 [palegreen3]=114 [darkslategray3]=116
$s$s[skyblue1]=117 [chartreuse1]=118 [lightgreen]=120 [aquamarine1]=122 [darkslategray1]=123 [deeppink4]=125 [mediumvioletred]=126 [darkviolet]=128
$s$s[purple]=129 [mediumorchid3]=133 [mediumorchid]=134 [darkgoldenrod]=136 [rosybrown]=138 [grey63]=139 [mediumpurple2]=140 [mediumpurple1]=141
$s$s[darkkhaki]=143 [navajowhite3]=144 [grey69]=145 [lightsteelblue3]=146 [lightsteelblue]=147 [darkolivegreen3]=149 [darkseagreen3]=150 [lightcyan3]=152
$s$s[lightskyblue1]=153 [greenyellow]=154 [darkolivegreen2]=155 [palegreen1]=156 [darkseagreen2]=157 [paleturquoise1]=159 [red3]=160 [deeppink3]=162
$s$s[magenta3]=164 [darkorange3]=166 [indianred]=167 [hotpink3]=168 [hotpink2]=169 [orchid]=170 [orange3]=172 [lightsalmon3]=173
$s$s[lightpink3]=174 [pink3]=175 [plum3]=176 [violet]=177 [gold3]=178 [lightgoldenrod3]=179 [tan]=180 [mistyrose3]=181
$s$s[thistle3]=182 [plum2]=183 [yellow3]=184 [khaki3]=185 [lightyellow3]=187 [grey84]=188 [lightsteelblue1]=189 [yellow2]=190
$s$s[darkolivegreen1]=192 [darkseagreen1]=193 [honeydew2]=194 [lightcyan1]=195 [red1]=196 [deeppink2]=197 [deeppink1]=199 [magenta2]=200
$s$s[magenta1]=201 [orangered1]=202 [indianred1]=204 [hotpink]=206 [mediumorchid1]=207 [darkorange]=208 [salmon1]=209 [lightcoral]=210
$s$s[palevioletred1]=211 [orchid2]=212 [orchid1]=213 [orange1]=214 [sandybrown]=215 [lightsalmon1]=216 [lightpink1]=217 [pink1]=218
$s$s[plum1]=219 [gold1]=220 [lightgoldenrod2]=222 [navajowhite1]=223 [mistyrose1]=224 [thistle1]=225 [yellow1]=226 [lightgoldenrod1]=227
$s$s[khaki1]=228 [wheat1]=229 [cornsilk1]=230 [grey100]=231 [grey3]=232 [grey7]=233 [grey11]=234 [grey15]=235
$s$s[grey19]=236 [grey23]=237 [grey27]=238 [grey30]=239 [grey35]=240 [grey39]=241 [grey42]=242 [grey46]=243
$s$s[grey50]=244 [grey54]=245 [grey58]=246 [grey62]=247 [grey66]=248 [grey70]=249 [grey74]=250 [grey78]=251
$s)\nfi
$s$d ${prefix}_TEXT_FORMATS=( [bold]=1 [dim]=2 [italic]=3 )
"
# $s$d ${prefix}S=("

  variables_string+=$(resolve_var "${prefix}S")
  # variables_string+="$(resolve_var "${prefix}_TEXT_FORMATS" "( [bold]=1 [dim]=2 [italic]=3 )")\n"
  # variables_string+="$(resolve_var "${prefix}S")\n"
# $s$d ${prefix}_TEXT_FORMATS=( [bold]=1 [dim]=2 [italic]=3 )
# $s$d ${prefix}S=("

  local -A presets=(
  	[warning]="header_icon=☢︎|list_icon=»|color=yellow|text_style=bold"
  	[error]="header_icon=|list_icon=»|color=red|text_style=bold"
  	[info]="header_icon=𝒊|list_icon=»|color=blue|text_style=bold"
  	[success]="header_icon=|list_icon=»|color=green|text_style=bold"
  	[default]="header_icon=|list_icon=|color=white|text_style=bold"
  )
  
  for key in $(printf '%s\n' "${!presets[@]}" | sort); do
      theme_name="${key^^}_${prefix}"
      variables_string+="\n$s$s[$key]='${theme_name}'"
      variables_string2+="$s$d ${theme_name}=("
      for values in $(split "${presets[$key]}", '|'); do
          local -a pair=($(split "${values%,}" '='))
          local kval="${pair[0]}" vval="${pair[1]}"
          [[ $vval =~ ^[0-9]+$ ]] || vval="'$vval'"
          variables_string2+=" [$kval]=$vval"
      done
      variables_string2+=' )\n'
  done
  
  local maxlen=$(echo -e "$variables_string" | \
    awk '{if(length>max)max=length}END{print max}')
  local final_string
  
  final_string+="$shebang\n\n"
  final_string+="$(block $maxlen "$title")"
  final_string+="$variables_string\nfi\n$s)\n"
  final_string+="$variables_string2"
  final_string+="$(block $maxlen "END $title")"
  
  echo -e "$final_string" > "${func_name}.sh"
}

save_theme_variables_to_file "${1:-}"

# declare -p | grep "PRESET_THEME_
# echo "${PRESET_ABORT['icon']}"

# git clone --depth=1 https://github.com/romkatv/powerlevel10k.git ~/.zsh-themes/powerlevel10k
# echo 'source ~/.zsh-themes/powerlevel10k/powerlevel10k.zsh-theme' >>~/.zshrc








