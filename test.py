import argparse

def parse(args):
    params = {}
    for key, value in args.split("="):
        params[key.trim()] = value.trim()
        
    return params
        

def main():
    parser = argparse.ArgumentParser(description="TAMS Automater")
    parser.add_argument("params", nargs="*", help="List of key value parameter pairs.")
    
    params = parse(parser.parse_args())
    
    for key, value in vars(params).items():
        print(f"Key: {key}, Value: {value}")
    
    
if __name__ == "__main__":
    main()
