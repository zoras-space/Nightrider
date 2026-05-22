import argparse
import json
import os
import sys

def count_file_contents(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            line_count = len(content.splitlines())
            word_count = len(content.split())
            char_count = len(content)
            return {
                "line_count": line_count,
                "word_count": word_count,
                "char_count": char_count
            }
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.", file=sys.stderr)
        sys.exit(1)
    except PermissionError:
        print(f"Error: Permission denied for file '{file_path}'.", file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Text Counter")
    parser.add_argument("file_path", type=str, help="Path to the UTF-8 text file")
    
    args = parser.parse_args()
    
    if not os.path.isfile(args.file_path):
        print(f"Error: '{args.file_path}' is not a valid file.", file=sys.stderr)
        sys.exit(1)
    
    try:
        result = count_file_contents(args.file_path)
        json_output = json.dumps(result)
        print(json_output)
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
