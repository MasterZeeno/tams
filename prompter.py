def print_message(code, icon, message):
    print(f"\033[{code}m  {icon} {message}\033[0m")

def print_success(message):
    print_message(92, '', message)

def print_error(message):
    print_message(91, '', message)

def print_warning(message):
    print_message(93, '‼', message)
