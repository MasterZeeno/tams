def print_msg(code: int, icon: str = "✔", msg: str = ""):
    color_range = 90
    spacer = "  "
    try:
        code = int(code)
    except (ValueError, TypeError):
        code = 2  # Default to success green
    # Clamp code to a safe range (0–7 for basic ANSI colors)
    code = max(0, min(code, 7))
    color_code = color_range + code  # Bright color range (90–97)
    print(f"\033[{color_code}m{spacer}{icon} {msg}\033[0m")

def print_error(msg: str):
    print_msg(1, "✖", msg)

def print_success(msg: str):
    print_msg(2, "✔", msg)

def print_warning(msg: str):
    print_msg(3, "⚠️", msg)