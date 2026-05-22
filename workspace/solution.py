import sys
import json

def parse_arguments(args):
    if len(args) != 3:
        raise ValueError("Invalid number of arguments")
    
    k1 = args[1]
    p1 = args[2]
    
    return k1, p1

def validate_input(k1, p1):
    if not isinstance(k1, str) or not isinstance(p1, str):
        raise TypeError("Both 'k1' and 'p1' must be strings")
    
    if not k1 and not p1:
        raise ValueError("At least one of 'k1' or 'p1' must be non-empty")

def main():
    try:
        k1, p1 = parse_arguments(sys.argv)
        validate_input(k1, p1)
        
        output = {
            "k1": k1,
            "p1": p1
        }
        
        print(json.dumps(output))
        sys.exit(0)
    
    except ValueError as e:
        sys.stderr.write(f"Error: {e}\n")
        sys.exit(1)
    
    except TypeError as e:
        sys.stderr.write(f"Error: {e}\n")
        sys.exit(2)

if __name__ == "__main__":
    main()
