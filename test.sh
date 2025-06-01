#!/data/data/com.termux/files/usr/bin/bash

PYSCRIPT=${1:-test3.py}

if [[ -f $PYSCRIPT && $PYSCRIPT =~ \.py$ ]]; then
    shift
    HAS_VENV=false
    WAKE_STATE=unlock
    PIP_OPTS=(
        -qqq
        --no-input
        --require-virtualenv
        --resume-retries 3
    )
    
    ESC="\033["
    RESET="${ESC}0m"
    INDENT="  "
    
    print() {
        local code=37
        local bold=1
    
        if (( $# > 1 )); then
            while (($#)); do
                case "$1" in
                    3[0-7]|9[0-7]) code=$1 ;;
                    true|false|0|1)
                        [[ $1 =~ ^(true|1)$ ]] && \
                            bold=1 || bold=0 ;;
                    *) break ;;
                esac
                shift
            done
        fi
    
        local fmt="${INDENT}${ESC}"
        (( bold )) && fmt+="1;"
        fmt+="${code}m"
    
        for arg in "$@"; do
            printf "%b%s%b\n" "$fmt" "$arg" "$RESET" >&2
        done
    }
    
    abort() {
        print 31 1 " Error: $*"
        exit 1
    }
    
    success() {
        print 32 1 " Success: $*"
    }
    
    cmd_exists() {
        command -v "$1" >/dev/null 2>&1 || \
            abort "Command [$1] not found"
    }
    
    exec_safely() {
        cmd_exists "$1" || return 1
        "$@" || abort "Failed to execute: $*"
    }
    
    resolve_venv() {
        local cfg=venv/pyvenv.cfg
        
        [[ -f "$cfg" ]] && grep -q "$PREFIX" "$cfg" && \
            HAS_VENV=true || HAS_VENV=false
            
        $HAS_VENV || exec_safely python3 -m venv venv
    }
   
    toggle_switches() {
        case $WAKE_STATE in
            un*) WAKE_STATE=lock ;;
            *) WAKE_STATE=unlock ;;
        esac
        
        exec_safely termux-wake-$WAKE_STATE
        $HAS_VENV || resolve_venv
        
        [[ -n $VIRTUAL_ENV ]] && \
            . ./venv/bin/activate || \
            exec_safely deactivate
    }
    
    clear
    toggle_switches
    trap toggle_switches EXIT INT TERM
    
    INSTALLED_PKGS=($(pip3 freeze))
    for pkg in requests selenium==4.9.1 beautifulsoup4; do
        if echo "${INSTALLED_PKGS[@]}" | grep -qF $pkg; then
            echo "Installing [${pkg%%=*}]..."
            exec_safely pip3 install -U $pkg ${PIP_OPTS[@]}
        fi
    done
    
    exec_safely python3 $PYSCRIPT "$@"
fi

