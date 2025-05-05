import sys
import shlex

def parse_cli_params():
    # Join all arguments into a single string (skip script name at sys.argv[0])
    # raw = ' '.join(sys.argv[1:])
    try:
        pairs = shlex.split(' '.join(sys.argv[1:]))
        return dict(pair.split('=', 1) for pair in pairs if '=' in pair)
    except ValueError as e:
        print(f"Error parsing parameters: {e}")
        return {}

# Example usage
if __name__ == '__main__':
    params = parse_cli_params()
    print(params["username"])
