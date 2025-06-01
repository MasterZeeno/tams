from .printer import Printer

print_success = Printer(preset='success')
# print_error = Printer(preset='error')
# print_warning = Printer(preset='warning')

__all__ = [
    'print_success',
    # 'print_error',
    # 'print_warning'
]
